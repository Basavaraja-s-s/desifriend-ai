// DesiFriend AI - Voice Functionality
// Handles voice recording, speech-to-text, and audio playback

// Configuration
const API_BASE_URL = 'http://localhost:8000';

// State
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

// DOM elements
const micButton = document.getElementById('micButton');
const recordingIndicator = document.getElementById('recordingIndicator');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupVoiceEventListeners();
});

// Event listeners
function setupVoiceEventListeners() {
    micButton.addEventListener('click', toggleRecording);
}

// Toggle recording
async function toggleRecording() {
    if (isRecording) {
        stopRecording();
    } else {
        await startRecording();
    }
}

// Start recording
async function startRecording() {
    try {
        // Request microphone permission
        const stream = await requestMicrophonePermission();
        
        if (!stream) {
            alert('Microphone permission denied. Please allow microphone access to use voice input.');
            return;
        }
        
        // Initialize MediaRecorder
        audioChunks = [];
        mediaRecorder = new MediaRecorder(stream, {
            mimeType: 'audio/webm'
        });
        
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };
        
        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            await sendVoiceMessage(audioBlob);
            
            // Stop all tracks
            stream.getTracks().forEach(track => track.stop());
        };
        
        // Start recording
        mediaRecorder.start();
        isRecording = true;
        
        // Update UI
        micButton.classList.add('recording');
        recordingIndicator.style.display = 'flex';
        
    } catch (error) {
        console.error('Error starting recording:', error);
        alert('Failed to start recording. Please check your microphone.');
    }
}

// Stop recording
function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        
        // Update UI
        micButton.classList.remove('recording');
        recordingIndicator.style.display = 'none';
    }
}

// Request microphone permission
async function requestMicrophonePermission() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            audio: true 
        });
        return stream;
    } catch (error) {
        console.error('Microphone permission error:', error);
        return null;
    }
}

// Send voice message to API
async function sendVoiceMessage(audioBlob) {
    // Show processing state
    if (window.isProcessing) {
        return;
    }
    
    window.isProcessing = true;
    
    // Show typing indicator (from chat.js)
    if (typeof showTypingIndicator === 'function') {
        showTypingIndicator();
    }
    
    try {
        // Prepare form data
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');
        formData.append('session_id', sessionId || '');
        formData.append('device_locale', navigator.language || 'en-US');
        formData.append('voice_gender', 'female');
        
        // Send to API
        const response = await fetch(`${API_BASE_URL}/api/voice-chat`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Remove typing indicator
        if (typeof removeTypingIndicator === 'function') {
            removeTypingIndicator();
        }
        
        // Display transcribed text as user message
        if (data.transcribed_text && typeof displayUserMessage === 'function') {
            displayUserMessage(data.transcribed_text);
        }
        
        // Display AI response
        if (typeof displayAIMessage === 'function') {
            displayAIMessage(data);
        }
        
        // Auto-play audio response
        if (data.audio_url && typeof playAudio === 'function') {
            playAudio(data.audio_url);
        }
        
        // Update language indicator
        if (typeof updateLanguageIndicator === 'function') {
            updateLanguageIndicator(data.detected_language.language_name);
        }
        
        // Store session ID
        if (data.session_id) {
            sessionId = data.session_id;
            localStorage.setItem('desifriend_session_id', sessionId);
        }
        
    } catch (error) {
        if (typeof removeTypingIndicator === 'function') {
            removeTypingIndicator();
        }
        if (typeof displayErrorMessage === 'function') {
            displayErrorMessage('Sorry, voice processing failed. Please try again.');
        }
        console.error('Voice chat error:', error);
    } finally {
        window.isProcessing = false;
    }
}

// Play audio function (can be called from chat.js)
window.playAudio = function(audioUrl) {
    const audioPlayer = document.getElementById('audioPlayer');
    const fullUrl = `${API_BASE_URL}${audioUrl}`;
    audioPlayer.src = fullUrl;
    audioPlayer.play().catch(error => {
        console.error('Error playing audio:', error);
        alert('Failed to play audio. Please try again.');
    });
};
