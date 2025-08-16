"""
TTS Audio Generation Service
This service provides a /generate-audio endpoint that converts text to speech.
Runs on port 8000 to work with the TTS client application.
"""

import os
import tempfile
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from werkzeug.middleware.proxy_fix import ProxyFix
import hashlib
import uuid

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
tts_app = Flask(__name__)
tts_app.secret_key = os.environ.get("SESSION_SECRET", "tts-service-secret")
tts_app.wsgi_app = ProxyFix(tts_app.wsgi_app, x_proto=1, x_host=1)

# Store for generated audio files (in production, use a proper storage solution)
generated_files = {}

@tts_app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'TTS Audio Generation',
        'timestamp': datetime.utcnow().isoformat()
    })

@tts_app.route('/generate-audio', methods=['POST'])
def generate_audio():
    """
    Generate audio from text input
    Expected input: {"text": "text to convert"}
    Returns: {"audio_url": "url_to_audio_file", "success": true}
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        text = data.get('text', '').strip()
        if not text:
            return jsonify({'error': 'Text field is required'}), 400
        
        if len(text) > 1000:
            return jsonify({'error': 'Text too long. Maximum 1000 characters allowed.'}), 400
        
        tts_app.logger.info(f"Generating audio for text: {text[:50]}...")
        
        # Generate a unique filename based on text content
        text_hash = hashlib.md5(text.encode()).hexdigest()
        filename = f"tts-{text_hash}-{uuid.uuid4().hex[:8]}.mp3"
        
        # For now, we'll create a placeholder audio file
        # In a real implementation, you would use a TTS library like:
        # - gTTS (Google Text-to-Speech)
        # - pyttsx3 (offline TTS)
        # - Azure Cognitive Services Speech
        # - AWS Polly
        # - OpenAI TTS API
        
        audio_url = generate_placeholder_audio(text, filename)
        
        # Store the file info for cleanup later
        generated_files[filename] = {
            'text': text,
            'created_at': datetime.utcnow(),
            'url': audio_url
        }
        
        return jsonify({
            'audio_url': audio_url,
            'success': True,
            'text': text,
            'filename': filename,
            'message': 'Audio generated successfully'
        })
        
    except Exception as e:
        tts_app.logger.error(f"Error generating audio: {str(e)}")
        return jsonify({
            'error': f'Audio generation failed: {str(e)}',
            'success': False
        }), 500

def generate_placeholder_audio(text, filename):
    """
    Generate a placeholder audio file URL
    In a real implementation, this would use an actual TTS service
    """
    # For demonstration, we return a URL that would contain the audio
    # In practice, you would:
    # 1. Use a TTS service to generate actual audio
    # 2. Save the audio file to storage
    # 3. Return the URL to access the file
    
    # Return a placeholder URL that indicates this is a demo
    return f"http://localhost:8000/audio/{filename}"

@tts_app.route('/audio/<filename>', methods=['GET'])
def serve_audio(filename):
    """
    Serve generated audio files
    In a real implementation, this would serve actual audio files
    """
    if filename not in generated_files:
        return jsonify({'error': 'Audio file not found'}), 404
    
    # For demonstration purposes, return info about the "audio file"
    file_info = generated_files[filename]
    
    return jsonify({
        'message': 'This is a placeholder for actual audio file',
        'filename': filename,
        'text': file_info['text'],
        'created_at': file_info['created_at'].isoformat(),
        'note': 'In a real implementation, this would stream the actual audio file'
    })

@tts_app.route('/files', methods=['GET'])
def list_files():
    """List all generated audio files"""
    return jsonify({
        'files': list(generated_files.keys()),
        'count': len(generated_files),
        'note': 'These are placeholder files for demonstration'
    })

if __name__ == '__main__':
    print("Starting TTS Audio Generation Service...")
    print("Service will be available at: http://localhost:8000")
    print("Health check: http://localhost:8000/health")
    print("Generate audio: POST http://localhost:8000/generate-audio")
    
    tts_app.run(
        host='0.0.0.0',
        port=8000,
        debug=True
    )