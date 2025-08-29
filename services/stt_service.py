
"""
Speech-to-Text Service
Handles AssemblyAI integration with error handling and fallbacks
"""
import os
import logging
import tempfile
import assemblyai as aai
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class STTService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("ASSEMBLYAI_API_KEY")
        if self.api_key:
            aai.settings.api_key = self.api_key
        else:
            logger.warning("AssemblyAI API key not configured")
    
    def is_configured(self) -> bool:
        """Check if the service is properly configured"""
        return bool(self.api_key)
    
    def transcribe_audio(self, audio_file) -> Dict[str, Any]:
        """
        Transcribe audio file using AssemblyAI
        
        Args:
            audio_file: Audio file to transcribe
            
        Returns:
            Dict containing transcription result and metadata
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'STT service not configured',
                'fallback_message': 'Speech recognition is temporarily unavailable'
            }
        
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
                audio_file.save(temp_file.name)
                
                # Configure transcription
                config = aai.TranscriptionConfig(
                    speech_model=aai.SpeechModel.best,
                    language_code="en"
                )
                transcriber = aai.Transcriber(config=config)
                
                logger.info("Starting AssemblyAI transcription...")
                
                # Transcribe audio
                transcript = transcriber.transcribe(temp_file.name)
                
                # Clean up temp file
                os.unlink(temp_file.name)
                
                # Check transcription status
                if transcript.status == aai.TranscriptStatus.error:
                    logger.error(f"Transcription failed: {transcript.error}")
                    return {
                        'success': False,
                        'error': f'Transcription failed: {transcript.error}',
                        'fallback_message': 'Speech recognition failed. Please try speaking more clearly.'
                    }
                
                # Extract results
                transcription_text = transcript.text or "No speech detected"
                
                if not transcription_text or transcription_text == "No speech detected":
                    return {
                        'success': False,
                        'error': 'No speech detected',
                        'transcription': transcription_text,
                        'fallback_message': 'No speech detected. Please try speaking more clearly.'
                    }
                
                logger.info(f"Transcription successful: {len(transcription_text)} characters")
                
                return {
                    'success': True,
                    'transcription': transcription_text,
                    'confidence': getattr(transcript, 'confidence', None),
                    'audio_duration': getattr(transcript, 'audio_duration', None),
                    'word_count': len(transcription_text.split()) if transcription_text else 0
                }
                
        except Exception as e:
            logger.error(f"STT service error: {str(e)}")
            
            # Clean up temp file on error
            try:
                if 'temp_file' in locals():
                    os.unlink(temp_file.name)
            except:
                pass
            
            return {
                'success': False,
                'error': f'STT service error: {str(e)}',
                'fallback_message': 'Speech recognition service is temporarily unavailable.'
            }
