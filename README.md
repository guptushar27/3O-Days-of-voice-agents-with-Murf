
# 🎙️ VoxAura - Advanced AI Voice Conversational Agent

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1+-green.svg)](https://flask.palletsprojects.com)
[![AI-Powered](https://img.shields.io/badge/AI-Powered-purple.svg)](https://github.com)
[![Voice-Enabled](https://img.shields.io/badge/Voice-Enabled-orange.svg)](https://github.com)

> A sophisticated AI-powered voice conversational agent that combines cutting-edge speech recognition, language modeling, and text-to-speech technologies into a seamless voice interaction experience.

![VoxAura AI Interface](screenshots/main-interface.png)

## 🚀 Features

### 🎯 Core Capabilities
- **🎤 Real-time Voice Recording** - High-quality browser-based audio capture
- **🧠 AI Speech Recognition** - Professional transcription using AssemblyAI
- **🤖 Intelligent Conversations** - Context-aware responses powered by Google Gemini
- **🗣️ Neural Text-to-Speech** - Premium voice synthesis with Murf AI
- **💾 Conversation Memory** - Persistent chat history and context retention
- **🔄 Multi-Modal Input** - Support for both voice and text interactions

### 🎨 Advanced UI Features
- **✨ Animated Star Background** - Interactive starfield with mouse-responsive movement
- **🌊 Wave Processing Animation** - Beautiful wave effects during AI processing
- **💬 ChatGPT-style Interface** - Modern chat layout with message bubbles
- **🎛️ Voice Orb Control** - Interactive circular voice interface with animations
- **📱 Responsive Design** - Optimized for all device sizes
- **🎭 Glassmorphism Effects** - Modern translucent design elements

### 🛠️ Technical Features
- **🏗️ Modular Architecture** - Clean separation of services and schemas
- **🔒 Robust Error Handling** - Graceful fallbacks when APIs are unavailable
- **📊 Request Validation** - Pydantic models for API request/response validation
- **🔍 Comprehensive Logging** - Structured logging for debugging and monitoring
- **⚡ Performance Optimized** - Efficient audio processing and response generation

## 🏗️ Project Structure

```
voxaura-voice-agent/
├── 📁 services/                    # Third-party service integrations
│   ├── __init__.py
│   ├── stt_service.py             # Speech-to-Text (AssemblyAI)
│   ├── llm_service.py             # Language Model (Google Gemini)
│   └── tts_service.py             # Text-to-Speech (Murf AI + gTTS)
├── 📁 schemas/                     # Pydantic models for validation
│   ├── __init__.py
│   ├── requests.py                # Request validation schemas
│   └── responses.py               # Response schemas
├── 📁 static/                      # Static assets
│   ├── 📁 css/
│   │   └── custom.css             # Custom styling and animations
│   └── 📁 js/
│       ├── tts.js                 # Text-to-speech functionality
│       └── echo-bot.js            # Voice recording and playback
├── 📁 templates/                   # HTML templates
│   ├── index.html                 # Main voice agent interface
│   └── test_llm.html              # Component testing interface
├── 📁 instance/                    # Runtime data
│   ├── 📁 static/audio/           # Generated audio files
│   ├── 📁 uploads/                # Uploaded audio recordings
│   └── tts_client.db              # SQLite database
├── app.py                         # Main Flask application
├── models.py                      # Database models
├── main.py                        # Application entry point
├── simulate_errors.py             # Error simulation for testing
└── README.md                      # This documentation
```

## 🧩 Architecture Overview

### Service Layer Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask API     │    │   Service Layer │
│                 │    │                 │    │                 │
│ • HTML5 Audio   │◄──►│ • Request Valid │◄──►│ • STT Service   │
│ • JavaScript    │    │ • Response      │    │ • LLM Service   │
│ • Animations    │    │   Formatting    │    │ • TTS Service   │
│ • Star Effects  │    │ • Error Handling│    │ • Fallbacks     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Voice Processing Pipeline
```
Voice Input → STT Service → LLM Service → TTS Service → Audio Output
     ↑                                                        ↓
 Validation ← Request/Response Schemas → Error Handling → Fallbacks
```

## 🛠️ Technology Stack

### Backend Technologies
- **Framework**: Flask 3.1+ with modular architecture
- **Database**: SQLAlchemy with SQLite (PostgreSQL ready)
- **Validation**: Pydantic models for request/response validation
- **Logging**: Structured logging with Python logging module

### AI Services Integration
- **AssemblyAI**: Professional speech-to-text recognition
- **Google Gemini**: Advanced language model for conversations
- **Murf AI**: Premium neural text-to-speech synthesis
- **gTTS**: Google Text-to-Speech (fallback)

### Frontend Technologies
- **UI Framework**: Bootstrap 5 with dark theme
- **JavaScript**: Vanilla ES6+ with modern async/await patterns
- **Audio**: HTML5 MediaRecorder API for voice capture
- **Animations**: CSS3 keyframes with interactive star field
- **Styling**: Custom CSS3 with glassmorphism and gradient effects

## 📦 Installation & Setup

### Prerequisites
- Python 3.11 or higher
- Modern web browser with microphone support
- API keys for AI services

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd voxaura-voice-agent
```

### 2. Install Dependencies
```bash
# Dependencies auto-install via pyproject.toml
python main.py
```

### 3. Environment Configuration
Create a `.env` file in the root directory:

```env
# Required API Keys
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
GEMINI_API_KEY=your_google_gemini_api_key_here
MURF_API_KEY=your_murf_ai_api_key_here

# Optional Configuration
FLASK_SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///tts_client.db

# Development Settings
FLASK_ENV=development
FLASK_DEBUG=True
```

### 4. API Keys Setup Guide

#### AssemblyAI (Speech Recognition)
1. Visit [AssemblyAI](https://www.assemblyai.com/)
2. Create a free account
3. Navigate to your dashboard and copy your API key
4. Add to `.env`: `ASSEMBLYAI_API_KEY=your_key_here`

#### Google Gemini (Language Model)
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key
3. Add to `.env`: `GEMINI_API_KEY=your_key_here`

#### Murf AI (Text-to-Speech)
1. Sign up at [Murf AI](https://murf.ai/)
2. Get your API credentials from the dashboard
3. Add to `.env`: `MURF_API_KEY=your_key_here`

### 5. Run the Application
```bash
python main.py
```

The application will be available at `http://localhost:5000`

### 6. Testing WebSocket Connection

#### Using the Built-in Test Panel
1. Look for the WebSocket test input at the bottom of the sidebar
2. Type a test message and click send
3. The server will echo back your message
4. Check the chat area for system messages showing the echo

#### Using External Tools (Postman, curl, etc.)
```bash
# Test WebSocket connection with wscat (install with: npm install -g wscat)
wscat -c ws://localhost:5000/socket.io/?EIO=4&transport=websocket

# Send a test message
{"type": "message", "data": "Hello WebSocket!"}
```

#### WebSocket Events Available
- `connect`: Establish connection
- `message`: Send/receive text messages  
- `chat_message`: Send chat messages with session info
- `audio_stream`: Send audio data for processing
- `echo_response`: Receive echoed messages
- `chat_response`: Receive AI chat responses

## 🎯 Usage Guide

### Enhanced Voice Conversation Mode
1. **Start Recording**: Click the animated voice orb or microphone button to begin recording
2. **Speak Clearly**: Talk naturally into your microphone
3. **Stop Recording**: Click the orb again to stop recording
4. **AI Processing**: Watch the enhanced horizontal wave animation and star heartbeat effects
5. **View Response**: See the conversation in the chat interface with enhanced controls
6. **Listen to Response**: Click the play button to hear the AI response
7. **Get Summaries**: Click the summary button for quick audio summaries of long responses

### WebSocket Real-time Communication
1. **Auto-Connect**: WebSocket connection established automatically
2. **Real-time Status**: See connection status in sidebar and header
3. **Test Messages**: Use the WebSocket test panel to send test messages
4. **Echo Responses**: Server echoes back messages for testing

### Enhanced Text Input Mode
1. Type your message in the text input at the bottom
2. Use the microphone button next to the input for voice messages
3. Enhanced audio controls appear with each AI response
4. Click summary buttons for condensed audio versions

### New Features
- **Star Heartbeat Animation**: Background stars pulse during AI processing
- **Horizontal Wave Processing**: Multi-colored wave animation during processing
- **Reduced Processing Time**: Faster AI responses for better user experience
- **Audio Controls**: Play and summary buttons for each message
- **WebSocket Integration**: Real-time bidirectional communication
- **Enhanced UI**: Larger interface with better responsive design
- **Connection Monitoring**: Real-time WebSocket connection statuse bottom
2. Press Enter or click the send button
3. View the AI response in the chat interface

### Chat Features
- **Session Management**: Each session maintains conversation context
- **Message History**: All messages are displayed in ChatGPT-style bubbles
- **Export Chat**: Download your conversation as a text file
- **Clear History**: Reset the conversation when needed
- **Auto-record**: Automatically start recording after AI responses

## 🔧 API Endpoints

### Voice Agent Endpoints
- `POST /agent/chat/<session_id>` - Process voice conversation
- `GET /agent/chat/<session_id>/history` - Get chat history
- `POST /agent/chat/<session_id>/clear` - Clear chat history

### Audio Processing Endpoints
- `POST /generate-tts` - Generate text-to-speech audio
- `POST /transcribe/file` - Transcribe audio to text
- `POST /upload-audio` - Upload audio files

### AI Service Endpoints
- `POST /llm/query` - Query language model directly
- `GET /audio/<filename>` - Serve generated audio files

## 🎨 UI/UX Features

### Modern Design Elements
- **Animated Star Field**: Interactive background with mouse-responsive movement
- **Wave Processing Animation**: Beautiful wave effects during AI processing
- **Glassmorphism Effects**: Translucent cards with backdrop blur
- **Gradient Animations**: Smooth color transitions and hover effects
- **Voice Orb Interface**: Interactive circular voice control with animations
- **ChatGPT-style Layout**: Modern conversation interface with message bubbles

### Accessibility Features
- **Keyboard Navigation**: Full keyboard accessibility support
- **Screen Reader Support**: ARIA labels and semantic HTML
- **Visual Indicators**: Clear status messages and error handling
- **Mobile Optimized**: Touch-friendly controls and responsive design

## 🔍 Error Handling & Fallbacks

### Service-Level Error Recovery
- **STT Service**: Graceful fallback messages when speech recognition fails
- **LLM Service**: Contextual fallback responses when AI services are unavailable
- **TTS Service**: Automatic fallback from Murf AI to gTTS
- **Network Issues**: Comprehensive error messages and retry mechanisms

### Monitoring & Logging
- **Structured Logging**: Comprehensive logging at service and endpoint levels
- **Request Validation**: Pydantic models ensure data integrity
- **Error Analytics**: Detailed error reporting and debugging information
- **Performance Metrics**: Response times and success rates tracked

## 🧪 Testing

### Error Simulation
Use the included error simulation script to test fallback scenarios:

```bash
python simulate_errors.py
```

This tool helps you test:
- AssemblyAI API failures
- Gemini LLM service issues
- Murf TTS unavailability
- Network connectivity problems

### Component Testing
Access `/test-llm` route for individual component testing:
- Speech transcription testing
- LLM query testing
- TTS generation testing

## 🚀 Deployment on Replit

### Quick Deploy
1. Fork this project on Replit
2. Set up environment variables in the Secrets panel:
   - `ASSEMBLYAI_API_KEY`
   - `GEMINI_API_KEY`
   - `MURF_API_KEY`
3. Click the "Run" button to start the application
4. Use Replit's deployment features for production

### Production Deployment
```bash
# The app auto-configures for production
python main.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Follow the modular architecture patterns
4. Add appropriate error handling and logging
5. Update schemas for new API endpoints
6. Test with the error simulation tools
7. Commit your changes: `git commit -m 'Add amazing feature'`
8. Push to the branch: `git push origin feature/amazing-feature`
9. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **AssemblyAI** for providing excellent speech recognition services
- **Google** for the powerful Gemini language model
- **Murf AI** for high-quality text-to-speech synthesis
- **Bootstrap** for the responsive UI framework
- **Font Awesome** for beautiful icons

## 📞 Support

If you encounter any issues:

1. Check the error simulation guide for testing fallback scenarios
2. Review service logs for detailed error information
3. Ensure all API keys are correctly configured
4. Check browser console for JavaScript errors

---

**Built with ❤️ using cutting-edge AI technologies and modern web development practices**

*VoxAura - Where conversations meet the future*
