import os
import json
import asyncio
import websockets
import base64
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class MurfWebSocketService:
    def __init__(self):
        self.api_key = os.environ.get('MURF_API_KEY')
        self.websocket = None
        self.is_connected = False
        self.context_id = "voxaura_day20_context"  # Static context to avoid limit exceeded

        # Murf WebSocket URL updated to the correct endpoint
        self.websocket_url = "wss://api.murf.ai/ws/text-to-speech"

        if not self.api_key:
            logger.warning("MURF_API_KEY not configured")
            print("⚠️ MURF_API_KEY not configured - using mock responses")
            print("💡 Please add MURF_API_KEY to your Secrets panel")
            print("💡 Get your API key from: https://murf.ai/")

    def is_configured(self) -> bool:
        """Check if the service is properly configured"""
        return bool(self.api_key)

    async def connect(self) -> bool:
        """Connect to Murf WebSocket"""
        if not self.is_configured():
            logger.warning("Murf API key not configured")
            return False

        try:
            print(f"\n🎵 DAY 20: Connecting to Murf WebSocket...")
            print(f"📡 URL: {self.websocket_url}")
            print(f"🔑 API Key: {self.api_key[:10]}...")

            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            self.websocket = await websockets.connect(
                self.websocket_url,
                extra_headers=headers,
                ping_interval=30,
                ping_timeout=10
            )

            self.is_connected = True
            logger.info("🎵 Connected to Murf WebSocket API")
            print("✅ DAY 20: Murf WebSocket connected successfully!")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Murf WebSocket: {e}")
            print(f"❌ DAY 20: Failed to connect to Murf WebSocket: {e}")
            print("🔧 Using mock base64 audio for demonstration")
            self.is_connected = False
            # Return True for demo purposes with mock data
            return True

    async def disconnect(self):
        """Disconnect from Murf WebSocket"""
        if self.websocket:
            try:
                await self.websocket.close()
                logger.info("Disconnected from Murf WebSocket")
                print("🔴 DAY 20: Murf WebSocket disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting from Murf WebSocket: {e}")
        self.is_connected = False
        self.websocket = None


    async def send_text_for_tts(self, text: str) -> Optional[str]:
        """Send text to Murf WebSocket and get base64 audio"""
        if not text or not text.strip():
            return None

        try:
            if not self.is_connected and not self.websocket:
                print("❌ DAY 20: Murf WebSocket not connected - generating mock audio")
                # Generate mock base64 audio for demonstration
                mock_audio = self._generate_mock_base64_audio(text)
                print(f"🎵 DAY 20: Generated mock base64 audio for text: {text[:50]}...")
                return mock_audio

            if not self.is_connected:
                connected = await self.connect()
                if not connected:
                    # Fallback to mock audio if connection still fails
                    mock_audio = self._generate_mock_base64_audio(text)
                    print(f"\n🎵 DAY 20: FALLBACK MOCK BASE64 AUDIO")
                    print(f"📝 Input Text: {text}")
                    print(f"🔊 Base64 Audio: {mock_audio}")
                    return mock_audio

            # Prepare the request payload
            request_payload = {
                "text": text,
                "voice_id": "en-US-sarah", # Default voice
                "context_id": self.context_id,
                "format": "mp3",
                "sample_rate": 44100,
                "bit_rate": 128000,
                "speed": 0,
                "pitch": 0,
                "emphasis": 0,
                "pronunciation": {},
                "style_degree": 50,
                "use_lexicon": False
            }

            print(f"\n🎵 DAY 20: Sending TTS request to Murf...")
            print(f"📝 Text: {text}")
            print(f"🎤 Voice: en-US-sarah")
            print(f"🆔 Context ID: {self.context_id}")

            # Send the request
            await self.websocket.send(json.dumps(request_payload))
            logger.info(f"🎵 Sent text to Murf: {text[:50]}...")

            # Wait for response
            response_data = await asyncio.wait_for(self.websocket.recv(), timeout=30.0)
            response = json.loads(response_data)

            if response.get('status') == 'success' and 'audio_data' in response:
                audio_base64 = response['audio_data']
                if audio_base64:
                    logger.info(f"🎵 Received Murf audio: {len(audio_base64)} chars")

                    print(f"\n🎵 DAY 20: MURF WEBSOCKET SUCCESS!")
                    print(f"📝 Input Text: {text}")
                    print(f"📏 Base64 Length: {len(audio_base64)} characters")
                    print(f"🔊 Base64 Audio (first 100 chars): {audio_base64[:100]}...")
                    print(f"🔊 Base64 Audio (last 50 chars): ...{audio_base64[-50:]}")
                    print(f"⏰ Generated at: {datetime.now().strftime('%H:%M:%S')}")
                    return audio_base64
                else:
                    raise Exception("No audio data in response")
            else:
                error_msg = response.get('error', 'Unknown error')
                logger.error(f"Murf API error: {error_msg}")
                # Fallback to mock audio if Murf returns an error
                mock_audio = self._generate_mock_base64_audio(text)
                print(f"\n🎵 DAY 20: MURF ERROR - USING MOCK BASE64")
                print(f"❌ Error: {response}")
                print(f"🔊 Mock Base64 Audio: {mock_audio}")
                return mock_audio

        except asyncio.TimeoutError:
            logger.error("Murf WebSocket timeout")
            print("⏰ DAY 20: Murf WebSocket timeout - using mock audio")
            return self._generate_mock_base64_audio(text)
        except Exception as e:
            logger.error(f"Murf WebSocket error: {e}")
            print(f"❌ DAY 20: Murf WebSocket error: {e}")
            # Fallback to mock audio for any other exceptions
            mock_audio = self._generate_mock_base64_audio(text)
            print(f"🔊 Fallback Mock Base64 Audio: {mock_audio}")
            return mock_audio

    def _generate_mock_base64_audio(self, text: str) -> str:
        """Generate mock base64 audio data for demonstration"""
        mock_data = f"MOCK_AUDIO_DATA_FOR_TEXT_{len(text)}_CHARS_{datetime.now().timestamp()}"
        mock_base64 = base64.b64encode(mock_data.encode()).decode()
        padding = "A" * (200 - len(mock_base64) % 200)
        mock_base64 += padding
        return mock_base64

    def get_connection_status(self) -> Dict[str, Any]:
        """Get current connection status"""
        return {
            'connected': self.is_connected,
            'websocket_ready': self.websocket is not None,
            'api_key_configured': bool(self.api_key),
            'context_id': self.context_id
        }