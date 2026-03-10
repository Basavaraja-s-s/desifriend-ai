# DesiFriend AI - Language Detector Module
"""
Language detection module for DesiFriend AI.
Detects user language from text input including support for Indian languages
and mixed languages like Hinglish and Kanglish.
"""

from langdetect import detect, detect_langs, LangDetectException
from typing import Dict, Optional
import re


class LanguageDetector:
    """
    Detects the language of user input text.
    Supports 10 Indian languages plus English and mixed language detection.
    """
    
    # Mapping of language codes to full names
    LANGUAGE_NAMES = {
        'hi': 'Hindi',
        'kn': 'Kannada',
        'ta': 'Tamil',
        'te': 'Telugu',
        'ml': 'Malayalam',
        'bn': 'Bengali',
        'mr': 'Marathi',
        'gu': 'Gujarati',
        'pa': 'Punjabi',
        'en': 'English'
    }
    
    # Unicode ranges for Indian scripts
    SCRIPT_RANGES = {
        'devanagari': (0x0900, 0x097F),  # Hindi, Marathi
        'bengali': (0x0980, 0x09FF),     # Bengali
        'gurmukhi': (0x0A00, 0x0A7F),    # Punjabi
        'gujarati': (0x0A80, 0x0AFF),    # Gujarati
        'tamil': (0x0B80, 0x0BFF),       # Tamil
        'telugu': (0x0C00, 0x0C7F),      # Telugu
        'kannada': (0x0C80, 0x0CFF),     # Kannada
        'malayalam': (0x0D00, 0x0D7F),   # Malayalam
    }
    
    def __init__(self):
        """Initialize the Language Detector."""
        pass
    
    def detect_language(self, text: str) -> Dict[str, any]:
        """
        Detect the language of the input text.
        
        Args:
            text: The input text to analyze
            
        Returns:
            Dictionary containing:
                - language_code: ISO 639-1 language code
                - language_name: Full language name
                - is_mixed: Boolean indicating if text contains mixed languages
                - confidence: Confidence score (0.0 to 1.0)
                - detected_scripts: List of detected scripts for mixed language
        """
        if not text or not text.strip():
            return {
                'language_code': 'en',
                'language_name': 'English',
                'is_mixed': False,
                'confidence': 0.0,
                'detected_scripts': []
            }
        
        # Check for mixed language (script analysis)
        scripts_found = self._detect_scripts(text)
        has_latin = self._has_latin_script(text)
        has_indian_script = len(scripts_found) > 0
        
        # Mixed language detection (e.g., Hinglish, Kanglish)
        is_mixed = has_latin and has_indian_script
        
        try:
            # Use langdetect for primary language detection
            detected_langs = detect_langs(text)
            primary_lang = detected_langs[0]
            
            lang_code = primary_lang.lang
            confidence = primary_lang.prob
            
            # Map to supported languages
            if lang_code not in self.LANGUAGE_NAMES:
                # Default to English if unsupported language
                lang_code = 'en'
                confidence = 0.5
            
            # For mixed languages, adjust the language code based on script
            if is_mixed and scripts_found:
                # Determine primary Indian language from script
                script_lang_map = {
                    'devanagari': 'hi',  # Default to Hindi for Devanagari
                    'bengali': 'bn',
                    'gurmukhi': 'pa',
                    'gujarati': 'gu',
                    'tamil': 'ta',
                    'telugu': 'te',
                    'kannada': 'kn',
                    'malayalam': 'ml'
                }
                
                for script in scripts_found:
                    if script in script_lang_map:
                        lang_code = script_lang_map[script]
                        break
            
            return {
                'language_code': lang_code,
                'language_name': self.LANGUAGE_NAMES.get(lang_code, 'English'),
                'is_mixed': is_mixed,
                'confidence': confidence,
                'detected_scripts': scripts_found
            }
            
        except LangDetectException:
            # Fallback to English if detection fails
            return {
                'language_code': 'en',
                'language_name': 'English',
                'is_mixed': is_mixed,
                'confidence': 0.3,
                'detected_scripts': scripts_found
            }
    
    def _detect_scripts(self, text: str) -> list:
        """
        Detect Indian scripts present in the text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of detected script names
        """
        detected_scripts = []
        
        for char in text:
            code_point = ord(char)
            for script_name, (start, end) in self.SCRIPT_RANGES.items():
                if start <= code_point <= end:
                    if script_name not in detected_scripts:
                        detected_scripts.append(script_name)
        
        return detected_scripts
    
    def _has_latin_script(self, text: str) -> bool:
        """
        Check if text contains Latin script (English characters).
        
        Args:
            text: Input text to analyze
            
        Returns:
            True if Latin characters are found
        """
        # Check for English letters (a-z, A-Z)
        return bool(re.search(r'[a-zA-Z]', text))
