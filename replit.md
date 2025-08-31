# Whisper Class - AI Video Tutor Platform

## Overview

Whisper Class is an AI-powered educational platform that transforms any uploaded or linked educational video into a private tutor. The application generates comprehensive summaries, interactive quizzes, flashcards, and provides a chat assistant that answers questions based on the video content. Built with Flask backend and vanilla HTML/CSS/JS frontend, it integrates with OpenAI's APIs for transcription and content generation, with Supabase PostgreSQL for data persistence.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

- **August 31, 2025**: Complete rebuild from Streamlit data analysis tool to Flask-based AI video tutor
- Implemented full-stack video processing pipeline with OpenAI integration
- Created responsive web interface with three main sections: Upload, Library, and Study
- Added real-time AI-powered content generation and chat functionality

## Project Architecture

### Backend Architecture
- **Framework**: Flask with CORS support for cross-origin requests
- **Database**: Supabase PostgreSQL with SQLAlchemy ORM
- **API Integration**: OpenAI GPT-5 for content generation and Whisper for transcription
- **File Handling**: Video upload support (MP4, AVI, MOV, WMV, FLV, WebM) and YouTube URL processing
- **Data Models**: Videos, Quizzes, and Flashcards with relational structure

### Frontend Architecture
- **Technology**: Vanilla HTML5, CSS3, and JavaScript
- **Design**: Responsive mobile-first design with gradient backgrounds and modern UI
- **Navigation**: Tab-based interface with Upload, Library, and Study sections
- **Components**: Interactive quiz system, flip-card flashcards, and real-time chat interface

### AI Processing Pipeline
- **Video Ingestion**: File upload or YouTube URL download via youtube-dl
- **Audio Extraction**: MoviePy integration for extracting audio from video files
- **Transcription**: OpenAI Whisper API for speech-to-text conversion
- **Content Generation**: GPT-5 powered summary, quiz, and flashcard creation
- **Chat Assistant**: Context-aware Q&A using video transcript as knowledge base

### Database Schema
- **Videos Table**: Stores video metadata, transcripts, summaries, and processing status
- **Quizzes Table**: JSON-formatted multiple-choice questions with explanations
- **Flashcards Table**: JSON-formatted front/back card pairs for spaced repetition
- **Relationships**: One-to-one relationships between videos and their study materials

## Core Features

### Video Processing
- **Upload Support**: Drag-and-drop file upload with progress tracking
- **YouTube Integration**: Direct URL processing with automatic download
- **AI Transcription**: Automatic speech-to-text using OpenAI Whisper
- **Content Analysis**: Intelligent summary generation highlighting key learning points

### Study Materials Generation
- **Smart Summaries**: Comprehensive overviews focusing on educational content
- **Interactive Quizzes**: 5 multiple-choice questions with explanations and scoring
- **Flashcards**: 8 key concept cards with term/definition pairs
- **Adaptive Content**: AI-generated materials tailored to video content type

### Learning Interface
- **Study Modes**: Summary review, quiz taking, flashcard practice, and AI chat
- **Progress Tracking**: Quiz scoring and completion status
- **Interactive Elements**: Clickable quiz options, flip animations for flashcards
- **Mobile Optimization**: Touch-friendly interface with responsive design

### AI Chat Assistant
- **Context-Aware**: Uses video transcript to provide relevant answers
- **Educational Focus**: Tutor-style responses that promote understanding
- **Real-Time**: Instant responses with typing indicators
- **Conversation History**: Persistent chat sessions during study periods

## External Dependencies

### Core Backend
- **Flask**: Web application framework with routing and request handling
- **SQLAlchemy**: ORM for database operations and model definitions
- **OpenAI**: GPT-5 and Whisper API integration for AI features
- **MoviePy**: Video processing and audio extraction capabilities
- **youtube-dl**: YouTube video downloading and metadata extraction

### Frontend Libraries
- **Font Awesome**: Icon library for consistent UI elements
- **CSS3 Animations**: Custom transitions and hover effects
- **Vanilla JavaScript**: No framework dependencies for lightweight performance

### Development Tools
- **Flask-CORS**: Cross-origin resource sharing for API access
- **python-dotenv**: Environment variable management
- **psycopg2-binary**: PostgreSQL database adapter

### Production Considerations
- **Environment Variables**: Secure API key and database URL management
- **Error Handling**: Comprehensive try-catch blocks with user-friendly messages
- **File Management**: Temporary file cleanup and storage optimization
- **Rate Limiting**: Considerations for OpenAI API usage limits