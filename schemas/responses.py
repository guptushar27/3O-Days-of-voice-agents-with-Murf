
"""
Response schemas for API responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict

class BaseResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message if failed")

class TTSResponse(BaseResponse):
    audio_url: Optional[str] = Field(None, description="URL to generated audio")
    voice_used: Optional[str] = Field(None, description="Voice ID used for generation")
    service_used: Optional[str] = Field(None, description="TTS service used")
    character_count: Optional[int] = Field(None, description="Character count of text")
    filename: Optional[str] = Field(None, description="Generated filename")

class TranscriptionResponse(BaseResponse):
    transcription: Optional[str] = Field(None, description="Transcribed text")
    confidence: Optional[float] = Field(None, description="Transcription confidence")
    audio_duration: Optional[float] = Field(None, description="Audio duration in seconds")
    word_count: Optional[int] = Field(None, description="Word count")
    fallback_message: Optional[str] = Field(None, description="Fallback message for errors")

class LLMResponse(BaseResponse):
    response: Optional[str] = Field(None, description="LLM generated response")
    model_used: Optional[str] = Field(None, description="Model used for generation")
    character_count: Optional[int] = Field(None, description="Response character count")
    fallback_response: Optional[str] = Field(None, description="Fallback response for errors")

class ConversationResponse(BaseResponse):
    audio_url: Optional[str] = Field(None, description="Response audio URL")
    transcription: Optional[str] = Field(None, description="User input transcription")
    llm_response: Optional[str] = Field(None, description="AI response text")
    session_id: str = Field(..., description="Session identifier")
    message_count: int = Field(..., description="Total messages in session")
    model_used: Optional[str] = Field(None, description="LLM model used")
    voice_used: Optional[str] = Field(None, description="TTS voice used")
    response_type: Optional[str] = Field(None, description="Response type (conversational/fallback)")
    had_transcription_error: Optional[bool] = Field(None, description="Whether transcription had errors")
    had_llm_error: Optional[bool] = Field(None, description="Whether LLM had errors")
    fallback_audio_url: Optional[str] = Field(None, description="Fallback audio URL")

class ChatHistoryResponse(BaseResponse):
    session_id: str = Field(..., description="Session identifier")
    messages: List[Dict[str, Any]] = Field(default_factory=list, description="Chat messages")
    message_count: int = Field(0, description="Total message count")
    created_at: Optional[str] = Field(None, description="Session creation timestamp")

class AudioUploadResponse(BaseResponse):
    filename: Optional[str] = Field(None, description="Uploaded filename")
    original_filename: Optional[str] = Field(None, description="Original filename")
    content_type: Optional[str] = Field(None, description="File content type")
    size: Optional[int] = Field(None, description="File size in bytes")
    size_human: Optional[str] = Field(None, description="Human readable file size")
    upload_time: Optional[str] = Field(None, description="Upload timestamp")
