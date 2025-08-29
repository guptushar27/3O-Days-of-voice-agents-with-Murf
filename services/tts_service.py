import os
import logging
import hashlib
import uuid
from typing import Dict, Any, Optional
from gtts import gTTS
try:
    from murf import Murf
except ImportError:
    Murf = None
from flask import url_for
from datetime import datetime
import io

logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self, app=None, api_key=None):
        from flask import current_app

        self.app = app or current_app
        self.api_key = api_key or os.environ.get('MURF_API_KEY')

        if self.api_key and Murf:
            try:
                self.murf_client = Murf(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Murf client: {e}")
                self.murf_client = None
        else:
            self.murf_client = None
            if not Murf:
                logger.warning("Murf package not available")
            else:
                logger.warning("Murf API key not configured")

        if self.app:
            try:
                self.audio_dir = os.path.join(self.app.instance_path, 'static', 'audio')
                os.makedirs(self.audio_dir, exist_ok=True)
            except:
                self.audio_dir = os.path.join(os.getcwd(), 'static', 'audio')
                os.makedirs(self.audio_dir, exist_ok=True)
        else:
            self.audio_dir = os.path.join(os.getcwd(), 'static', 'audio')
            os.makedirs(self.audio_dir, exist_ok=True)

        self.persona_voices = {
            'default': {
                'voice': 'en-US-AriaNeural',
                'style': 'friendly',
                'pitch': '+0Hz',
                'rate': '+0%',
                'volume': '+0%'
            },
            'pirate': {
                'voice': 'en-US-DavisNeural',
                'style': 'authoritative',
                'pitch': '-15Hz',
                'rate': '-15%',
                'volume': '+10%'
            }
        }

    def is_murf_configured(self) -> bool:
        return bool(self.murf_client)

    def generate_speech(self, text: str, voice_id: str = "en-US-natalie", persona: str = "default") -> Dict[str, Any]:
        if not text or not text.strip():
            return {
                'success': False,
                'error': 'No text provided for speech generation'
            }

        text = text.strip()

        persona_config = {
            'pirate': {
                'voice_id': 'en-US-davis',
                'pitch_adjustment': -15,
                'speed_adjustment': -10,
                'style': 'gruff',
                'announce_change': "Arrr! Switching to me pirate voice now, matey!",
                'sound_effects': ['ocean_waves', 'ship_creaking']
            },
            'default': {
                'voice_id': 'en-US-sarah',
                'pitch_adjustment': 0,
                'speed_adjustment': 0,
                'style': 'friendly',
                'announce_change': "Switching back to my default voice.",
                'sound_effects': []
            }
        }

        config = persona_config.get(persona, persona_config['default'])
        voice_id = config['voice_id']

        if persona != 'default':
            logger.info(f"🎭 PERSONA VOICE CHANGE: {config['announce_change']}")
            print(f"🎭 {config['announce_change']}")

        logger.info(f"Using voice '{voice_id}' for persona '{persona}' with adjustments: pitch={config['pitch_adjustment']}%, speed={config['speed_adjustment']}%")

        if self.is_murf_configured():
            murf_result = self._generate_murf_speech_with_persona(text, voice_id, config)
            if murf_result['success']:
                return murf_result

            logger.warning("Murf TTS failed, falling back to gTTS")

        return self._generate_gtts_speech_with_persona(text, persona, config)

    def _generate_murf_speech_with_persona(self, text: str, voice_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.info(f"Generating Murf speech with persona: {len(text)} characters")

            base_pitch = 1.0
            base_speed = 1.0

            pitch_multiplier = base_pitch + (config['pitch_adjustment'] / 100.0)
            speed_multiplier = base_speed + (config['speed_adjustment'] / 100.0)

            logger.info(f"Applying voice modulation - Pitch: {pitch_multiplier:.2f}, Speed: {speed_multiplier:.2f}")

            murf_params = {
                'text': text,
                'voice_id': voice_id,
                'format': "MP3",
                'sample_rate': 44100.0
            }

            try:
                murf_params['pitch'] = pitch_multiplier
                murf_params['speed'] = speed_multiplier
                murf_params['style'] = config.get('style', 'default')
            except:
                logger.warning("Voice modulation parameters not supported by current Murf version")

            response = self.murf_client.text_to_speech.generate(**murf_params)

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

            logger.info("Murf speech with persona generated successfully")

            return {
                'success': True,
                'audio_url': audio_url,
                'voice_used': voice_id,
                'service_used': 'murf_persona',
                'character_count': len(text),
                'persona_config': config,
                'voice_modulation': {
                    'pitch': pitch_multiplier,
                    'speed': speed_multiplier,
                    'style': config.get('style')
                }
            }

        except Exception as e:
            logger.error(f"Murf TTS with persona error: {str(e)}")
            return {
                'success': False,
                'error': f'Murf TTS with persona error: {str(e)}'
            }

    def _generate_gtts_speech_with_persona(self, text: str, persona: str, config: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.info(f"Generating gTTS speech with persona '{persona}': {len(text)} characters")

            text_hash = hashlib.md5(text.encode()).hexdigest()
            filename = f"gtts-{persona}-{text_hash[:8]}-{uuid.uuid4().hex[:8]}.mp3"

            modified_text = self._apply_persona_text_effects(text, persona, config)

            slow_speech = config['speed_adjustment'] < -5
            tts = gTTS(text=modified_text, lang='en', slow=slow_speech)

            static_dir = os.path.join(self.app.instance_path, 'static', 'audio')
            os.makedirs(static_dir, exist_ok=True)

            audio_path = os.path.join(static_dir, filename)
            tts.save(audio_path)

            processed_audio_path = self._apply_voice_effects(audio_path, config)

            with self.app.app_context():
                final_filename = os.path.basename(processed_audio_path) if processed_audio_path else filename
                audio_url = url_for('serve_audio_file', filename=final_filename, _external=True, _scheme='https')

            logger.info(f"gTTS speech with persona '{persona}' generated successfully")

            return {
                'success': True,
                'audio_url': audio_url,
                'voice_used': f'gTTS-{persona}-enhanced',
                'service_used': 'gtts_persona',
                'character_count': len(text),
                'filename': final_filename if processed_audio_path else filename,
                'persona': persona,
                'persona_config': config,
                'voice_effects_applied': bool(processed_audio_path),
                'original_text': text,
                'modified_text': modified_text
            }

        except Exception as e:
            logger.error(f"gTTS with persona error: {str(e)}")
            return {
                'success': False,
                'error': f'gTTS with persona error: {str(e)}'
            }

    def _apply_persona_text_effects(self, text: str, persona: str, config: Dict[str, Any]) -> str:
        if persona == 'pirate':
            modified_text = text
            modified_text = modified_text.replace('.', '... ')
            modified_text = modified_text.replace(',', ', pause, ')

            pirate_words = ['arrr', 'matey', 'ahoy', 'ye', 'treasure', 'ship', 'sea', 'captain']
            for word in pirate_words:
                modified_text = modified_text.replace(word, f'{word.upper()}')
                modified_text = modified_text.replace(word.capitalize(), f'{word.upper()}')

            return modified_text

        return text

    def _apply_voice_effects(self, audio_path: str, config: Dict[str, Any]) -> str:
        try:
            effects = []
            if config['pitch_adjustment'] != 0:
                effects.append(f"pitch adjustment: {config['pitch_adjustment']}%")
            if config['speed_adjustment'] != 0:
                effects.append(f"speed adjustment: {config['speed_adjustment']}%")
            if config.get('style') != 'default':
                effects.append(f"style: {config['style']}")

            if effects:
                logger.info(f"Voice effects to apply: {', '.join(effects)}")
                print(f"🎵 Voice effects simulated: {', '.join(effects)}")

            return None

        except Exception as e:
            logger.warning(f"Voice effects processing failed: {str(e)}")
            return None

    def generate_audio(self, text: str) -> Dict[str, Any]:
        return self.generate_speech(text)

    def create_fallback_audio(self, message: str = "I'm having trouble connecting right now") -> str:
        try:
            result = self._generate_gtts_speech(message)
            if result['success']:
                return result['audio_url']
        except Exception as e:
            logger.error(f"Fallback audio generation failed: {str(e)}")

        return "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmcfCjuO0y7RgTEGHW/A7+OZUSI="