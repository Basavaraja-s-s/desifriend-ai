# DesiFriend AI - Main FastAPI Application
"""
Main FastAPI application for DesiFriend AI backend.
Handles API endpoints, CORS, and module initialization.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from pathlib import Path
import uuid
import asyncio

# Import modules
from language_detector import LanguageDetector
from country_detector import CountryDetector
from context_manager import ContextManager
from ai_engine import AIEngine
from speech_to_text import SpeechToText
from text_to_speech import TextToSpeech

# Import models
from models import (
    ChatRequest, ChatResponse, VoiceChatRequest,
    HealthResponse, ErrorResponse, LanguageDetectionResult
)

# Load environment variables
load_dotenv()

# Initialize modules globally
language_detector = None
country_detector = None
context_manager = None
ai_engine = None
speech_to_text = None
text_to_speech = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    global language_detector, country_detector, context_manager
    global ai_engine, speech_to_text, text_to_speech
    
    print("Initializing DesiFriend AI modules...")
    
    # Initialize all modules
    language_detector = LanguageDetector()
    country_detector = CountryDetector()
    context_manager = ContextManager(
        session_timeout_minutes=int(os.getenv('SESSION_TIMEOUT_MINUTES', 30)),
        max_history=int(os.getenv('MAX_CONVERSATION_HISTORY', 10))
    )
    ai_engine = AIEngine()
    speech_to_text = SpeechToText()
    text_to_speech = TextToSpeech(
        output_dir=os.getenv('AUDIO_OUTPUT_DIR', 'audio_files')
    )
    
    # Create audio directory
    audio_dir = Path(os.getenv('AUDIO_OUTPUT_DIR', 'audio_files'))
    audio_dir.mkdir(exist_ok=True)
    
    # Start background task for session cleanup
    cleanup_task = asyncio.create_task(periodic_cleanup())
    
    print("DesiFriend AI initialized successfully!")
    
    yield
    
    # Shutdown
    print("Shutting down DesiFriend AI...")
    cleanup_task.cancel()


# Create FastAPI app
app = FastAPI(
    title="DesiFriend AI",
    description="AI companion with multi-language support and Indian accent voices",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
allowed_origins = os.getenv('ALLOWED_ORIGINS', '*').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins != ['*'] else ['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for audio
audio_dir = Path(os.getenv('AUDIO_OUTPUT_DIR', 'audio_files'))
audio_dir.mkdir(exist_ok=True)
app.mount("/audio", StaticFiles(directory=str(audio_dir)), name="audio")


async def periodic_cleanup():
    """Background task to periodically clean up expired sessions."""
    while True:
        await asyncio.sleep(300)  # Run every 5 minutes
        if context_manager:
            cleaned = context_manager.cleanup_expired_sessions()
            if cleaned > 0:
                print(f"Cleaned up {cleaned} expired sessions")


@app.get("/", response_model=dict)
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to DesiFriend AI!",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/chat",
            "voice_chat": "/api/voice-chat",
            "health": "/api/health"
        }
    }


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        active_sessions=context_manager.get_session_count() if context_manager else 0
    )


# Additional endpoints will be implemented in subsequent tasks
# - POST /api/chat (Task 5.3)
# - POST /api/voice-chat (Task 5.4)




@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint for text-based conversations.
    Detects language, generates AI response, and creates audio.
    """
    try:
        # Get or create session
        session_id = request.session_id
        if not session_id or not context_manager.session_exists(session_id):
            session_id = context_manager.create_session()
        
        # Detect language
        lang_result = language_detector.detect_language(request.message)
        
        # Detect country
        country_code = country_detector.detect_country(
            device_locale=request.device_locale,
            ip_address=request.ip_address
        )
        
        # Get conversation history
        conversation_history = context_manager.get_conversation_context(session_id)
        
        # Add user message to context
        context_manager.add_message(
            session_id=session_id,
            role='user',
            content=request.message,
            language=lang_result['language_code']
        )
        
        # Generate AI response
        ai_response = ai_engine.generate_response(
            user_message=request.message,
            conversation_history=conversation_history,
            language_code=lang_result['language_code'],
            language_name=lang_result['language_name']
        )
        
        # Add AI response to context
        context_manager.add_message(
            session_id=session_id,
            role='assistant',
            content=ai_response,
            language=lang_result['language_code']
        )
        
        # Generate audio
        audio_filename = f"{session_id}_{uuid.uuid4().hex[:8]}"
        audio_bytes = text_to_speech.synthesize(
            text=ai_response,
            country_code=country_code,
            gender=request.voice_gender,
            language_code=lang_result['language_code']
        )
        
        # Save audio file
        audio_path = text_to_speech.output_dir / f"{audio_filename}.mp3"
        with open(audio_path, 'wb') as f:
            f.write(audio_bytes)
        
        # Build audio URL
        audio_url = f"/audio/{audio_filename}.mp3"
        
        # Build response
        return ChatResponse(
            session_id=session_id,
            user_message=request.message,
            ai_response=ai_response,
            audio_url=audio_url,
            detected_language=LanguageDetectionResult(**lang_result),
            detected_country=country_code
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/api/voice-chat", response_model=ChatResponse)
async def voice_chat(
    audio: UploadFile = File(...),
    session_id: str = Form(None),
    device_locale: str = Form(None),
    ip_address: str = Form(None),
    voice_gender: str = Form('female')
):
    """
    Voice chat endpoint for voice-based conversations.
    Transcribes audio, then processes like text chat.
    """
    try:
        # Validate audio format
        if not speech_to_text.is_supported_format(audio.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported audio format. Supported: {', '.join(speech_to_text.SUPPORTED_FORMATS)}"
            )
        
        # Read audio file
        audio_bytes = await audio.read()
        
        # Transcribe audio to text
        transcribed_text = speech_to_text.transcribe(
            audio_file=audio_bytes,
            filename=audio.filename
        )
        
        if not transcribed_text:
            raise HTTPException(status_code=400, detail="Could not transcribe audio")
        
        # Process as regular chat
        chat_request = ChatRequest(
            message=transcribed_text,
            session_id=session_id,
            device_locale=device_locale,
            ip_address=ip_address,
            voice_gender=voice_gender
        )
        
        # Call chat endpoint logic
        response = await chat(chat_request)
        
        # Add transcribed text to response
        response.transcribed_text = transcribed_text
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
