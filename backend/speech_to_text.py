# DesiFriend AI - Speech-to-Text Module
"""
Speech-to-Text module for DesiFriend AI.
Converts voice input to text using OpenAI Whisper API.
Supports multiple audio formats and Indian languages.
"""

from openai import OpenAI
from typing import Optional
import os
import io


class SpeechToText:
    """
    Speech-to-Text converter using OpenAI Whisper API.
    Supports multiple audio formats and languages.
    """
    
    # Supported audio formats
    SUPPORTED_FORMATS = ['webm', 'mp3', 'wav', 'm4a', 'ogg']
    
    # Language code mapping for Whisper API
    LANGUAGE_CODES = {
        'hi': 'hindi',
        'kn': 'kannada',
        'ta': 'tamil',
        'te': 'telugu',
        'ml': 'malayalam',
        'bn': 'bengali',
        'mr': 'marathi',
        'gu': 'gujarati',
        'pa': 'punjabi',
        'en': 'english'
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Speech-to-Text module.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key)
    
    def transcribe(self, audio_file, 
                  language_hint: Optional[str] = None,
                  filename: str = "audio.webm") -> str:
        """
        Transcribe audio to text.
        
        Args:
            audio_file: Audio file object (bytes or file-like object)
            language_hint: Language code hint for better accuracy (e.g., 'hi', 'en')
            filename: Original filename with extension
            
        Returns:
            Transcribed text
        """
        try:
            # Prepare audio file for API
            if isinstance(audio_file, bytes):
                audio_file = io.BytesIO(audio_file)
                audio_file.name = filename
            
            # Prepare transcription parameters
            transcribe_params = {
                "model": "whisper-1",
                "file": audio_file
            }
            
            # Add language hint if provided
            if language_hint and language_hint in self.LANGUAGE_CODES:
                transcribe_params["language"] = language_hint
            
            # Call Whisper API
            response = self.client.audio.transcriptions.create(**transcribe_params)
            
            # Extract transcribed text
            transcribed_text = response.text.strip()
            return transcribed_text
            
        except Exception as e:
            # Return error message
            raise Exception(f"Speech-to-text transcription failed: {str(e)}")
    
    def is_supported_format(self, filename: str) -> bool:
        """
        Check if audio format is supported.
        
        Args:
            filename: Audio filename with extension
            
        Returns:
            True if format is supported
        """
        extension = filename.split('.')[-1].lower()
        return extension in self.SUPPORTED_FORMATS
    
    def get_language_code(self, language_name: str) -> Optional[str]:
        """
        Get language code from language name.
        
        Args:
            language_name: Full language name (e.g., 'Hindi', 'English')
            
        Returns:
            Language code or None
        """
        for code, name in self.LANGUAGE_CODES.items():
            if name.lower() == language_name.lower():
                return code
        return None
