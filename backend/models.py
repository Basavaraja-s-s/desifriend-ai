# DesiFriend AI - Pydantic Data Models
"""
Data models for API requests and responses.
Uses Pydantic for validation and serialization.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class Message(BaseModel):
    """Individual message in conversation."""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[str] = Field(None, description="ISO format timestamp")
    language: Optional[str] = Field(None, description="Detected language code")
    
    @validator('role')
    def validate_role(cls, v):
        if v not in ['user', 'assistant']:
            raise ValueError("Role must be 'user' or 'assistant'")
        return v


class LanguageDetectionResult(BaseModel):
    """Language detection result."""
    language_code: str = Field(..., description="ISO 639-1 language code")
    language_name: str = Field(..., description="Full language name")
    is_mixed: bool = Field(False, description="Whether text contains mixed languages")
    confidence: float = Field(..., description="Detection confidence (0.0 to 1.0)")
    detected_scripts: List[str] = Field(default_factory=list, description="Detected scripts")


class VoiceConfig(BaseModel):
    """Voice configuration for TTS."""
    country_code: str = Field('IN', description="Country code: IN, US, GB, OTHER")
    gender: str = Field('female', description="Voice gender: male or female")
    
    @validator('country_code')
    def validate_country(cls, v):
        if v not in ['IN', 'US', 'GB', 'OTHER']:
            raise ValueError("Country code must be IN, US, GB, or OTHER")
        return v
    
    @validator('gender')
    def validate_gender(cls, v):
        if v not in ['male', 'female']:
            raise ValueError("Gender must be male or female")
        return v


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1, description="User message text")
    session_id: Optional[str] = Field(None, description="Session ID for context")
    device_locale: Optional[str] = Field(None, description="Device locale (e.g., en-IN)")
    ip_address: Optional[str] = Field(None, description="User IP address")
    voice_gender: str = Field('female', description="Preferred voice gender")
    
    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()


class VoiceChatRequest(BaseModel):
    """Request model for voice chat endpoint (multipart form data)."""
    session_id: Optional[str] = Field(None, description="Session ID for context")
    device_locale: Optional[str] = Field(None, description="Device locale")
    ip_address: Optional[str] = Field(None, description="User IP address")
    voice_gender: str = Field('female', description="Preferred voice gender")


class ChatResponse(BaseModel):
    """Response model for chat endpoints."""
    session_id: str = Field(..., description="Session ID")
    user_message: str = Field(..., description="User's message")
    ai_response: str = Field(..., description="AI generated response")
    audio_url: Optional[str] = Field(None, description="URL to audio file")
    detected_language: LanguageDetectionResult = Field(..., description="Language detection result")
    detected_country: str = Field(..., description="Detected country code")
    transcribed_text: Optional[str] = Field(None, description="Transcribed text (voice chat only)")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Response timestamp")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field("healthy", description="Service status")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Check timestamp")
    active_sessions: int = Field(0, description="Number of active sessions")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Error timestamp")
