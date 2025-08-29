
# 🚀 NeuralVoice AI - Quick Setup Guide

## 📋 Prerequisites Checklist

- [ ] Python 3.11+ installed
- [ ] Modern web browser (Chrome, Firefox, Safari, Edge)
- [ ] Microphone access enabled
- [ ] Internet connection for AI services

## ⚡ Quick Start (5 Minutes)

### Step 1: Get Your API Keys

#### 🎯 AssemblyAI (Speech Recognition) - FREE
1. Go to [assemblyai.com](https://www.assemblyai.com/)
2. Sign up for free account
3. Copy your API key from dashboard
4. Free tier: 5 hours/month

#### 🧠 Google Gemini (AI Brain) - FREE
1. Visit [aistudio.google.com](https://aistudio.google.com/)
2. Create API key (Google account required)
3. Free tier: Generous usage limits

#### 🗣️ Murf AI (Voice Synthesis) - TRIAL
1. Sign up at [murf.ai](https://murf.ai/)
2. Get trial API key from dashboard
3. Trial includes premium voices

### Step 2: Environment Setup

Create `.env` file in project root:

```env
# Required API Keys
ASSEMBLYAI_API_KEY=your_assemblyai_key_here
GEMINI_API_KEY=your_gemini_key_here
MURF_API_KEY=your_murf_key_here

# Optional (has defaults)
FLASK_SECRET_KEY=your_random_secret_key
DATABASE_URL=sqlite:///neuralvoice.db
```

### Step 3: Install & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Start the application
python run.py
```

🎉 **That's it!** Open http://localhost:5000 in your browser.

## 🔧 Advanced Configuration

### Database Configuration
```env
# SQLite (default)
DATABASE_URL=sqlite:///neuralvoice.db

# PostgreSQL (production)
DATABASE_URL=postgresql://user:password@localhost/neuralvoice
```

### Security Configuration
```env
# Generate a secure secret key
FLASK_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex())')
```

### Development vs Production
```env
# Development
FLASK_ENV=development
FLASK_DEBUG=True

# Production
FLASK_ENV=production
FLASK_DEBUG=False
```

## 🎯 Testing Your Setup

### 1. Basic Functionality Test
- Click the voice orb to start recording
- Speak clearly for 3-5 seconds
- Click again to stop
- Wait for AI response

### 2. API Services Test
Run the error simulation script:
```bash
python simulate_errors.py
```

### 3. Browser Console Check
- Open browser developer tools (F12)
- Check console for any JavaScript errors
- Look for successful API responses

## 🚨 Troubleshooting

### Common Issues

#### ❌ "Microphone access required"
**Solution:** Enable microphone permissions in browser settings

#### ❌ "Speech recognition service not configured"
**Solution:** Check ASSEMBLYAI_API_KEY in .env file

#### ❌ "Gemini API not configured"
**Solution:** Verify GEMINI_API_KEY is correct and has quota

#### ❌ "Murf API not configured"
**Solution:** Ensure MURF_API_KEY is valid and has credits

### Advanced Debugging

#### Enable Verbose Logging
```python
# Add to run.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Check API Key Format
```bash
# AssemblyAI: Should start with letters/numbers
echo $ASSEMBLYAI_API_KEY

# Gemini: Should be an API key format
echo $GEMINI_API_KEY

# Murf: Check their documentation for format
echo $MURF_API_KEY
```

#### Database Issues
```bash
# Reset database
rm instance/neuralvoice.db
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

## 🌐 Deployment Options

### Option 1: Replit (Recommended)
1. Fork project on Replit
2. Add API keys to Secrets panel
3. Click Run button
4. Use Deploy tab for public hosting

### Option 2: Local Development
```bash
# Install production dependencies
pip install gunicorn

# Run production server
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Option 3: Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 📊 API Usage Monitoring

### Check Your Usage
- **AssemblyAI**: Visit dashboard for transcription hours
- **Gemini**: Check Google Cloud Console quotas
- **Murf**: Monitor credits in Murf dashboard

### Optimize Costs
- Enable auto-record toggle for continuous conversations
- Use shorter voice messages when possible
- Monitor error rates to avoid quota waste

## 🤝 Getting Help

### Resources
- 📖 [Complete README](README.md)
- 🐛 [Report Issues](https://github.com/yourusername/neuralvoice-ai/issues)
- 💡 [Feature Requests](https://github.com/yourusername/neuralvoice-ai/discussions)

### Community
- Share your experience with #NeuralVoiceAI
- Join our Discord community (coming soon)
- Follow development updates

---

**🎙️ Welcome to the future of voice AI!**

*Need help? The error messages in the app are designed to guide you to solutions.*
