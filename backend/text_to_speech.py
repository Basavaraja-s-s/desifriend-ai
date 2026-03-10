# DesiFriend AI - Text-to-Speech Module
"""
Text-to-Speech module for DesiFriend AI.
Converts AI responses to speech with Indian accent support.
Uses OpenAI TTS API for voice generation.
"""

from openai import OpenAI
from typing import Optional
import os
from pathlib import Path


class TextToSpeech:
    """
    Text-to-Speech converter with Indian accent support.
    Generates audio from text using OpenAI TTS API.
    """
    
    # Voice mapping based on country and gender
    VOICE_MAP = {
        'IN': {
            'male': 'onyx',    # Deep, warm voice suitable for Indian accent
            'female': 'nova'   # Friendly, warm female voice
        },
        'US': {
            'male': 'onyx',
            'female': 'nova'
        },
        'GB': {
            'male': 'echo',    # British-style voice
            'female': 'shimmer'
        },
        'OTHER': {
            'male': 'onyx',
            'female': 'nova'
        }
    }
    
    def __init__(self, api_key: Optional[str] = None, 
                 output_dir: str = "audio_files"):
        """
        Initialize the Text-to-Speech module.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            output_dir: Directory to save audio files
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # TTS settings
        self.model = "tts-1"  # Use tts-1 for faster, lower latency
        self.audio_format = "mp3"
    
    def synthesize(self, text: str, 
                  country_code: str = 'IN',
                  gender: str = 'female',
                  language_code: Optional[str] = None) -> bytes:
        """
        Convert text to speech audio.
        
        Args:
            text: Text to convert to speech
            country_code: Country code for accent ('IN', 'US', 'GB', 'OTHER')
            gender: Voice gender ('male' or 'female')
            language_code: Language code (e.g., 'hi', 'en') - currently informational
            
        Returns:
            Audio data as bytes (MP3 format)
        """
        try:
            # Select appropriate voice
            voice = self._select_voice(country_code, gender)
            
            # Call OpenAI TTS API
            response = self.client.audio.speech.create(
                model=self.model,
                voice=voice,
                input=text,
                response_format=self.audio_format
            )
            
            # Return audio bytes
            return response.content
            
        except Exception as e:
            raise Exception(f"Text-to-speech synthesis failed: {str(e)}")
    
    def synthesize_and_save(self, text: str,
                           filename: str,
                           country_code: str = 'IN',
                           gender: str = 'female',
                           language_code: Optional[str] = None) -> str:
        """
        Convert text to speech and save to file.
        
        Args:
            text: Text to convert to speech
            filename: Output filename (without extension)
            country_code: Country code for accent
            gender: Voice gender
            language_code: Language code
            
        Returns:
            Path to saved audio file
        """
        # Generate audio
        audio_bytes = self.synthesize(text, country_code, gender, language_code)
        
        # Save to file
        output_path = self.output_dir / f"{filename}.{self.audio_format}"
        with open(output_path, 'wb') as f:
            f.write(audio_bytes)
        
        return str(output_path)
    
    def _select_voice(self, country_code: str, gender: str) -> str:
        """
        Select appropriate voice based on country and gender.
        
        Args:
            country_code: Country code
            gender: Voice gender
            
        Returns:
            Voice identifier for OpenAI TTS
        """
        # Normalize inputs
        country_code = country_code.upper()
        gender = gender.lower()
        
        # Default to India if country not found
        if country_code not in self.VOICE_MAP:
            country_code = 'IN'
        
        # Default to female if gender not found
        if gender not in ['male', 'female']:
            gender = 'female'
        
        return self.VOICE_MAP[country_code][gender]
    
    def set_model(self, model: str):
        """
        Change the TTS model.
        
        Args:
            model: Model name ('tts-1' for speed, 'tts-1-hd' for quality)
        """
        self.model = model
    
    def get_supported_voices(self) -> list:
        """
        Get list of all supported voice options.
        
        Returns:
            List of voice identifiers
        """
        voices = set()
        for country_voices in self.VOICE_MAP.values():
            voices.update(country_voices.values())
        return sorted(list(voices))
