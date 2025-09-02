
**Whisper Class - AI Video Tutor Platform**

Access the AI Tuto by clicking the link below

URL:https://53c82044-278c-44c7-b436-be9edcf31e0a-00-15bo4fvx921cj.janeway.replit.dev/


**Collaborators**

1. Kibiwott Kamoo: Full-Stack Developer & AI Integration Lead

2. Godrick Mlewa: Frontend Developer & UX Designer Lead

3. Fabian kipyegon rono: Frontend Developer & Pitch Lead



**Overview**
Whisper Class is an AI-powered educational platform that transforms any uploaded or linked educational video into a private tutor. The application generates comprehensive summaries, interactive quizzes, flashcards, and provides a chat assistant that answers questions based on the video content. Built with Flask backend and vanilla HTML/CSS/JS frontend, it integrates with OpenAI's APIs for transcription and content generation, with Supabase PostgreSQL for data persistence.

In Summary, It generates:
- ✅ Video Transcripts (via Whisper)
- ✅ Intelligent Summaries
- ✅ Interactive Quizzes
- ✅ Flashcards
- ✅ AI Chat Assistant for Q&A

Tailored for students with ADHD and diverse learning needs, Whisper Class helps learners engage more deeply with educational video content.

**User Preferences**

Preferred communication style: Simple, everyday language.

**Project Architecture**

**Backend Architecture**

Framework: Flask with CORS support for cross-origin requests
Database: Supabase PostgreSQL with SQLAlchemy ORM
API Integration: OpenAI GPT-5 for content generation and Whisper for transcription
File Handling: Video upload support (MP4, AVI, MOV, WMV, FLV, WebM) and YouTube URL processing
Data Models: Videos, Quizzes, and Flashcards with relational structure

**Frontend Architecture**

Technology: Vanilla HTML5, CSS3, and JavaScript
Design: Responsive mobile-first design with gradient backgrounds and modern UI
Navigation: Tab-based interface with Upload, Library, and Study sections
Components: Interactive quiz system, flip-card flashcards, and real-time chat interface

**AI Processing Pipeline**

Video Ingestion: File upload or YouTube URL download via youtube-dl
Audio Extraction: MoviePy integration for extracting audio from video files
Transcription: OpenAI Whisper API for speech-to-text conversion
Content Generation: GPT-5 powered summary, quiz, and flashcard creation
Chat Assistant: Context-aware Q&A using video transcript as knowledge base

**Database Schema**

Videos Table: Stores video metadata, transcripts, summaries, and processing status
Quizzes Table: JSON-formatted multiple-choice questions with explanations
Flashcards Table: JSON-formatted front/back card pairs for spaced repetition
Relationships: One-to-one relationships between videos and their study materials

_Core Features_

**Video Processing**

Upload Support: Drag-and-drop file upload with progress tracking
YouTube Integration: Direct URL processing with automatic download
AI Transcription: Automatic speech-to-text using OpenAI Whisper
Content Analysis: Intelligent summary generation highlighting key learning points

**Study Materials Generation**

Smart Summaries: Comprehensive overviews focusing on educational content
Interactive Quizzes: 5 multiple-choice questions with explanations and scoring
Flashcards: 8 key concept cards with term/definition pairs
Adaptive Content: AI-generated materials tailored to video content type

**Learning Interface**

Study Modes: Summary review, quiz taking, flashcard practice, and AI chat
Progress Tracking: Quiz scoring and completion status
Interactive Elements: Clickable quiz options, flip animations for flashcards
Mobile Optimization: Touch-friendly interface with responsive design

**AI Chat Assistant**

Context-Aware: Uses video transcript to provide relevant answers
Educational Focus: Tutor-style responses that promote understanding
Real-Time: Instant responses with typing indicators
Conversation History: Persistent chat sessions during study periods

_External Dependencies_

**Core Backend**

Flask: Web application framework with routing and request handling
SQLAlchemy: ORM for database operations and model definitions
OpenAI: GPT-5 and Whisper API integration for AI features
MoviePy: Video processing and audio extraction capabilities
youtube-dl: YouTube video downloading and metadata extraction


**Frontend Libraries******

Font Awesome: Icon library for consistent UI elements
CSS3 Animations: Custom transitions and hover effects
Vanilla JavaScript: No framework dependencies for lightweight performance

**Project Structure**

whisper-class/
├── app.py                  # Main Flask application
├── templates/              # HTML templates
├── static/                 # CSS and JS files
├── utils/                  # Helper functions (transcription, AI, etc.)
├── .streamlit/             # Streamlit configs (if used later)
├── requirements.txt        # Python dependencies
├── README.md               # Project info
└── .env                    # Environment variables (not committed)


**Development Tools**

Flask-CORS: Cross-origin resource sharing for API access
python-dotenv: Environment variable management
psycopg2-binary: PostgreSQL database adapter

**Production Considerations**
Environment Variables: Secure API key and database URL management
Error Handling: Comprehensive try-catch blocks with user-friendly messages
File Management: Temporary file cleanup and storage optimization
Rate Limiting: Considerations for OpenAI API usage limits


**Contact**

Have questions or suggestions? Reach us at:

Email: kibiwottkamoo@gmail.com

bit202432699@mylife.mku.ac.ke, funwell113@gmail.

