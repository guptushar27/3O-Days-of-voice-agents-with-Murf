# Overview

A Flask-based Text-to-Speech (TTS) web application that converts user-provided text into audio using Google Text-to-Speech (gTTS). The application features a clean, simplified UI with Bootstrap dark theme styling, real audio generation, playback controls, and request tracking for analytics. Users can input text through a web interface and generate actual MP3 audio files that can be played back immediately.

## Recent Changes
- **Day 9 Completion (Aug 10, 2025)**: Comprehensive Ancient Voice Oracle with ALL previous features integrated
- **Ancient-Modern UI Design**: Beautiful mystical theme with gold gradients, floating animations, and glassmorphism effects
- **Complete Feature Integration**: All 9 days of features now accessible through tabbed interface with ancient oracle theme
- **Full Voice Pipeline**: Voice → AssemblyAI Transcription → Gemini LLM → Murf TTS → Audio Response (Working)
- **Enhanced UI Features**: Mystical orbs, status indicators, ancient buttons with animations, shimmer effects
- **Multi-Mode Support**: Voice Oracle (Day 9), Text Wisdom (Day 8), Echo Bot v2 (Day 7), Basic TTS (Day 3), Transcription (Day 6)
- **Responsive Design**: Mobile-friendly ancient oracle interface with modern accessibility
- **Day 8 Completion (Aug 9, 2025)**: Added LLM Query endpoint with Google Gemini API integration
- **LLM Query Endpoint**: New `/llm/query` POST route that accepts text and returns Gemini AI responses
- **Google Gemini Integration**: Professional AI text generation using gemini-2.5-flash model with generous free tier
- **API Configuration**: Properly configured Gemini client with error handling and response validation
- **Day 7 Completion (Aug 8, 2025)**: Implemented Echo Bot v2 with Murf AI voice generation
- **Echo Bot v2 Features**: Records speech, transcribes with AssemblyAI, generates professional Murf voice, plays back in Natalie voice
- **API Integration**: Added Murf Python SDK for high-quality text-to-speech generation
- **Enhanced UI**: Updated interface to show "Echo Bot v2" with professional voice capabilities
- **Day 6 Completion (Aug 7, 2025)**: Added speech transcription functionality using AssemblyAI
- **Transcription Endpoint**: New `/transcribe/file` Flask route that converts speech to text using AssemblyAI API
- **Beautiful Transcription UI**: Real-time transcription display with word count, confidence scores, and copy functionality
- **AssemblyAI Integration**: Professional speech recognition service with high accuracy and detailed metadata
- **Day 5 Completion (Aug 6, 2025)**: Added server audio upload functionality with real-time status tracking
- **Audio Upload Endpoint**: New `/upload-audio` Flask route that receives and saves audio files to uploads folder
- **Upload Status UI**: Real-time upload progress indicators with success/error feedback
- **File Management**: Secure filename generation, file size reporting, and organized storage system
- **Day 4 Completion (Aug 5, 2025)**: Added Echo Bot functionality with voice recording and playback
- **UI Enhancement**: Transformed interface into "AI Voice Studio" with modern glassmorphism design
- **Echo Bot Integration**: Implemented MediaRecorder API for microphone recording and audio playback
- **Design Overhaul**: Added gradient backgrounds, animated elements, and professional card-based layout
- **Day 3 Completion (Aug 4, 2025)**: Integrated real TTS functionality using gTTS library
- **Audio Generation**: Implemented actual audio file creation and serving instead of placeholder content

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
The frontend uses a single-page application approach with vanilla JavaScript and Bootstrap for styling:
- **Template Engine**: Jinja2 templates with Flask for server-side rendering
- **Styling Framework**: Bootstrap 5 with dark theme and custom CSS overrides
- **JavaScript Architecture**: Class-based vanilla JavaScript (TTSClient and EchoBot) for handling user interactions
- **UI Components**: Form-based text input with character counting, audio player controls, transcription display, copy functionality, loading states, and error handling

## Backend Architecture
The backend follows a traditional Flask MVC pattern:
- **Web Framework**: Flask with SQLAlchemy ORM for database operations
- **Database Layer**: SQLAlchemy with declarative base model configuration
- **Request Handling**: RESTful API endpoints for TTS generation (`/generate-tts`) and speech transcription (`/transcribe/file`)
- **Configuration Management**: Environment variable-based configuration for database URLs, session secrets, and AssemblyAI API key
- **Middleware**: ProxyFix middleware for handling reverse proxy headers
- **AI Integration**: AssemblyAI speech-to-text service for professional transcription capabilities

## Data Storage
- **Primary Database**: SQLite for development with configurable database URL support
- **ORM**: SQLAlchemy with DeclarativeBase for model definitions
- **Connection Management**: Pool recycling and pre-ping enabled for connection health
- **Data Model**: TTSRequest model tracks text input, generated audio URLs, timestamps, success status, and error messages

## Request Lifecycle
- User submits text through the web form
- Flask validates input and processes TTS generation request
- Request details are logged to the database for analytics
- Generated audio URL is returned to the client for playback

# External Dependencies

## Core Framework Dependencies
- **Flask**: Web application framework with template rendering
- **SQLAlchemy**: ORM and database toolkit with Flask integration
- **Werkzeug**: WSGI utilities including ProxyFix middleware

## Frontend Dependencies
- **Bootstrap 5**: CSS framework with dark theme support
- **Font Awesome 6.4.0**: Icon library for UI elements
- **Bootstrap Agent Dark Theme**: Replit-specific Bootstrap theme

## AI Service Dependencies
- **AssemblyAI SDK**: Professional speech recognition API for audio transcription
- **Google Text-to-Speech (gTTS)**: Text-to-speech conversion library
- **Python Requests**: HTTP library for external API calls
- **Python Logging**: Built-in logging for debugging and monitoring

## Complete Feature Integration
All major features are now fully implemented:
- **Text-to-Speech**: Real audio generation using Google TTS
- **Voice Recording**: Browser-based audio recording with MediaRecorder API
- **Audio Upload**: Server-side file handling and storage
- **Speech Transcription**: AI-powered speech-to-text using AssemblyAI