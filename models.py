
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

def create_models(db):
    class TTSRequest(db.Model):
        """Model to track TTS requests for analytics/debugging"""
        
        __tablename__ = 'tts_requests'

        id = db.Column(db.Integer, primary_key=True)
        text = db.Column(db.Text, nullable=False)
        audio_url = db.Column(db.String(500))
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        success = db.Column(db.Boolean, default=False)
        error_message = db.Column(db.Text)

        def __repr__(self):
            return f'<TTSRequest {self.id}: {self.text[:50]}...>'

    return TTSRequest
