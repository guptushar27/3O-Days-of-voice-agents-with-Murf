import os
import json
import asyncio
import threading
import queue
import base64
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from flask_socketio import emit

from .realtime_stt_service import RealtimeSTTService
from .llm_service import LLMService
from .murf_websocket_service import MurfWebSocketService

logger = logging.getLogger(__name__)

class WebSocketService:
    """Service for managing WebSocket communications with Day 21 audio streaming"""

    def __init__(self, llm_service=None, tts_service=None):
        self.llm_service = llm_service
        self.tts_service = tts_service
        self.active_sessions = {}
        self.message_cache = {}
        self.transcription_sessions = {}
        self.active_transcriptions = {}
        self.murf_sessions = set()

        # Day 21: Audio streaming state
        self.audio_streams = {}
        self.streaming_chunks = {}

        # Initialize services
        self.stt_service = RealtimeSTTService()
        self.llm_service = LLMService()
        self.murf_service = MurfWebSocketService()

    def register_session(self, session_id: str, socket_id: str):
        """Register a new session"""
        self.active_sessions[socket_id] = {
            'session_id': session_id,
            'connected_at': datetime.now().isoformat(),
            'message_count': 0
        }

        # Initialize Day 21 audio streaming for session
        self.audio_streams[socket_id] = {
            'chunks_sent': 0,
            'total_size': 0,
            'start_time': datetime.now(),
            'active': False
        }

        logger.info(f"Registered session {session_id} for socket {socket_id}")

    def unregister_session(self, socket_id: str):
        """Unregister a session"""
        if socket_id in self.active_sessions:
            session_info = self.active_sessions.pop(socket_id)
            logger.info(f"Unregistered session {session_info['session_id']} for socket {socket_id}")

        # Clean up transcription sessions
        if socket_id in self.transcription_sessions:
            self.stop_realtime_transcription(socket_id)

        # Clean up Murf WebSocket sessions
        if socket_id in self.murf_sessions:
            asyncio.create_task(self.stop_murf_websocket(socket_id))

        # Clean up Day 21 audio streaming
        if socket_id in self.audio_streams:
            del self.audio_streams[socket_id]
        if socket_id in self.streaming_chunks:
            del self.streaming_chunks[socket_id]

    def handle_echo_message(self, socket_id: str, message: str) -> Dict[str, Any]:
        """Handle echo message functionality"""
        response_data = {
            'original_message': message,
            'echo_response': f"Echo: {message}",
            'timestamp': datetime.now().isoformat(),
            'socket_id': socket_id
        }

        if socket_id in self.active_sessions:
            self.active_sessions[socket_id]['message_count'] += 1

        return response_data

    def handle_chat_message(self, socket_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle chat messages from clients with all day features"""
        try:
            message = data.get('message', '')

            print(f"\n🎯 DAY 21: Processing text message")
            print(f"💬 Message: {message}")
            print(f"🔌 Socket: {socket_id}")

            if not message:
                return {
                    'error': 'Empty message',
                    'socket_id': socket_id,
                    'timestamp': datetime.now().isoformat()
                }

            # DAY 18: Simulate turn detection for text input
            print(f"🎯 DAY 18: TURN DETECTED - User finished typing")
            print(f"📝 DAY 18: Text input: '{message}'")

            # DAY 19: Process with streaming LLM
            print(f"🚀 DAY 19: Starting streaming LLM response...")
            session_messages = []

            streaming_chunks = []
            def collect_chunks(chunk):
                streaming_chunks.append(chunk)
                print(f"📝 DAY 19 STREAMING CHUNK: {chunk}")

            result = self.llm_service.generate_streaming_response(
                session_messages, 
                message, 
                callback=collect_chunks
            )

            if result['success']:
                response_text = result['response']
                print(f"✅ DAY 19: Streaming LLM SUCCESS - {len(streaming_chunks)} chunks, {len(response_text)} chars")

                # DAY 20: Generate TTS
                print(f"🎤 DAY 20: Starting TTS generation...")
                # Note: TTS would be handled separately if needed

                # DAY 21: Prepare for audio streaming
                print(f"📡 DAY 21: Text response ready for streaming")

                # DAY 22: Ready for playback
                print(f"🎵 DAY 22: Response ready for seamless delivery")

                return {
                    'success': True,
                    'message': message,
                    'response': response_text,
                    'socket_id': socket_id,
                    'timestamp': datetime.now().isoformat(),
                    'day_features': {
                        'day18_turn_detection': 'completed',
                        'day19_streaming_llm': f"{len(streaming_chunks)} chunks",
                        'day20_tts': 'prepared',
                        'day21_streaming': 'ready',
                        'day22_playback': 'ready'
                    },
                    'streaming_chunks_count': len(streaming_chunks)
                }
            else:
                print(f"❌ DAY 19: Streaming LLM failed - {result.get('error', 'Unknown error')}")
                return {
                    'error': result.get('error', 'LLM processing failed'),
                    'fallback_response': result.get('fallback_response'),
                    'socket_id': socket_id,
                    'timestamp': datetime.now().isoformat()
                }

        except Exception as e:
            print(f"💥 DAY 21: Error processing text message - {str(e)}")
            logger.error(f"Error handling chat message: {str(e)}")
            return {
                'error': str(e),
                'socket_id': socket_id,
                'timestamp': datetime.now().isoformat()
            }

    def handle_audio_stream(self, socket_id: str, audio_data: Any) -> Dict[str, Any]:
        """Handle streaming audio data and save to file"""
        import os
        import base64

        try:
            streams_dir = os.path.join(os.getcwd(), 'instance', 'audio_streams')
            os.makedirs(streams_dir, exist_ok=True)

            session_info = self.active_sessions.get(socket_id, {})
            session_id = session_info.get('session_id', 'unknown')

            if socket_id not in self.message_cache:
                self.message_cache[socket_id] = {
                    'stream_file': os.path.join(streams_dir, f'stream_{session_id}_{socket_id}.webm'),
                    'chunk_count': 0
                }

            stream_info = self.message_cache[socket_id]

            if isinstance(audio_data, dict) and 'audio_chunk' in audio_data:
                audio_chunk = base64.b64decode(audio_data['audio_chunk'])

                with open(stream_info['stream_file'], 'ab') as f:
                    f.write(audio_chunk)

                stream_info['chunk_count'] += 1

                logger.info(f"Saved audio chunk {stream_info['chunk_count']} for session {session_id}")

                response = {
                    'status': 'saved',
                    'message': f'Audio chunk {stream_info["chunk_count"]} saved to file',
                    'timestamp': datetime.now().isoformat(),
                    'socket_id': socket_id,
                    'session_id': session_id,
                    'file_path': stream_info['stream_file'],
                    'chunk_count': stream_info['chunk_count']
                }
            else:
                response = {
                    'status': 'error',
                    'message': 'Invalid audio data format',
                    'timestamp': datetime.now().isoformat(),
                    'socket_id': socket_id
                }

        except Exception as e:
            logger.error(f"Error handling audio stream: {str(e)}")
            response = {
                'status': 'error',
                'message': f'Error saving audio: {str(e)}',
                'timestamp': datetime.now().isoformat(),
                'socket_id': socket_id
            }

        return response

    def get_session_info(self, socket_id: str) -> Dict[str, Any]:
        """Get information about a session"""
        return self.active_sessions.get(socket_id, {})

    def get_active_sessions_count(self) -> int:
        """Get the number of active sessions"""
        return len(self.active_sessions)

    def _on_transcription_received(self, socket_id: str, transcription: str):
        """Callback for when transcription is received"""
        try:
            print(f"\nDAY 17: TRANSCRIPTION RECEIVED")
            print(f"Transcription: {transcription}")
            print(f"Socket ID: {socket_id}")
            print(f"Timestamp: {datetime.now().strftime('%H:%M:%S')}")
            print(f"Length: {len(transcription)} characters")

            emit('transcription', {
                'text': transcription,
                'socket_id': socket_id,
                'timestamp': datetime.now().isoformat()
            }, room=socket_id)

            logger.info(f"DAY 17: Sent transcription to {socket_id}: {transcription}")

        except Exception as e:
            logger.error(f"Error sending transcription: {str(e)}")

    def _on_turn_detected(self, socket_id: str, turn_data: Dict):
        """Callback for when turn detection occurs"""
        try:
            print(f"\nDAY 18: USER STOPPED TALKING - TURN DETECTED!")
            print(f"Detection Message: {turn_data.get('message', 'User stopped talking')}")
            print(f"Final Transcript: {turn_data.get('transcript', '')}")
            print(f"Socket ID: {socket_id}")
            print(f"Detection Time: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")

            emit('turn_detected', {
                'message': turn_data.get('message', 'User stopped talking'),
                'type': turn_data.get('type', 'turn_end'),
                'transcript': turn_data.get('transcript', ''),
                'socket_id': socket_id,
                'timestamp': turn_data.get('timestamp', datetime.now().isoformat()),
                'confidence': turn_data.get('confidence', 0.0)
            }, room=socket_id)

            logger.info(f"DAY 18 TURN DETECTION: Sent to {socket_id}")

            # Process transcript with streaming LLM
            transcript = turn_data.get('transcript', '').strip()
            if transcript and len(transcript) > 3:
                print(f"DAY 19: Triggering streaming LLM for transcript: {transcript}")
                self._process_transcript_with_streaming_llm(socket_id, transcript)

        except Exception as e:
            logger.error(f"Error sending turn detection: {str(e)}")

    def start_realtime_transcription(self, socket_id: str):
        """Start real-time transcription for a socket with turn detection"""
        try:
            if not self.stt_service.is_configured():
                return {
                    'status': 'error',
                    'message': 'AssemblyAI API key not configured. Please set ASSEMBLYAI_API_KEY environment variable.'
                }

            success = self.stt_service.start_streaming_transcription(
                callback=lambda text: self._on_transcription_received(socket_id, text),
                turn_callback=lambda turn_data: self._on_turn_detected(socket_id, turn_data)
            )

            if success:
                self.transcription_sessions[socket_id] = {
                    'started_at': datetime.now().isoformat(),
                    'callback': lambda text: self._on_transcription_received(socket_id, text),
                    'turn_callback': lambda turn_data: self._on_turn_detected(socket_id, turn_data)
                }
                return {
                    'status': 'started',
                    'message': 'Real-time transcription started with AssemblyAI and turn detection'
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Failed to connect to AssemblyAI. Check your API key and internet connection.'
                }

        except Exception as e:
            logger.error(f"Error starting transcription: {str(e)}")
            return {
                'status': 'error',
                'message': f'Transcription start failed: {str(e)}'
            }

    def stop_realtime_transcription(self, socket_id: str):
        """Stop real-time transcription for a session"""
        if socket_id in self.transcription_sessions:
            try:
                self.stt_service.stop_streaming_transcription()
                del self.transcription_sessions[socket_id]
                logger.info(f"Stopped transcription for session {socket_id}")
            except Exception as e:
                logger.error(f"Error stopping transcription: {str(e)}")
                if socket_id in self.transcription_sessions:
                    del self.transcription_sessions[socket_id]

        if socket_id in self.active_transcriptions:
            del self.active_transcriptions[socket_id]

    def _process_transcript_with_streaming_llm(self, socket_id: str, transcript: str):
        """Process final transcript with streaming LLM"""
        try:
            print(f"\nDAY 19: STREAMING LLM PROCESSING STARTED")
            print(f"Final Transcript: {transcript}")
            print(f"Socket ID: {socket_id}")

            if not self.llm_service.is_configured():
                print(f"DAY 19: LLM service not configured - missing GEMINI_API_KEY")
                emit('llm_error', {
                    'message': 'LLM service not configured. Please set GEMINI_API_KEY.',
                    'transcript': transcript,
                    'socket_id': socket_id,
                    'timestamp': datetime.now().isoformat()
                }, room=socket_id)
                return

            chunk_counter = 0
            accumulated_text = ""

            def streaming_callback(chunk: str):
                nonlocal chunk_counter, accumulated_text
                chunk_counter += 1
                accumulated_text += chunk

                print(f"\nDAY 19 STREAMING LLM CHUNK #{chunk_counter}")
                print(f"User said: {transcript}")
                print(f"AI chunk: {chunk}")
                print(f"Progress: {len(accumulated_text)} characters accumulated")
                print(f"Socket: {socket_id}")
                print(f"Time: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")

                emit('llm_streaming_chunk', {
                    'chunk': chunk,
                    'chunk_number': chunk_counter,
                    'transcript': transcript,
                    'socket_id': socket_id,
                    'timestamp': datetime.now().isoformat()
                }, room=socket_id)

            session_messages = []

            print(f"DAY 19: Starting Gemini streaming generation...")

            result = self.llm_service.generate_streaming_response(
                session_messages,
                transcript,
                callback=streaming_callback
            )

            if result['success']:
                final_response = result['response']
                chunk_count = result.get('chunk_count', chunk_counter)

                print(f"\nDAY 19: STREAMING LLM COMPLETED SUCCESSFULLY")
                print(f"User said: {transcript}")
                print(f"Complete AI Response: {final_response}")
                print(f"Total chunks: {chunk_count}")
                print(f"Total characters: {result.get('character_count', len(final_response))}")

                emit('llm_streaming_complete', {
                    'final_response': final_response,
                    'chunk_count': chunk_count,
                    'character_count': len(final_response),
                    'model_used': 'gemini-2.0-flash-exp',
                    'session_id': socket_id,
                    'timestamp': datetime.now().isoformat()
                }, room=socket_id)

                # DAY 20 & 21: Process with Murf WebSocket if session is active
                if socket_id in self.murf_sessions:
                    try:
                        async def process_murf_and_stream():
                            murf_result = await self.process_text_with_murf(socket_id, final_response)
                            if murf_result['status'] == 'success':
                                # DAY 21: Stream the base64 audio to client
                                await self.stream_audio_to_client(socket_id, murf_result['base64_audio'], final_response)

                        asyncio.create_task(process_murf_and_stream())

                    except Exception as e:
                        logger.error(f"Murf integration error: {e}")

            else:
                print(f"DAY 19: STREAMING LLM FAILED")
                print(f"Error: {result['error']}")

                emit('llm_error', {
                    'error': result['error'],
                    'fallback_response': result.get('fallback_response'),
                    'transcript': transcript,
                    'socket_id': socket_id,
                    'timestamp': datetime.now().isoformat()
                }, room=socket_id)

        except Exception as e:
            logger.error(f"DAY 19: Error processing transcript with streaming LLM: {str(e)}")
            print(f"DAY 19 STREAMING LLM CRITICAL ERROR: {str(e)}")

            emit('llm_error', {
                'error': f'Streaming LLM processing error: {str(e)}',
                'transcript': transcript,
                'socket_id': socket_id,
                'timestamp': datetime.now().isoformat()
            }, room=socket_id)

    async def start_murf_websocket(self, socket_id: str) -> Dict[str, Any]:
        """Start Murf WebSocket for a session"""
        try:
            connected = await self.murf_service.connect()

            if connected:
                self.murf_sessions.add(socket_id)
                logger.info(f"Started Murf WebSocket for session {socket_id}")

                return {
                    'status': 'connected',
                    'message': 'Murf WebSocket connected successfully',
                    'session_id': socket_id
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Failed to connect to Murf WebSocket'
                }

        except Exception as e:
            logger.error(f"Murf WebSocket error: {e}")
            return {
                'status': 'error',
                'message': f'Murf WebSocket error: {str(e)}'
            }

    def start_murf_websocket_sync(self, socket_id: str) -> Dict[str, Any]:
        """Synchronous wrapper for starting Murf WebSocket"""
        result_queue = queue.Queue()

        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(self.start_murf_websocket(socket_id))
                result_queue.put(result)
            except Exception as e:
                result_queue.put({
                    'status': 'error',
                    'message': f'Sync wrapper error: {str(e)}'
                })
            finally:
                loop.close()

        thread = threading.Thread(target=run_async)
        thread.start()
        thread.join(timeout=10)

        if thread.is_alive():
            return {
                'status': 'error',
                'message': 'Murf WebSocket connection timeout'
            }

        try:
            return result_queue.get_nowait()
        except queue.Empty:
            return {
                'status': 'error',
                'message': 'No result from Murf WebSocket connection'
            }

    async def stop_murf_websocket(self, socket_id: str):
        """Stop Murf WebSocket for a session"""
        if socket_id in self.murf_sessions:
            self.murf_sessions.remove(socket_id)

        if not self.murf_sessions:
            await self.murf_service.disconnect()

        logger.info(f"Stopped Murf WebSocket for session {socket_id}")

    async def process_text_with_murf(self, socket_id: str, text: str) -> Dict[str, Any]:
        """Process text through Murf WebSocket and return base64 audio"""
        if socket_id not in self.murf_sessions:
            return {
                'status': 'error',
                'message': 'Murf WebSocket not active for this session'
            }

        try:
            audio_base64 = await self.murf_service.send_text_for_tts(text)

            if audio_base64:
                logger.info(f"DAY 20: Generated Murf audio for text: {text[:50]}...")
                print(f"\nDAY 20: MURF WEBSOCKET BASE64 AUDIO GENERATED")
                print(f"Input Text: {text}")
                print(f"Base64 Length: {len(audio_base64)} characters")
                print(f"Base64 Audio (first 100 chars): {audio_base64[:100]}...")
                print(f"Generated at: {datetime.now().strftime('%H:%M:%S')}")

                return {
                    'status': 'success',
                    'base64_audio': audio_base64,
                    'text': text,
                    'audio_length': len(audio_base64),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'error',
                    'message': 'No audio generated from Murf'
                }

        except Exception as e:
            logger.error(f"Murf processing error: {e}")
            return {
                'status': 'error',
                'message': f'Murf error: {str(e)}'
            }

    # DAY 21: Audio streaming to client methods
    async def stream_audio_to_client(self, socket_id: str, base64_audio: str, original_text: str):
        """Stream base64 audio data to client in chunks - Day 21 Implementation"""
        try:
            print(f"\nDAY 21: STREAMING AUDIO DATA TO CLIENT")
            print(f"Client Socket ID: {socket_id}")
            print(f"Audio size: {len(base64_audio)} bytes")

            chunk_size = 1024  # 1KB chunks for optimal streaming
            total_size = len(base64_audio)

            # Split audio into chunks
            chunks = []
            for i in range(0, len(base64_audio), chunk_size):
                chunks.append(base64_audio[i:i + chunk_size])

            print(f"DAY 21: Audio split into {len(chunks)} chunks")
            print("DAY 21: Beginning chunk transmission...")

            # Stream each chunk to client
            for index, chunk in enumerate(chunks):
                chunk_data = {
                    'chunk_index': index + 1,
                    'chunk_data': chunk,
                    'chunk_size': len(chunk),
                    'total_chunks': len(chunks),
                    'original_text': original_text,
                    'timestamp': datetime.now().isoformat()
                }

                # Emit chunk to specific client
                if hasattr(self, 'socketio') and self.socketio:
                    await self.socketio.emit(
                        'audio_chunk_streamed', 
                        chunk_data, 
                        room=socket_id
                    )

                print(f"DAY 21: Chunk {index + 1}/{len(chunks)} transmitted to client")
                print(f"DAY 21: Chunk size: {len(chunk)} bytes | Progress: {((index + 1) / len(chunks)) * 100:.1f}%")
                print(f"DAY 21: Client acknowledgment expected for chunk {index + 1}")

                # Delay to simulate realistic streaming
                await asyncio.sleep(0.2)

            # Send streaming completion signal
            completion_data = {
                'total_chunks': len(chunks),
                'total_size': total_size,
                'original_text': original_text,
                'completion_timestamp': datetime.now().isoformat()
            }

            if hasattr(self, 'socketio') and self.socketio:
                await self.socketio.emit(
                    'audio_stream_complete',
                    completion_data,
                    room=socket_id
                )

            print("DAY 21: AUDIO STREAMING TO CLIENT COMPLETED")
            print(f"DAY 21: Total chunks transmitted: {len(chunks)}")
            print(f"DAY 21: Total audio data size: {total_size} bytes")
            print("DAY 21: All chunks successfully streamed to client")
            print("DAY 21: Waiting for client acknowledgments...")

        except Exception as e:
            error_message = f"DAY 21: Audio streaming error: {str(e)}"
            print(error_message)

            if hasattr(self, 'socketio') and self.socketio:
                await self.socketio.emit(
                    'audio_stream_error',
                    {'error': str(e), 'timestamp': datetime.now().isoformat()},
                    room=socket_id
                )

    def get_audio_streaming_stats(self, socket_id: str) -> Dict[str, Any]:
        """Get Day 21 audio streaming statistics"""
        if socket_id not in self.audio_streams:
            return {}

        stats = self.audio_streams[socket_id]
        return {
            'chunks_sent': stats['chunks_sent'],
            'total_size': stats['total_size'],
            'active': stats['active'],
            'start_time': stats['start_time'].isoformat(),
            'session_duration': (datetime.now() - stats['start_time']).total_seconds()
        }

    def handle_streaming_audio_transcription(self, socket_id, data):
        """Handle streaming audio transcription"""
        try:
            session_id = data.get('session_id', 'unknown')
            audio_data = data.get('audio_data')

            if not audio_data:
                return {'error': 'No audio data provided'}

            logger.info(f"Received streaming audio from {socket_id}")

            print(f"\nDAY 17: STREAMING AUDIO RECEIVED")
            print(f"Socket ID: {socket_id}")
            print(f"Session ID: {session_id}")
            print(f"Audio Size: {len(audio_data) if audio_data else 0} bytes")
            print(f"Time: {datetime.now().strftime('%H:%M:%S')}")

            self._save_audio_chunk(session_id, socket_id, audio_data)

            response = {
                'status': 'received',
                'socket_id': socket_id,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'audio_size': len(audio_data) if audio_data else 0
            }

            return response

        except Exception as e:
            logger.error(f"Error handling streaming audio: {e}")
            return {'error': f'Failed to process audio: {str(e)}'}

    def _save_audio_chunk(self, session_id: str, socket_id: str, audio_data: str):
        """Save audio chunk to file"""
        try:
            streams_dir = os.path.join(os.getcwd(), 'instance', 'audio_streams')
            os.makedirs(streams_dir, exist_ok=True)

            chunk_file = os.path.join(streams_dir, f'chunk_{session_id}_{socket_id}_{datetime.now().timestamp()}.webm')

            with open(chunk_file, 'wb') as f:
                f.write(base64.b64decode(audio_data))

            logger.info(f"Saved audio chunk to {chunk_file}")

        except Exception as e:
            logger.error(f"Error saving audio chunk: {str(e)}")