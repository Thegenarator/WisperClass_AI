import os
import json
import tempfile
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from openai import OpenAI
import youtube_dl
try:
    from moviepy.editor import VideoFileClip
except ImportError:
    VideoFileClip = None
import requests
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Configure OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Database setup
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Database Models
class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    url = Column(String)
    transcript = Column(Text)
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)

class Quiz(Base):
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, index=True)
    questions = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

class Flashcard(Base):
    __tablename__ = "flashcards"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, index=True)
    cards = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def extract_audio_from_video(video_path):
    """Extract audio from video file"""
    if VideoFileClip is None:
        print("MoviePy not available, skipping audio extraction")
        return None
        
    try:
        video = VideoFileClip(video_path)
        audio_path = video_path.replace('.mp4', '.wav').replace('.avi', '.wav').replace('.mov', '.wav')
        video.audio.write_audiofile(audio_path, verbose=False, logger=None)
        video.close()
        return audio_path
    except Exception as e:
        print(f"Error extracting audio: {e}")
        return None

def transcribe_audio(audio_path):
    """Transcribe audio using OpenAI Whisper"""
    try:
        with open(audio_path, 'rb') as audio_file:
            # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
            # do not change this unless explicitly requested by the user
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        return transcript.text if hasattr(transcript, 'text') else str(transcript)
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return None

def generate_summary(transcript):
    """Generate summary using OpenAI"""
    try:
        response = client.chat.completions.create(
            model="gpt-5",  # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
            messages=[
                {"role": "system", "content": "You are an educational assistant. Create a comprehensive summary of the following video transcript that highlights key learning points, main concepts, and important details."},
                {"role": "user", "content": f"Please summarize this educational content:\n\n{transcript}"}
            ],
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating summary: {e}")
        return None

def generate_quiz(transcript):
    """Generate quiz questions using OpenAI"""
    try:
        response = client.chat.completions.create(
            model="gpt-5",  # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
            messages=[
                {"role": "system", "content": "You are an educational assistant. Create 5 multiple-choice quiz questions based on the video content. Return the response as JSON with this format: {\"questions\": [{\"question\": \"...\", \"options\": [\"A\", \"B\", \"C\", \"D\"], \"correct\": 0, \"explanation\": \"...\"}]}"},
                {"role": "user", "content": f"Create quiz questions for this content:\n\n{transcript}"}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error generating quiz: {e}")
        return None

def generate_flashcards(transcript):
    """Generate flashcards using OpenAI"""
    try:
        response = client.chat.completions.create(
            model="gpt-5",  # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
            messages=[
                {"role": "system", "content": "You are an educational assistant. Create 8 flashcards with key terms, concepts, and facts from the video content. Return as JSON: {\"cards\": [{\"front\": \"term/question\", \"back\": \"definition/answer\"}]}"},
                {"role": "user", "content": f"Create flashcards for this content:\n\n{transcript}"}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error generating flashcards: {e}")
        return None

def download_youtube_video(url):
    """Download YouTube video and return file path"""
    try:
        ydl_opts = {
            'format': 'best[height<=720]',
            'outtmpl': f'{UPLOAD_FOLDER}/%(title)s.%(ext)s',
        }
        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename, info.get('title', 'Unknown Video')
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_video():
    """Handle video upload"""
    db = get_db()
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Create video entry in database
            video = Video(title=filename, url=filepath)
            db.add(video)
            db.commit()
            db.refresh(video)
            
            return jsonify({
                'success': True,
                'video_id': video.id,
                'message': 'Video uploaded successfully'
            })
        
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/process-url', methods=['POST'])
def process_url():
    """Process YouTube URL"""
    db = get_db()
    
    try:
        data = request.get_json()
        url = data.get('url') if data else None
        
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        # Download video
        filepath, title = download_youtube_video(url)
        if not filepath:
            return jsonify({'error': 'Failed to download video'}), 400
        
        # Create video entry
        video = Video(title=title, url=url)
        db.add(video)
        db.commit()
        db.refresh(video)
        
        return jsonify({
            'success': True,
            'video_id': video.id,
            'title': title,
            'message': 'Video processed successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/process/<int:video_id>', methods=['POST'])
def process_video(video_id):
    """Process video to generate transcript, summary, quiz, and flashcards"""
    db = get_db()
    
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        
        # Extract audio from video
        video_path = video.url if video.url.startswith(UPLOAD_FOLDER) else video.url
        audio_path = extract_audio_from_video(video_path)
        
        if not audio_path:
            return jsonify({'error': 'Failed to extract audio'}), 500
        
        # Transcribe audio
        transcript = transcribe_audio(audio_path)
        if not transcript:
            return jsonify({'error': 'Failed to transcribe audio'}), 500
        
        # Generate summary
        summary = generate_summary(transcript)
        
        # Update video with transcript and summary
        video.transcript = transcript
        video.summary = summary
        video.processed = True
        
        # Generate quiz
        quiz_data = generate_quiz(transcript)
        if quiz_data:
            quiz = Quiz(video_id=video_id, questions=json.dumps(quiz_data))
            db.add(quiz)
        
        # Generate flashcards
        flashcard_data = generate_flashcards(transcript)
        if flashcard_data:
            flashcards = Flashcard(video_id=video_id, cards=json.dumps(flashcard_data))
            db.add(flashcards)
        
        db.commit()
        
        # Clean up audio file
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        return jsonify({
            'success': True,
            'transcript': transcript,
            'summary': summary,
            'quiz': quiz_data,
            'flashcards': flashcard_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat with AI about video content"""
    db = get_db()
    
    try:
        data = request.get_json()
        video_id = data.get('video_id')
        message = data.get('message')
        
        if not video_id or not message:
            return jsonify({'error': 'Video ID and message required'}), 400
        
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video or not video.transcript:
            return jsonify({'error': 'Video not found or not processed'}), 404
        
        # Generate response using video transcript as context
        response = client.chat.completions.create(
            model="gpt-5",  # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
            messages=[
                {"role": "system", "content": f"You are an AI tutor helping students understand video content. Use this transcript as context to answer questions: {str(video.transcript)[:3000]}..."},
                {"role": "user", "content": message}
            ],
            max_tokens=500
        )
        
        return jsonify({
            'response': response.choices[0].message.content
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/videos')
def get_videos():
    """Get all processed videos"""
    db = get_db()
    
    try:
        videos = db.query(Video).filter(Video.processed == True).all()
        return jsonify([{
            'id': v.id,
            'title': v.title,
            'created_at': v.created_at.isoformat(),
            'summary': str(v.summary)[:200] + '...' if v.summary and len(str(v.summary)) > 200 else str(v.summary) if v.summary else ''
        } for v in videos])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/video/<int:video_id>')
def get_video(video_id):
    """Get specific video details"""
    db = get_db()
    
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        
        quiz = db.query(Quiz).filter(Quiz.video_id == video_id).first()
        flashcards = db.query(Flashcard).filter(Flashcard.video_id == video_id).first()
        
        return jsonify({
            'id': video.id,
            'title': video.title,
            'summary': str(video.summary) if video.summary else '',
            'transcript': str(video.transcript) if video.transcript else '',
            'quiz': json.loads(str(quiz.questions)) if quiz and quiz.questions else None,
            'flashcards': json.loads(str(flashcards.cards)) if flashcards and flashcards.cards else None
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)