# DesiFriend AI - Context Manager Module
"""
Context management module for DesiFriend AI.
Manages conversation history and session state for maintaining context.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import uuid


class ContextManager:
    """
    Manages conversation context and session state.
    Stores message history in memory with session expiration.
    """
    
    def __init__(self, session_timeout_minutes: int = 30, max_history: int = 10):
        """
        Initialize the Context Manager.
        
        Args:
            session_timeout_minutes: Minutes before a session expires
            max_history: Maximum number of messages to keep per session
        """
        self.sessions: Dict[str, Dict] = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self.max_history = max_history
    
    def create_session(self) -> str:
        """
        Create a new session.
        
        Returns:
            Session ID (UUID string)
        """
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'messages': [],
            'created_at': datetime.now(),
            'last_activity': datetime.now()
        }
        return session_id
    
    def add_message(self, session_id: str, role: str, content: str, 
                   language: Optional[str] = None) -> bool:
        """
        Add a message to the session history.
        
        Args:
            session_id: Session identifier
            role: Message role ('user' or 'assistant')
            content: Message content
            language: Detected language (optional)
            
        Returns:
            True if message was added, False if session doesn't exist
        """
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        
        # Add message to history
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'language': language
        }
        session['messages'].append(message)
        
        # Limit history to max_history messages
        if len(session['messages']) > self.max_history:
            session['messages'] = session['messages'][-self.max_history:]
        
        # Update last activity
        session['last_activity'] = datetime.now()
        
        return True
    
    def get_history(self, session_id: str, limit: Optional[int] = None) -> List[Dict]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages to return (None for all)
            
        Returns:
            List of message dictionaries, or empty list if session doesn't exist
        """
        if session_id not in self.sessions:
            return []
        
        messages = self.sessions[session_id]['messages']
        
        if limit:
            return messages[-limit:]
        
        return messages
    
    def get_conversation_context(self, session_id: str) -> List[Dict]:
        """
        Get conversation context formatted for AI model.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of messages in format: [{'role': 'user'|'assistant', 'content': str}]
        """
        messages = self.get_history(session_id)
        
        # Format for AI model (remove timestamp and language fields)
        return [
            {'role': msg['role'], 'content': msg['content']}
            for msg in messages
        ]
    
    def clear_session(self, session_id: str) -> bool:
        """
        Clear a session and remove all its data.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session was cleared, False if session doesn't exist
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def session_exists(self, session_id: str) -> bool:
        """
        Check if a session exists.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session exists
        """
        return session_id in self.sessions
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove expired sessions based on last activity time.
        
        Returns:
            Number of sessions cleaned up
        """
        now = datetime.now()
        expired_sessions = []
        
        for session_id, session_data in self.sessions.items():
            last_activity = session_data['last_activity']
            if now - last_activity > self.session_timeout:
                expired_sessions.append(session_id)
        
        # Remove expired sessions
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        return len(expired_sessions)
    
    def get_session_count(self) -> int:
        """
        Get the total number of active sessions.
        
        Returns:
            Number of active sessions
        """
        return len(self.sessions)
