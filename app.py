import os
import logging
import tempfile
import hashlib
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
from pydantic import ValidationError

# Import services
from services.stt_service import STTService
from services.llm_service import LLMService
from services.tts_service import TTSService

# Import schemas
from schemas.requests import TTSRequest, LLMQueryRequest
from schemas.responses import (
    TTSResponse, TranscriptionResponse, LLMResponse,
    ConversationResponse, ChatHistoryResponse, AudioUploadResponse
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# In-memory chat sessions (use database in production)
chat_sessions = {}

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "voxaura-ai-voice-agent-2024")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///tts_client.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize database
db.init_app(app)

# Initialize services
stt_service = STTService()
llm_service = LLMService()
tts_service = TTSService(app)

with app.app_context():
    import models
    db.create_all()

@app.route('/')
def index():
    """Serve the main VoxAura interface"""
    return render_template('index.html')

@app.route('/test-llm')
def test_llm():
    """Serve the component testing interface"""
    return render_template('test_llm.html')

@app.route('/generate-tts', methods=['POST'])
def generate_tts():
    """Generate TTS audio from text"""
    try:
        # Validate request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided', 'success': False}), 400

        try:
            tts_request = TTSRequest(**data)
        except ValidationError as e:
            return jsonify({'error': f'Invalid request: {str(e)}', 'success': False}), 400

        logger.info(f"Generating TTS for: {tts_request.text[:50]}...")

        # Generate audio
        result = tts_service.generate_speech(tts_request.text, tts_request.voice_id)

        # Log to database
        tts_db_request = models.TTSRequest()
        tts_db_request.text = tts_request.text
        tts_db_request.success = result['success']

        if result['success']:
            tts_db_request.audio_url = result['audio_url']
            logger.info(f"TTS generated successfully using {result.get('service_used', 'unknown')}")
        else:
            tts_db_request.error_message = result['error']
            logger.error(f"TTS generation failed: {result['error']}")

        db.session.add(tts_db_request)
        db.session.commit()

        # Return response
        if result['success']:
            response = TTSResponse(
                success=True,
                audio_url=result['audio_url'],
                voice_used=result.get('voice_used'),
                service_used=result.get('service_used'),
                character_count=result.get('character_count'),
                filename=result.get('filename'),
                message='Audio generated successfully'
            )
        else:
            response = TTSResponse(
                success=False,
                error=result['error'],
                message='Audio generation failed'
            )

        return jsonify(response.dict())

    except Exception as e:
        logger.error(f"TTS endpoint error: {str(e)}")
        return jsonify({
            'error': f'Audio generation failed: {str(e)}',
            'success': False
        }), 500

@app.route('/transcribe/file', methods=['POST'])
def transcribe_file():
    """Transcribe audio file to text"""
    try:
        if 'audio' not in request.files:
            return jsonify({
                'error': 'No audio file provided',
                'success': False,
                'fallback_message': 'Please provide an audio file for transcription'
            }), 400

        audio_file = request.files['audio']

        if audio_file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'success': False,
                'fallback_message': 'Please select an audio file'
            }), 400

        logger.info(f"Transcribing audio file: {audio_file.filename}")

        # Transcribe using STT service
        result = stt_service.transcribe_audio(audio_file)

        # Create response
        if result['success']:
            response = TranscriptionResponse(
                success=True,
                transcription=result['transcription'],
                confidence=result.get('confidence'),
                audio_duration=result.get('audio_duration'),
                word_count=result.get('word_count'),
                message='Audio transcribed successfully'
            )
        else:
            response = TranscriptionResponse(
                success=False,
                error=result['error'],
                fallback_message=result.get('fallback_message'),
                transcription=result.get('transcription')
            )

        return jsonify(response.dict())

    except Exception as e:
        logger.error(f"Transcription endpoint error: {str(e)}")
        return jsonify({
            'error': f'Transcription failed: {str(e)}',
            'success': False,
            'fallback_message': 'An unexpected error occurred during transcription.'
        }), 500

@app.route('/agent/chat/<session_id>', methods=['POST'])
def agent_chat(session_id):
    """Main conversational AI agent endpoint"""
    try:
        # Validate audio input
        if 'audio' not in request.files:
            fallback_audio = tts_service.create_fallback_audio("Audio input is required for this service.")
            return jsonify({
                'error': 'Audio input is required for conversational agent',
                'success': False,
                'fallback_audio_url': fallback_audio
            }), 400

        audio_file = request.files['audio']

        if audio_file.filename == '':
            fallback_audio = tts_service.create_fallback_audio("No audio file was provided.")
            return jsonify({
                'error': 'No audio file selected',
                'success': False,
                'fallback_audio_url': fallback_audio
            }), 400

        logger.info(f"Processing conversation for session: {session_id}")

        # Initialize session
        if session_id not in chat_sessions:
            chat_sessions[session_id] = {
                'messages': [],
                'created_at': datetime.now().isoformat()
            }
            logger.info(f"Created new chat session: {session_id}")

        # Step 1: Transcribe audio
        transcription_result = stt_service.transcribe_audio(audio_file)

        if not transcription_result['success']:
            # Handle transcription failure
            user_message = "I'm having trouble with speech recognition right now"
            fallback_response = transcription_result.get('fallback_message',
                                                       "I'm having trouble connecting to my speech recognition service.")

            chat_sessions[session_id]['messages'].append({
                'role': 'user',
                'content': user_message,
                'timestamp': datetime.now().isoformat(),
                'transcription_error': True
            })

            fallback_audio = tts_service.create_fallback_audio(fallback_response)

            return jsonify({
                'error': transcription_result['error'],
                'success': False,
                'session_id': session_id,
                'fallback_audio_url': fallback_audio,
                'fallback_response': fallback_response,
                'transcription_fallback': user_message
            }), 500

        user_message = transcription_result['transcription']

        # Add user message to history
        chat_sessions[session_id]['messages'].append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })

        # Step 2: Generate LLM response
        llm_result = llm_service.generate_response(
            chat_sessions[session_id]['messages'],
            user_message
        )

        if not llm_result['success']:
            # Use fallback response
            llm_response = llm_result.get('fallback_response',
                                        "I'm having trouble connecting to my AI services right now.")
        else:
            llm_response = llm_result['response']

        # Add assistant response to history
        chat_sessions[session_id]['messages'].append({
            'role': 'assistant',
            'content': llm_response,
            'timestamp': datetime.now().isoformat(),
            'llm_error': not llm_result['success']
        })

        # Step 3: Generate speech
        tts_result = tts_service.generate_speech(llm_response)

        if not tts_result['success']:
            # Return text response with fallback audio
            fallback_audio = tts_service.create_fallback_audio(
                llm_response[:100] + "... I'm having trouble with voice generation."
            )

            response = ConversationResponse(
                error=f'Voice generation failed: {tts_result["error"]}',
                success=False,
                transcription=user_message,
                llm_response=llm_response,
                session_id=session_id,
                message_count=len(chat_sessions[session_id]['messages']),
                fallback_audio_url=fallback_audio,
                had_transcription_error=False,
                had_llm_error=not llm_result['success'],
                response_type='fallback'
            )
        else:
            # Successful full pipeline
            response = ConversationResponse(
                success=True,
                audio_url=tts_result['audio_url'],
                transcription=user_message,
                llm_response=llm_response,
                session_id=session_id,
                message_count=len(chat_sessions[session_id]['messages']),
                model_used=llm_result.get('model_used', 'gemini-2.5-flash'),
                voice_used=tts_result.get('voice_used'),
                message='Conversational AI response generated successfully',
                response_type='conversational',
                had_transcription_error=False,
                had_llm_error=not llm_result['success']
            )

        return jsonify(response.dict())

    except Exception as e:
        logger.error(f"Conversational agent error: {str(e)}")

        fallback_response = "I'm having trouble connecting right now. Please try again in a moment."
        fallback_audio = tts_service.create_fallback_audio(fallback_response)

        return jsonify({
            'error': f'Conversational agent failed: {str(e)}',
            'success': False,
            'session_id': session_id,
            'fallback_audio_url': fallback_audio,
            'fallback_response': fallback_response,
            'response_type': 'error_fallback'
        }), 500

@app.route('/agent/chat/<session_id>/history', methods=['GET'])
def get_chat_history(session_id):
    """Get chat history for a session"""
    if session_id not in chat_sessions:
        return jsonify({'error': 'Session not found', 'success': False}), 404

    response = ChatHistoryResponse(
        success=True,
        session_id=session_id,
        messages=chat_sessions[session_id]['messages'],
        message_count=len(chat_sessions[session_id]['messages']),
        created_at=chat_sessions[session_id]['created_at']
    )

    return jsonify(response.dict())

@app.route('/agent/chat/<session_id>/clear', methods=['POST'])
def clear_chat_history(session_id):
    """Clear chat history for a session"""
    if session_id in chat_sessions:
        del chat_sessions[session_id]
        logger.info(f"Cleared chat history for session: {session_id}")

    return jsonify({
        'success': True,
        'message': f'Chat history cleared for session {session_id}'
    })

@app.route('/llm/query', methods=['POST'])
def llm_query():
    """Direct LLM query endpoint"""
    try:
        # Handle both text and audio input
        is_audio_request = 'audio' in request.files

        if is_audio_request:
            # Audio input - transcribe first
            audio_file = request.files['audio']
            if audio_file.filename == '':
                return jsonify({'error': 'No audio file selected', 'success': False}), 400

            transcription_result = stt_service.transcribe_audio(audio_file)
            if not transcription_result['success']:
                return jsonify({
                    'error': transcription_result['error'],
                    'success': False
                }), 500

            query_text = transcription_result['transcription']
        else:
            # Text input
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data provided', 'success': False}), 400

            try:
                llm_request = LLMQueryRequest(**data)
                query_text = llm_request.text
            except ValidationError as e:
                return jsonify({'error': f'Invalid request: {str(e)}', 'success': False}), 400

        logger.info(f"Processing LLM query: {query_text[:100]}...")

        # Generate response
        llm_result = llm_service.generate_response([], query_text)

        if not llm_result['success']:
            return jsonify({
                'error': llm_result['error'],
                'success': False,
                'query': query_text
            }), 500

        response_text = llm_result['response']

        if is_audio_request:
            # Generate audio response
            tts_result = tts_service.generate_speech(response_text)

            if not tts_result['success']:
                return jsonify({
                    'error': f'TTS generation failed: {tts_result["error"]}',
                    'success': False,
                    'transcription': query_text,
                    'llm_response': response_text
                }), 500

            return jsonify({
                'success': True,
                'audio_url': tts_result['audio_url'],
                'transcription': query_text,
                'llm_response': response_text,
                'query': query_text,
                'model_used': llm_result.get('model_used'),
                'voice_used': tts_result.get('voice_used'),
                'message': 'LLM query processed with audio response',
                'response_type': 'audio'
            })
        else:
            # Text response
            response = LLMResponse(
                success=True,
                response=response_text,
                model_used=llm_result.get('model_used'),
                character_count=llm_result.get('character_count'),
                message='LLM response generated successfully'
            )

            return jsonify(response.dict())

    except Exception as e:
        logger.error(f"LLM query endpoint error: {str(e)}")
        return jsonify({
            'error': f'LLM query failed: {str(e)}',
            'success': False
        }), 500

@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    """Handle audio file upload"""
    try:
        if 'audio' not in request.files:
            return jsonify({
                'error': 'No audio file provided',
                'success': False
            }), 400

        audio_file = request.files['audio']

        if audio_file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'success': False
            }), 400

        # Process upload
        original_filename = audio_file.filename
        content_type = audio_file.content_type or 'audio/webm'

        # Create secure filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_extension = '.webm'
        if content_type:
            if 'mp4' in content_type:
                file_extension = '.mp4'
            elif 'wav' in content_type:
                file_extension = '.wav'

        secure_name = f"upload_{timestamp}_{uuid.uuid4().hex[:8]}{file_extension}"

        # Save file
        uploads_dir = os.path.join(app.instance_path, 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)

        file_path = os.path.join(uploads_dir, secure_name)
        audio_file.save(file_path)

        file_size = os.path.getsize(file_path)

        logger.info(f"Audio uploaded: {secure_name} ({file_size} bytes)")

        response = AudioUploadResponse(
            success=True,
            message='Audio file uploaded successfully',
            filename=secure_name,
            original_filename=original_filename,
            content_type=content_type,
            size=file_size,
            size_human=format_file_size(file_size),
            upload_time=datetime.now().isoformat()
        )

        return jsonify(response.dict())

    except Exception as e:
        logger.error(f"Audio upload error: {str(e)}")
        return jsonify({
            'error': f'Upload failed: {str(e)}',
            'success': False
        }), 500

@app.route('/audio/<filename>')
def serve_audio_file(filename):
    """Serve generated audio files"""
    try:
        audio_path = os.path.join(app.instance_path, 'static', 'audio', filename)

        if os.path.exists(audio_path):
            return send_file(audio_path, as_attachment=False, mimetype='audio/mpeg')
        else:
            return jsonify({'error': 'Audio file not found'}), 404

    except Exception as e:
        logger.error(f"Error serving audio file {filename}: {str(e)}")
        return jsonify({'error': 'Failed to serve audio file'}), 500

def format_file_size(size_bytes):
    """Convert file size to human readable format"""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)