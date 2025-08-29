
"""
Request schemas for API validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional

class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=3000, description="Text to convert to speech")
    voice_id: Optional[str] = Field("en-US-natalie", description="Voice ID for TTS")
    
    @validator('text')
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError('Text cannot be empty')
        return v.strip()

class LLMQueryRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, description="Query text for LLM")
    
    @validator('text')
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError('Query text cannot be empty')
        return v.strip()

class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    timestamp: str = Field(..., description="Message timestamp")
    
    @validator('role')
    def validate_role(cls, v):
        if v not in ['user', 'assistant']:
            raise ValueError('Role must be either user or assistant')
        return v
