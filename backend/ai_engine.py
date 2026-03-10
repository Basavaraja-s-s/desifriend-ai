# DesiFriend AI - AI Engine Module
"""
AI Engine module for DesiFriend AI.
Handles conversation with AI model using Groq API.
Generates casual, friendly responses in multiple languages.
"""

from groq import Groq
from typing import List, Dict, Optional
import os


class AIEngine:
    """
    AI Engine for generating conversational responses.
    Uses Groq LLM models with casual, friendly tone.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize the AI Engine.
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            model: Groq model to use (default: llama-3.3-70b-versatile)
        """
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        self.model = model
        self.client = Groq(api_key=self.api_key)
        self.temperature = 0.7  # Natural variation in responses
        
        # System prompt for casual, friendly tone
        self.system_prompt = """You are DesiFriend AI, a warm and friendly AI companion. 
Your personality:
- Talk like a casual friend, not a formal assistant
- Be warm, supportive, and relatable
- Use natural, conversational language
- Avoid robotic or overly formal phrasing
- Show empathy and understanding
- Keep responses concise but engaging
- Adapt your tone to match the user's language and culture

When responding in Indian languages:
- Use culturally appropriate expressions and references
- Match the formality level of the user's message
- For mixed languages (like Hinglish), naturally blend both languages
- Be respectful of cultural nuances

Remember: You're a friend having a conversation, not an AI providing information."""
    
    def generate_response(self, user_message: str, 
                         conversation_history: Optional[List[Dict]] = None,
                         language_code: Optional[str] = None,
                         language_name: Optional[str] = None) -> str:
        """
        Generate AI response based on user message and conversation context.
        
        Args:
            user_message: The user's input message
            conversation_history: Previous messages in format [{'role': 'user'|'assistant', 'content': str}]
            language_code: Detected language code (e.g., 'hi', 'en')
            language_name: Detected language name (e.g., 'Hindi', 'English')
            
        Returns:
            AI-generated response text
        """
        # Build messages for API call
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add language-specific instruction if not English
        if language_code and language_code != 'en':
            language_instruction = f"\n\nIMPORTANT: The user is communicating in {language_name}. You MUST respond in {language_name} to match their language."
            messages[0]["content"] += language_instruction
        
        # Add conversation history (last 10 messages)
        if conversation_history:
            messages.extend(conversation_history[-10:])
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=500  # Limit response length for mobile optimization
            )
            
            # Extract response text
            ai_response = response.choices[0].message.content.strip()
            return ai_response
            
        except Exception as e:
            # Fallback response on error
            error_responses = {
                'hi': 'माफ़ करें, मुझे कुछ समस्या हो रही है। कृपया फिर से कोशिश करें।',
                'en': "Sorry, I'm having some trouble right now. Please try again.",
                'ta': 'மன்னிக்கவும், எனக்கு சில சிக்கல் உள்ளது. மீண்டும் முயற்சிக்கவும்.',
                'te': 'క్షమించండి, నాకు కొంత సమస్య ఉంది. దయచేసి మళ్లీ ప్రయత్నించండి.',
                'kn': 'ಕ್ಷಮಿಸಿ, ನನಗೆ ಸ್ವಲ್ಪ ತೊಂದರೆ ಆಗುತ್ತಿದೆ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.',
                'ml': 'ക്ഷമിക്കണം, എനിക്ക് കുറച്ച് പ്രശ്നമുണ്ട്. ദയവായി വീണ്ടും ശ്രമിക്കുക.',
                'bn': 'দুঃখিত, আমার কিছু সমস্যা হচ্ছে। অনুগ্রহ করে আবার চেষ্টা করুন।',
                'mr': 'माफ करा, मला काही अडचण येत आहे. कृपया पुन्हा प्रयत्न करा.',
                'gu': 'માફ કરશો, મને થોડી સમસ્યા છે. કૃપા કરીને ફરી પ્રયાસ કરો.',
                'pa': 'ਮਾਫ਼ ਕਰਨਾ, ਮੈਨੂੰ ਕੁਝ ਸਮੱਸਿਆ ਹੋ ਰਹੀ ਹੈ। ਕਿਰਪਾ ਕਰਕੇ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।'
            }
            
            return error_responses.get(language_code, error_responses['en'])
    
    def set_temperature(self, temperature: float):
        """
        Set the temperature for response generation.
        
        Args:
            temperature: Value between 0.0 (deterministic) and 1.0 (creative)
        """
        self.temperature = max(0.0, min(1.0, temperature))
    
    def set_model(self, model: str):
        """
        Change the Groq model being used.
        
        Args:
            model: Model name (e.g., 'llama-3.3-70b-versatile', 'mixtral-8x7b-32768')
        """
        self.model = model
