// DesiFriend AI - Chat Functionality
// Handles text messaging, API communication, and UI updates

// Configuration
const API_BASE_URL = 'http://localhost:8000';

// State management
let sessionId = localStorage.getItem('desifriend_session_id') || null;
let isProcessing = false;

// DOM elements
const messagesArea = document.getElementById('messagesArea');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const languageIndicator = document.getElementById('detectedLanguage');
const audioPlayer = document.getElementById('audioPlayer');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    scrollToBottom();
});

// Event listeners
function setupEventListeners() {
    sendButton.addEventListener('click', handleSendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });
}

// Handle send message
async function handleSendMessage() {
    const message = messageInput.value.trim();
    
    if (!message || isProcessing) {
        return;
    }
    
    // Clear input
    messageInput.value = '';
    isProcessing = true;
    
    // Display user message
    displayUserMessage(message);
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Send message to API
        const response = await sendMessage(message);
        
        // Remove typing indicator
        removeTypingIndicator();
        
        // Display AI response
        displayAIMessage(response);
        
        // Auto-play audio if available
        if (response.audio_url) {
            playAudio(response.audio_url);
        }
        
        // Update language indicator
        updateLanguageIndicator(response.detected_language.language_name);
        
        // Store session ID
        if (response.session_id) {
            sessionId = response.session_id;
            localStorage.setItem('desifriend_session_id', sessionId);
        }
        
    } catch (error) {
        removeTypingIndicator();
        displayErrorMessage('Sorry, something went wrong. Please try again.');
        console.error('Error:', error);
    } finally {
        isProcessing = false;
        messageInput.focus();
    }
}

// Send message to API
async function sendMessage(message) {
    const requestBody = {
        message: message,
        session_id: sessionId,
        device_locale: navigator.language || 'en-US',
        voice_gender: 'female'
    };
    
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
    });
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
}

// Display user message
function displayUserMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    
    const text = document.createElement('p');
    text.textContent = message;
    
    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = getCurrentTime();
    
    bubble.appendChild(text);
    bubble.appendChild(time);
    messageDiv.appendChild(bubble);
    messagesArea.appendChild(messageDiv);
    
    scrollToBottom();
}

// Display AI message
function displayAIMessage(response) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ai-message';
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    
    const text = document.createElement('p');
    text.textContent = response.ai_response;
    
    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = getCurrentTime();
    
    bubble.appendChild(text);
    bubble.appendChild(time);
    
    // Add audio button if audio URL is available
    if (response.audio_url) {
        const audioButton = document.createElement('button');
        audioButton.className = 'audio-button';
        audioButton.innerHTML = '🔊 Play Audio';
        audioButton.onclick = () => playAudio(response.audio_url);
        bubble.appendChild(audioButton);
    }
    
    messageDiv.appendChild(bubble);
    messagesArea.appendChild(messageDiv);
    
    scrollToBottom();
}

// Display error message
function displayErrorMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ai-message';
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.style.backgroundColor = '#FFEBEE';
    
    const text = document.createElement('p');
    text.textContent = message;
    text.style.color = '#C62828';
    
    bubble.appendChild(text);
    messageDiv.appendChild(bubble);
    messagesArea.appendChild(messageDiv);
    
    scrollToBottom();
}

// Show typing indicator
function showTypingIndicator() {
    const template = document.getElementById('typingIndicatorTemplate');
    const indicator = template.content.cloneNode(true);
    indicator.firstElementChild.id = 'typingIndicator';
    messagesArea.appendChild(indicator);
    scrollToBottom();
}

// Remove typing indicator
function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

// Play audio
function playAudio(audioUrl) {
    const fullUrl = `${API_BASE_URL}${audioUrl}`;
    audioPlayer.src = fullUrl;
    audioPlayer.play().catch(error => {
        console.error('Error playing audio:', error);
    });
}

// Update language indicator
function updateLanguageIndicator(languageName) {
    languageIndicator.textContent = languageName;
}

// Scroll to bottom
function scrollToBottom() {
    setTimeout(() => {
        messagesArea.parentElement.scrollTop = messagesArea.parentElement.scrollHeight;
    }, 100);
}

// Get current time
function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
    });
}
