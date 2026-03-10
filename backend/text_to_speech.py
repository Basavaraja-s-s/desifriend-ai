# DesiFriend AI - Text-to-Speech Module
"""
Text-to-Speech module for DesiFriend AI.
Converts AI responses to speech using Google Text-to-Speech (gTTS) - FREE!
Supports multiple languages including Indian languages.
"""

from gtts import gTTS
from typing import Optional
import os
from pathlib import Path
import io


class TextToSpeech:
    """
    Text-to-Speech converter using Google Text-to-Speech (gTTS).
    Completely free and supports multiple languages.
    """
    
    # Language code mapping for gTTS
    LANGUAGE_MAP = {
        'en': 'en',      # English
        'hi': 'hi',      # Hindi
        'kn': 'kn',      # Kannada (not supported by gTTS, fallback to Hindi)
        'ta': 'ta',      # Tamil
        'te': 'te',      # Telugu
        'ml': 'ml',      # Malayalam
        'bn': 'bn',      # Bengali
        'mr': 'mr',      # Marathi
        'gu': 'gu',      # Gujarati
        'pa': 'pa'       # Punjabi (not supported by gTTS, fallback to Hindi)
    }
    
    # Accent/TLD mapping based on country
    TLD_MAP = {
        'IN': 'co.in',   # India
        'US': 'com',     # USA
        'GB': 'co.uk',   # UK
        'OTHER': 'com'   # Default
    }
    
    def __init__(self, output_dir: str = "audio_files"):
        """
        Initialize the Text-to-Speech module.
        
        Args:
            output_dir: Directory to save audio files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.audio_format = "mp3"
    
    def synthesize(self, text: str, 
                  country_code: str = 'IN',
                  gender: str = 'female',
                  language_code: Optional[str] = None) -> bytes:
        """
        Convert text to speech audio using gTTS.
        
        Args:
            text: Text to convert to speech
            country_code: Country code for accent ('IN', 'US', 'GB', 'OTHER')
            gender: Voice gender (not used in gTTS, kept for compatibility)
            language_code: Language code (e.g., 'hi', 'en')
            
        Returns:
            Audio data as bytes (MP3 format)
        """
        try:
            # Select language
            lang = self._select_language(language_code)
            
            # Select TLD for accent
            tld = self.TLD_MAP.get(country_code.upper(), 'com')
            
            # Create gTTS object
            tts = gTTS(
                text=text,
                lang=lang,
                tld=tld,
                slow=False
            )
            
            # Save to bytes
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            
            return audio_fp.read()
            
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
            gender: Voice gender (not used in gTTS)
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
    
    def _select_language(self, language_code: Optional[str]) -> str:
        """
        Select appropriate language for gTTS.
        
        Args:
            language_code: Language code
            
        Returns:
            Language code for gTTS
        """
        if not language_code:
            return 'en'
        
        # Get language from map, fallback to Hindi for unsupported Indian languages
        lang = self.LANGUAGE_MAP.get(language_code.lower())
        
        if not lang:
            # If not in map, try using the code directly
            return language_code.lower()
        
        # For Kannada and Punjabi (not supported by gTTS), use Hindi
        if language_code.lower() in ['kn', 'pa']:
            return 'hi'
        
        return lang
    
    def get_supported_languages(self) -> list:
        """
        Get list of all supported language codes.
        
        Returns:
            List of language codes
        """
        return list(self.LANGUAGE_MAP.keys())
