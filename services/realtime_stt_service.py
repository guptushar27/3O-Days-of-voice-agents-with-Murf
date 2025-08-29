
"""
Real-time Speech-to-Text Service using AssemblyAI
Handles streaming audio transcription with turn detection
"""
import os
import logging
import base64
import json
import threading
import time
from datetime import datetime
from typing import Dict, Any, Callable, Optional
import assemblyai as aai
import websocket

logger = logging.getLogger(__name__)

class RealtimeSTTService:
    def __init__(self):
        self.api_key = os.environ.get("ASSEMBLYAI_API_KEY")
        if self.api_key and len(self.api_key.strip()) > 10:
            aai.settings.api_key = self.api_key
            logger.info("AssemblyAI API key configured successfully")
        else:
            logger.warning("AssemblyAI API key not configured or invalid")
            if self.api_key:
                logger.warning(f"API key length: {len(self.api_key)} (should be longer)")
            self.api_key = None

        # WebSocket and connection state
        self.ws = None
        self.ws_thread = None
        self.is_connected = False
        self.connection_error = None
        self.is_streaming = False

        # Callbacks
        self.transcription_callback = None
        self.turn_detection_callback = None

        # Session info
        self.session_info = {}

    def is_configured(self) -> bool:
        """Check if the service is properly configured"""
        return bool(self.api_key)

    def start_streaming_transcription(self, callback: Callable[[str], None], turn_callback: Optional[Callable[[Dict], None]] = None):
        """Start real-time transcription with turn detection"""
        if not self.is_configured():
            logger.error("AssemblyAI API key not configured")
            print("❌ AssemblyAI API key not configured")
            print("💡 Please add ASSEMBLYAI_API_KEY to your Secrets panel")
            print("💡 Get your API key from: https://www.assemblyai.com/")
            return False

        try:
            print("🚀 Starting AssemblyAI Real-time Transcription...")
            print("📋 Configuration: 16kHz, 16-bit, mono PCM audio")
            print("🎯 Features: Turn detection enabled")

            # Store callbacks
            self.transcription_callback = callback
            self.turn_detection_callback = turn_callback

            # Reset connection state
            self.is_connected = False
            self.connection_error = None

            # WebSocket URL for AssemblyAI real-time API with turn detection
            ws_url = f"wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000&token={self.api_key}"

            # Connect to AssemblyAI
            self.ws = websocket.WebSocketApp(
                ws_url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )

            # Start WebSocket in a separate thread
            self.ws_thread = threading.Thread(target=self.ws.run_forever)
            self.ws_thread.daemon = True
            self.ws_thread.start()

            # Wait for connection with timeout
            timeout = 10
            while timeout > 0 and not self.is_connected and not self.connection_error:
                time.sleep(0.1)
                timeout -= 0.1

            if self.connection_error:
                logger.error(f"Connection failed: {self.connection_error}")
                print(f"❌ Connection failed: {self.connection_error}")
                return False
            
            if not self.is_connected:
                logger.error("Connection timed out")
                print("❌ Connection timed out")
                return False

            self.is_streaming = True
            logger.info("✅ Started AssemblyAI real-time transcription with turn detection")
            print("✅ AssemblyAI connection established with turn detection")
            return True

        except Exception as e:
            logger.error(f"Failed to start streaming transcription: {str(e)}")
            print(f"❌ Failed to start transcription: {str(e)}")
            return False

    def send_audio_data(self, audio_data: bytes):
        """Send audio data to AssemblyAI for transcription"""
        if self.ws and self.is_streaming:
            try:
                # Encode audio data to base64 and send as JSON
                encoded_data = base64.b64encode(audio_data).decode('utf-8')
                message = json.dumps({"audio_data": encoded_data})
                self.ws.send(message)
            except Exception as e:
                logger.error(f"Error sending audio data: {str(e)}")
                print(f"❌ Error sending audio: {str(e)}")

    def stop_streaming_transcription(self):
        """Stop real-time transcription"""
        if self.ws:
            try:
                self.ws.close()
                logger.info("Attempted to close AssemblyAI WebSocket connection")
                print("🔴 Stopping AssemblyAI transcription...")
            except Exception as e:
                logger.error(f"Error closing WebSocket: {str(e)}")
                print(f"❌ Error stopping transcription: {str(e)}")
        
        self.is_streaming = False
        self.is_connected = False

    def _on_open(self, ws):
        """Handle WebSocket connection opened"""
        logger.info("WebSocket connection opened")
        print("\n✅ DAY 17 TRANSCRIPTION SESSION OPENED")
        print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
        print("🎤 Ready for audio input...")
        self.is_connected = True

    def _on_message(self, ws, message):
        """Handle incoming messages from AssemblyAI"""
        try:
            data = json.loads(message)
            
            # Handle different message types
            if data.get('message_type') == 'PartialTranscript':
                # Partial transcription (real-time)
                text = data.get('text', '').strip()
                if text and self.transcription_callback:
                    print(f"📝 PARTIAL: {text}")
                    self.transcription_callback(text)
                    
            elif data.get('message_type') == 'FinalTranscript':
                # Final transcription with turn detection
                text = data.get('text', '').strip()
                if text:
                    print(f"✅ FINAL TRANSCRIPT: {text}")
                    print(f"🔴 USER STOPPED TALKING - PROCESSING TURN")
                    
                    if self.transcription_callback:
                        self.transcription_callback(text)
                    
                    # DAY 18 & 19: Trigger turn detection with final transcript
                    if self.turn_detection_callback:
                        turn_data = {
                            'type': 'turn_end',
                            'message': 'User stopped talking - turn detected',
                            'transcript': text,
                            'confidence': data.get('confidence', 0.0),
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        print(f"🎯 DAY 18: TURN DETECTION TRIGGERED")
                        print(f"🚀 DAY 19: PREPARING STREAMING LLM FOR: {text}")
                        self.turn_detection_callback(turn_data)

            elif data.get('message_type') == 'SessionBegins':
                print("✅ AssemblyAI session started successfully")
                self.is_connected = True

            elif data.get('message_type') == 'SessionTerminated':
                print("🔴 AssemblyAI session terminated")
                self.is_connected = False
                self.is_streaming = False

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            print(f"❌ Message processing error: {str(e)}")
            if "WebSocket connection is closed" in str(e):
                self.is_connected = False
                self.is_streaming = False

    def _on_error(self, ws, error):
        """Handle WebSocket errors"""
        logger.error(f"WebSocket error: {error}")
        print(f"\n❌ WEBSOCKET ERROR: {error}")
        self.connection_error = str(error)
        self.is_connected = False
        self.is_streaming = False

    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket connection closed"""
        logger.info(f"WebSocket connection closed: {close_status_code} - {close_msg}")
        print(f"\n🔴 WEBSOCKET CLOSED: {close_status_code} - {close_msg}")
        self.is_connected = False
        self.is_streaming = False
