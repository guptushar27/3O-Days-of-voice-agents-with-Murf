
"""
Text-to-Speech Service
Handles Murf AI and gTTS fallback for voice synthesis
"""
import os
import logging
import hashlib
import uuid
from typing import Dict, Any, Optional
from gtts import gTTS
from murf import Murf
from flask import url_for

logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self, app):
        self.app = app
        self.murf_api_key = os.environ.get("MURF_API_KEY")
        if self.murf_api_key:
            self.murf_client = Murf(api_key=self.murf_api_key)
        else:
            self.murf_client = None
            logger.warning("Murf API key not configured")
    
    def is_murf_configured(self) -> bool:
        """Check if Murf service is configured"""
        return bool(self.murf_client)
    
    def generate_speech(self, text: str, voice_id: str = "en-US-natalie") -> Dict[str, Any]:
        """
        Generate speech from text using Murf AI with gTTS fallback
        
        Args:
            text: Text to convert to speech
            voice_id: Voice ID for Murf (default: en-US-natalie)
            
        Returns:
            Dict containing audio URL and metadata
        """
        if not text or not text.strip():
            return {
                'success': False,
                'error': 'No text provided for speech generation'
            }
        
        text = text.strip()
        
        # Try Murf first if configured
        if self.is_murf_configured():
            murf_result = self._generate_murf_speech(text, voice_id)
            if murf_result['success']:
                return murf_result
            
            logger.warning("Murf TTS failed, falling back to gTTS")
        
        # Fallback to gTTS
        return self._generate_gtts_speech(text)
    
    def _generate_murf_speech(self, text: str, voice_id: str) -> Dict[str, Any]:
        """Generate speech using Murf AI"""
        try:
            logger.info(f"Generating Murf speech: {len(text)} characters")
            
            response = self.murf_client.text_to_speech.generate(
                text=text,
                voice_id=voice_id,
                format="MP3",
                sample_rate=44100.0
            )
            
            # Extract audio URL
            audio_url = None
            if hasattr(response, 'audio_file'):
                audio_url = response.audio_file
            elif isinstance(response, dict):
                audio_url = response.get('audio_file') or response.get('url')
            
            if not audio_url:
                logger.error("No audio URL in Murf response")
                return {
                    'success': False,
                    'error': 'No audio URL received from Murf API'
                }
            
            logger.info("Murf speech generated successfully")
            
            return {
                'success': True,
                'audio_url': audio_url,
                'voice_used': voice_id,
                'service_used': 'murf',
                'character_count': len(text)
            }
            
        except Exception as e:
            logger.error(f"Murf TTS error: {str(e)}")
            return {
                'success': False,
                'error': f'Murf TTS error: {str(e)}'
            }
    
    def _generate_gtts_speech(self, text: str) -> Dict[str, Any]:
        """Generate speech using Google TTS fallback"""
        try:
            logger.info(f"Generating gTTS speech: {len(text)} characters")
            
            # Create unique filename
            text_hash = hashlib.md5(text.encode()).hexdigest()
            filename = f"gtts-{text_hash[:8]}-{uuid.uuid4().hex[:8]}.mp3"
            
            # Generate TTS
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Save to audio directory
            static_dir = os.path.join(self.app.instance_path, 'static', 'audio')
            os.makedirs(static_dir, exist_ok=True)
            
            audio_path = os.path.join(static_dir, filename)
            tts.save(audio_path)
            
            # Generate URL
            with self.app.app_context():
                audio_url = url_for('serve_audio_file', filename=filename, _external=True)
            
            logger.info("gTTS speech generated successfully")
            
            return {
                'success': True,
                'audio_url': audio_url,
                'voice_used': 'gTTS-english',
                'service_used': 'gtts',
                'character_count': len(text),
                'filename': filename
            }
            
        except Exception as e:
            logger.error(f"gTTS error: {str(e)}")
            return {
                'success': False,
                'error': f'gTTS error: {str(e)}'
            }
    
    def create_fallback_audio(self, message: str = "I'm having trouble connecting right now") -> str:
        """Create fallback audio for error cases"""
        try:
            result = self._generate_gtts_speech(message)
            if result['success']:
                return result['audio_url']
        except Exception as e:
            logger.error(f"Fallback audio generation failed: {str(e)}")
        
        # Return demo audio URL as last resort
        return "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmcfCjuO0y7RgTEGHW/A7+OZUSI="
