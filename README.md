
# 🎙️ VoxAura AI - Complete Voice Conversational Agent

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1+-green.svg)](https://flask.palletsprojects.com)
[![AI-Powered](https://img.shields.io/badge/AI-Powered-purple.svg)](https://github.com)
[![Voice-Enabled](https://img.shields.io/badge/Voice-Enabled-orange.svg)](https://github.com)

> A sophisticated AI-powered voice conversational agent with ChatGPT-like interface, featuring real-time speech recognition, intelligent conversations, neural text-to-speech, document analysis, weather integration, and complete chat history management.

## 🚀 Key Features

### 🎯 Core Voice Capabilities
- **🎤 Real-time Voice Recording** - High-quality browser-based audio capture with WebSocket streaming
- **🧠 Advanced Speech Recognition** - Professional transcription using AssemblyAI with turn detection
- **🤖 Intelligent Conversations** - Context-aware responses powered by Google Gemini 2.0
- **🗣️ Neural Text-to-Speech** - Premium voice synthesis with Murf AI and gTTS fallback
- **🔄 Multi-Modal Input** - Seamless voice and text interactions
- **📡 Real-time Communication** - WebSocket-powered streaming for instant responses

### 🎨 Modern Interface Features
- **💬 ChatGPT-style Interface** - Familiar chat layout with message bubbles and modern design
- **📱 Fully Responsive Design** - Optimized for mobile, tablet, and desktop devices
- **📱 Mobile-Optimized UI** - Touch-friendly controls with proper scaling for smartphones
- **✨ Animated Star Background** - Interactive starfield with mouse-responsive movement and pulsing effects
- **🌊 Wave Processing Animation** - Beautiful wave effects during AI processing
- **🎛️ Interactive Voice Orb** - Animated circular voice interface with visual feedback
- **🔮 Glassmorphism Effects** - Modern translucent design with backdrop blur
- **🎭 Dynamic Personas** - Multiple AI personalities (Default, Pirate) with unique voices

### 📄 Document Intelligence
- **📁 PDF Processing** - Extract text, summarize, and analyze PDF documents
- **📝 Document Analysis** - Support for PDF, DOC, DOCX, and TXT files (up to 10MB)
- **🔍 Smart Queries** - Ask questions about uploaded documents
- **📊 Content Extraction** - Key points, concepts, and question generation
- **💡 AI-Powered Insights** - Intelligent document summarization and analysis
- **📋 Multi-Format Support** - Comprehensive document format compatibility

### 🌤️ Weather Integration
- **🌡️ Real-time Weather Data** - Current conditions and forecasts
- **🌍 Global Coverage** - Weather information for any city worldwide
- **📊 Detailed Forecasts** - Temperature, humidity, wind speed, and conditions
- **🔮 Smart Weather Queries** - Natural language weather requests
- **⚡ Multiple Weather APIs** - WeatherAPI and OpenWeatherMap integration
- **🌈 Weather Alerts** - Severe weather notifications and warnings

### 🗂️ Chat Management
- **💾 Persistent Chat History** - All conversations saved locally with full context
- **🔍 Advanced Search** - Find past conversations instantly with keyword search
- **➕ New Chat Sessions** - Start fresh conversations while preserving history
- **📋 Session Management** - Switch between multiple chat sessions seamlessly
- **💭 Smart Previews** - Quick preview of conversation topics in sidebar
- **📤 Export Functionality** - Export chat history in multiple formats

### 🛠️ Enhanced Configuration
- **⚙️ In-App API Configuration** - Complete API key management through settings dialog
- **🔗 Direct API Key Links** - Quick access to get API keys from all providers
- **🔄 Dynamic Service Switching** - Automatic fallback when services are unavailable
- **📊 Service Status Monitoring** - Real-time status of all connected services
- **🎨 UI Color Customization** - Custom scrollbars and theme matching
- **💡 Smart Notifications** - Context-aware alerts and status updates

### 🛠️ Technical Excellence
- **🏗️ Modular Architecture** - Clean separation of services with robust error handling
- **🔒 Secure API Management** - Dynamic configuration through encrypted settings panel
- **📊 Request Validation** - Pydantic models for API request/response validation
- **🔍 Comprehensive Logging** - Structured logging for debugging and monitoring
- **⚡ Performance Optimized** - Efficient audio processing and streaming
- **🌐 WebSocket Integration** - Real-time bidirectional communication
- **🔄 Auto-reconnection** - Intelligent WebSocket reconnection with status indicators

## 🔧 API Services Integration

### Primary AI Services
- **AssemblyAI** - Professional speech-to-text with real-time streaming
- **Google Gemini 2.0** - Advanced language model for intelligent conversations
- **Murf AI** - Premium neural text-to-speech synthesis
- **WeatherAPI** - Comprehensive weather information with forecasts and alerts
- **OpenWeatherMap** - Alternative weather service with global coverage

### Fallback Services
- **Google TTS (gTTS)** - Reliable text-to-speech fallback
- **DuckDuckGo Search** - Web search capabilities (no API key required)
- **Built-in PDF Processing** - Document analysis without external dependencies

## 📦 Quick Setup

### 1. Environment Setup
Create a `.env` file in the root directory:

```env
# Required API Keys
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
GEMINI_API_KEY=your_google_gemini_api_key_here
MURF_API_KEY=your_murf_ai_api_key_here

# Weather Services (Optional)
WEATHER_API_KEY=your_weather_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Additional AI Services (Optional)
GOOGLE_AI_API_KEY=your_google_ai_api_key_here

# Application Settings
FLASK_SECRET_KEY=your_secret_key_here
FLASK_ENV=development
FLASK_DEBUG=True
```

### 2. Installation & Run
```bash
# Clone and navigate to directory
git clone <your-repo-url>
cd voxaura-voice-agent

# Run the application (dependencies auto-install)
python main.py
```

The app will be available at `http://localhost:5000`

### 3. API Keys Setup (In-App Configuration)

VoxAura now features **in-app API configuration**! Click the **Settings** ⚙️ button in the sidebar to configure all your API keys through the beautiful settings dialog.

#### AssemblyAI (Speech Recognition)
1. Visit [AssemblyAI](https://www.assemblyai.com/) and create account
2. Get API key from dashboard
3. Add via Settings dialog or `.env` file

#### Google Gemini (AI Conversations)
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create API key
3. Add via Settings dialog or `.env` file

#### Murf AI (Premium Voice)
1. Sign up at [Murf AI](https://murf.ai/)
2. Get API credentials
3. Add via Settings dialog or `.env` file

#### Weather Services
1. **WeatherAPI**: Get free API key at [WeatherAPI](https://www.weatherapi.com/)
2. **OpenWeatherMap**: Alternative at [OpenWeatherMap](https://openweathermap.org/api)

## 🎯 How to Use

### Voice Conversations
1. **Click the microphone orb** to start recording
2. **Speak naturally** - the app detects when you stop talking
3. **Watch the animations** - stars pulse and waves flow during processing
4. **Listen to responses** - AI responds with natural voice synthesis
5. **View in chat** - All conversations appear in ChatGPT-style interface

### Text Conversations
1. **Type in the input box** at the bottom
2. **Press Enter** or click send button
3. **Get instant responses** with optional audio playback
4. **Use voice commands** by clicking the mic button next to input

### Document Analysis
1. **Click the attachment button** next to text input
2. **Upload PDF, DOC, DOCX, or TXT** files (max 10MB)
3. **Choose analysis type**: Summarize, Q&A, Key Points, Concepts
4. **Ask questions** about the document content
5. **Get AI insights** based on document analysis

### Weather Queries
1. **Ask natural weather questions**: "What's the weather in New York?"
2. **Get current conditions**: Temperature, humidity, wind speed
3. **Request forecasts**: "Will it rain tomorrow in London?"
4. **Global coverage**: Weather for any city worldwide
5. **Smart parsing**: Natural language weather requests

### Chat Management
1. **Open sidebar** by clicking the hamburger menu (☰)
2. **Start new chat** with the "+" button
3. **Browse chat history** - all past conversations saved
4. **Search conversations** using the search box
5. **Switch between chats** by clicking on history items

### Settings & Configuration
1. **Click settings icon** ⚙️ to open configuration panel
2. **Add API keys** with direct links to get them
3. **Configure all services** in one convenient dialog
4. **Choose AI personas** (Default, Pirate)
5. **Real-time status** of all connected services

## 📱 Mobile & Responsive Design

VoxAura is fully optimized for all devices:

### 📱 Smartphone Features
- **Touch-optimized controls** - Large, easy-to-tap buttons
- **Responsive sidebar** - Collapsible navigation for mobile screens
- **Optimized input areas** - Full-width text input with proper scaling
- **Mobile-friendly settings** - Easy-to-use configuration dialog
- **Voice-first design** - Perfect for hands-free mobile usage

### 📱 Tablet & iPad Support
- **Adaptive layout** - Optimal spacing for tablet screens
- **Touch gestures** - Intuitive touch interactions
- **Split-screen friendly** - Works great in multi-app environments

### 💻 Desktop Enhancement
- **Full-featured experience** - All features accessible
- **Keyboard shortcuts** - Efficient navigation and controls
- **Multi-window support** - Great for productivity workflows

## 🏗️ Project Architecture

```
voxaura-voice-agent/
├── 📁 services/                    # AI service integrations
│   ├── stt_service.py             # Speech-to-Text (AssemblyAI)
│   ├── llm_service.py             # Language Model (Gemini)
│   ├── tts_service.py             # Text-to-Speech (Murf + gTTS)
│   ├── pdf_service.py             # Document processing
│   ├── weather_service.py         # Weather integration
│   ├── websocket_service.py       # Real-time communication
│   └── web_search_service.py      # Search capabilities
├── 📁 static/                      # Frontend assets
│   ├── css/custom.css             # Responsive styling and animations
│   └── js/                        
│       ├── main.js                # Main application logic
│       ├── websocket-client.js    # WebSocket handling
│       └── streaming-audio.js     # Audio processing
├── 📁 templates/                   # HTML templates
│   └── index.html                 # Responsive main interface
├── 📁 schemas/                     # Data validation
├── main.py                        # Application entry point
├── requirements.txt               # Python dependencies
└── README.md                      # This documentation
```

## 🔍 Features Deep Dive

### Real-time Voice Processing Pipeline
```
Voice Input → WebSocket Stream → AssemblyAI STT → Gemini AI → Murf TTS → Audio Output
     ↑                                                                         ↓
Turn Detection ← Real-time Transcription → Context Management → Response Streaming
```

### Document Processing Workflow
```
File Upload → Text Extraction → Content Analysis → AI Processing → Formatted Response
     ↑                                                                    ↓
Validation ← Format Detection → Smart Chunking → Context Preservation → User Display
```

### Weather Integration Pipeline
```
Weather Query → Location Parsing → API Request → Data Processing → Natural Response
     ↑                                                                      ↓
NLP Processing ← Service Selection → Multi-API Fallback → Smart Formatting → Voice Output
```

### Chat History Management
```
User Message → Session Storage → Local Persistence → Search Indexing → Quick Retrieval
     ↑                                                                      ↓
Auto-save ← Context Maintenance → History Organization → Smart Previews → Sidebar Display
```

## 🎨 UI/UX Features

### Visual Effects
- **Animated Star Field**: 200+ stars with physics-based movement
- **Interactive Orb**: Pulsing voice control with gradient animations
- **Wave Processing**: Multi-colored wave animations during AI thinking
- **Glassmorphism**: Translucent elements with backdrop blur effects
- **Smooth Transitions**: CSS3 animations for all interactions
- **Custom Scrollbars**: Themed scrollbars matching UI colors

### Responsive Design
- **Mobile-Optimized**: Touch-friendly controls and responsive layout
- **Tablet Support**: Adaptive sidebar and optimized spacing
- **Desktop Enhanced**: Full-featured experience with keyboard shortcuts
- **Cross-Browser**: Tested on Chrome, Firefox, Safari, and Edge

### Accessibility
- **Keyboard Navigation**: Full keyboard accessibility support
- **Screen Reader Support**: ARIA labels and semantic HTML
- **High Contrast**: Readable color schemes and clear indicators
- **Error Handling**: Clear error messages and recovery options

## 🔧 Advanced Configuration

### Environment Variables
```env
# Core Services
ASSEMBLYAI_API_KEY=           # Speech recognition
GEMINI_API_KEY=              # AI conversations
MURF_API_KEY=                # Premium voice synthesis

# Weather Services
WEATHER_API_KEY=             # Primary weather service
OPENWEATHER_API_KEY=         # Alternative weather service

# Additional AI
GOOGLE_AI_API_KEY=           # Additional Google AI services

# Application Settings
FLASK_SECRET_KEY=            # Session security
FLASK_ENV=development        # Environment mode
FLASK_DEBUG=True             # Debug mode
MAX_CONTENT_LENGTH=16777216  # 16MB file upload limit
```

### In-App Configuration Panel
- **Dynamic Key Management**: Add/update API keys without restart
- **Service Status**: Real-time status of all connected services
- **Direct Links**: Quick access to get API keys from all providers
- **Fallback Configuration**: Automatic fallback when services unavailable
- **Usage Monitoring**: Track API usage and rate limits

## 🧪 Testing & Debugging

### Built-in Testing Tools
- **Component Testing**: Individual service testing interface
- **Error Simulation**: Test fallback scenarios and error handling
- **WebSocket Testing**: Real-time communication testing
- **Audio Processing**: Voice recording and playback testing

### Debugging Features
- **Comprehensive Logging**: Detailed logs for all operations
- **Error Analytics**: Structured error reporting
- **Performance Metrics**: Response times and success rates
- **Browser Console**: Client-side debugging information

## 🚀 Deployment on Replit

### Quick Deploy
1. **Fork this project** on Replit
2. **Set environment variables** in Secrets panel
3. **Click Run** to start the application
4. **Access via provided URL** for public sharing

### Production Configuration
```bash
# Auto-configures for production deployment
python main.py
```

### Environment Variables in Replit
Add these to your Replit Secrets:
- `ASSEMBLYAI_API_KEY`
- `GEMINI_API_KEY`
- `MURF_API_KEY`
- `WEATHER_API_KEY` (optional)
- `OPENWEATHER_API_KEY` (optional)
- `GOOGLE_AI_API_KEY` (optional)

## 📊 Recent Updates & New Features

### 🆕 Latest Enhancements (Day 29)
- **📱 Full Mobile Responsiveness** - Complete mobile optimization for all screen sizes
- **⚙️ In-App API Configuration** - Beautiful settings dialog with direct API key links
- **🌤️ Advanced Weather Integration** - Comprehensive weather queries with multiple API support
- **📄 Enhanced Document Processing** - Improved PDF analysis with better error handling
- **🎨 UI/UX Improvements** - Custom scrollbars, better animations, mobile-friendly design
- **🔄 Auto-reconnection Logic** - Smart WebSocket reconnection with visual status indicators
- **🔍 Enhanced Search** - Better chat history search with real-time filtering
- **📊 Service Monitoring** - Real-time status of all connected AI services

### 🎯 Performance Optimizations
- **⚡ Faster Response Times** - Optimized API calls and caching
- **📱 Mobile Performance** - Optimized for slower mobile connections
- **🔄 Better Error Handling** - Graceful fallbacks and user feedback
- **💾 Efficient Storage** - Optimized chat history management

## 🤝 Contributing

### Development Guidelines
1. **Fork the repository** and create feature branch
2. **Follow modular architecture** patterns
3. **Add comprehensive error handling** and logging
4. **Update schemas** for new API endpoints
5. **Test with error simulation** tools
6. **Document new features** in README

### Code Structure
- **Services**: Isolated, testable service modules
- **Schemas**: Pydantic models for validation
- **Error Handling**: Graceful fallbacks and user feedback
- **Logging**: Structured logging for debugging

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **AssemblyAI** - Professional speech recognition services
- **Google** - Powerful Gemini language model
- **Murf AI** - High-quality text-to-speech synthesis
- **WeatherAPI** - Comprehensive weather data services
- **Bootstrap** - Responsive UI framework
- **Font Awesome** - Beautiful icon library
- **WebSocket** - Real-time communication protocol

## 📞 Support & Troubleshooting

### Common Issues
1. **API Key Errors**: Configure keys in settings panel or `.env` file
2. **Microphone Access**: Ensure browser permissions for microphone
3. **WebSocket Connection**: Check firewall and proxy settings
4. **Audio Playback**: Verify browser audio permissions and settings
5. **Mobile Issues**: Ensure latest browser version for optimal experience

### Getting Help
- **Check browser console** for JavaScript errors
- **Review application logs** for service errors
- **Test individual components** using built-in testing tools
- **Verify API key configuration** in settings panel

---

**Built with ❤️ using cutting-edge AI technologies and modern web development practices**

*VoxAura AI - Where conversations meet the future*

**Features Checklist:**
✅ Real-time Voice Conversations  
✅ ChatGPT-style Interface  
✅ Document Analysis (PDF/DOC/TXT)  
✅ Advanced Weather Integration  
✅ Chat History & Search  
✅ Multiple AI Personas  
✅ WebSocket Streaming  
✅ Animated UI Effects  
✅ Full Mobile Responsiveness  
✅ In-App API Configuration  
✅ Error Handling & Fallbacks  
✅ Service Status Monitoring  
✅ Multi-Device Optimization  

*Ready to deploy on Replit with one click!*

## 🌐 Live Demo

**Deployed on Render**: [https://threeo-days-of-voice-agents-with-murf.onrender.com/](https://threeo-days-of-voice-agents-with-murf.onrender.com/)

*Experience VoxAura AI in action with full voice capabilities, document processing, weather integration, and mobile-optimized interface!*
