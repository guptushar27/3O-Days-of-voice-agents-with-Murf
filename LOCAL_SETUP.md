
# VoxAura AI - Local Development Setup

## Prerequisites

1. **Python 3.11+** installed on your system
2. **Git** for version control
3. **Code editor** (VS Code recommended)

## Setup Instructions

### 1. Clone or Download the Project

```bash
# If you have git
git clone <your-repo-url>
cd voxaura-ai

# Or download and extract the zip file
```

### 2. Install Python Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### 3. Environment Variables Setup

Create a `.env` file in the root directory:

```env
# Required API Keys
ASSEMBLYAI_API_KEY=your_assemblyai_key_here
GOOGLE_AI_API_KEY=your_gemini_api_key_here
MURF_API_KEY=your_murf_api_key_here

# Flask Configuration
SECRET_KEY=your_secret_key_here
FLASK_ENV=development
```

### 4. Get API Keys

1. **AssemblyAI**: Visit https://www.assemblyai.com/
   - Sign up for free account
   - Get API key from dashboard
   - Add to `.env` file

2. **Google Gemini**: Visit https://aistudio.google.com/
   - Create Google account if needed
   - Generate API key
   - Add to `.env` file

3. **Murf AI**: Visit https://murf.ai/
   - Sign up for account
   - Get API key from settings
   - Add to `.env` file

### 5. VS Code Setup (Recommended)

1. **Install VS Code Extensions**:
   - Python
   - Flask-Snippets
   - HTML CSS Support
   - JavaScript (ES6) code snippets

2. **VS Code Settings** (`.vscode/settings.json`):
```json
{
    "python.defaultInterpreterPath": "./bin/python",
    "python.terminal.activateEnvironment": true,
    "files.associations": {
        "*.html": "html"
    }
}
```

3. **Launch Configuration** (`.vscode/launch.json`):
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Flask App",
            "type": "python",
            "request": "launch",
            "program": "main.py",
            "env": {
                "FLASK_ENV": "development"
            },
            "console": "integratedTerminal"
        }
    ]
}
```

### 6. Run the Application

```bash
# Method 1: Direct Python
python main.py

# Method 2: Using Flask command
flask run --host=0.0.0.0 --port=5000 --debug

# Method 3: In VS Code
# Press F5 or use Run > Start Debugging
```

### 7. Access the Application

Open your browser and navigate to:
- **Local**: http://localhost:5000
- **Network**: http://0.0.0.0:5000

## File Structure

```
voxaura-ai/
├── main.py                 # Main Flask application
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (create this)
├── services/              # Core services
│   ├── llm_service.py     # Gemini AI integration
│   ├── stt_service.py     # AssemblyAI integration
│   ├── tts_service.py     # Murf AI + gTTS integration
│   └── websocket_service.py # WebSocket handling
├── templates/             # HTML templates
│   └── index.html         # Main UI
├── static/               # Static assets
│   ├── js/               # JavaScript files
│   │   └── main.js       # Main client-side logic
│   └── css/              # CSS files
└── instance/             # Generated files
    └── static/
        └── audio/        # Generated audio files
```

## Development Tips

### 1. Console Logging
The app provides comprehensive console logging for:
- **Day 17**: Speech-to-Text processing
- **Day 18**: Turn detection
- **Day 19**: Streaming LLM responses
- **Day 20**: TTS generation
- **Day 21**: Audio streaming
- **Day 22**: Seamless playback
- **Day 23**: Complete pipeline

### 2. Debugging
- Check browser console for client-side logs
- Check terminal/VS Code console for server-side logs
- Use browser developer tools for network requests

### 3. Common Issues

**HTTPS/Mixed Content**: 
- The app automatically converts HTTP URLs to HTTPS in production
- For local development, this shouldn't be an issue

**Microphone Access**:
- Ensure you allow microphone permissions in browser
- Use HTTPS or localhost for microphone access

**API Keys**:
- Verify all API keys are correctly set in `.env`
- Check API key validity and quotas

### 4. Testing Features

1. **Text Chat**: Type messages and press Enter
2. **Voice Chat**: Click microphone button and speak
3. **Audio Playback**: Generated responses have play/stop buttons
4. **Real-time Features**: All processing steps are logged to console

## Production Deployment

For production deployment, the app is designed to work on Replit with:
- Automatic HTTPS handling
- Environment variable management
- Static file serving
- WebSocket support

## Troubleshooting

### Port Issues
If port 5000 is busy:
```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 <PID>

# Or use different port
python main.py --port=5001
```

### Dependency Issues
```bash
# Clear pip cache
pip cache purge

# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### Audio Issues
- Ensure microphone permissions are granted
- Check browser compatibility (Chrome/Firefox recommended)
- Verify API keys are working

## Support

For issues or questions:
1. Check console logs first
2. Verify API key configuration
3. Test with simple text messages before voice
4. Ensure all dependencies are installed correctly
