# DesiFriend AI

A full-stack AI companion application that provides conversational interactions in multiple Indian languages with Indian-accent voice responses.

## Features

- **Multi-Language Support**: Hindi, Kannada, Tamil, Telugu, Malayalam, Bengali, Marathi, Gujarati, Punjabi, and English
- **Automatic Language Detection**: Detects user language automatically, including mixed languages (Hinglish, Kanglish)
- **Voice Input/Output**: Speak to the AI and hear responses with Indian accent voices
- **Conversation Context**: Maintains conversation history for natural, continuous chat
- **Mobile-Friendly**: WhatsApp-inspired responsive design optimized for mobile devices
- **Country-Based Accents**: Adapts voice accent based on user location (India, USA, UK)

## Tech Stack

**Backend:**
- Python 3.11
- FastAPI
- OpenAI API (GPT-3.5/4 for chat, Whisper for STT, TTS for voice)
- Pydantic for data validation

**Frontend:**
- HTML5
- CSS3 (Mobile-first design)
- Vanilla JavaScript

## Prerequisites

- Python 3.11 or higher
- OpenAI API key
- Modern web browser with microphone support (for voice features)

## Local Development Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd desifriend-ai
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the `backend` directory:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional - Server Configuration
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development

# Optional - Session Configuration
SESSION_TIMEOUT_MINUTES=30
MAX_CONVERSATION_HISTORY=10

# Optional - Audio Configuration
AUDIO_OUTPUT_DIR=audio_files
AUDIO_FORMAT=mp3
AUDIO_COMPRESSION_QUALITY=128

# Optional - CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 4. Run the Backend

```bash
# From backend directory
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 5. Run the Frontend

Open `frontend/index.html` in your web browser, or serve it using a simple HTTP server:

```bash
# Using Python
cd frontend
python -m http.server 3000

# Or using Node.js
npx serve frontend -p 3000
```

Access the application at `http://localhost:3000`

## API Endpoints

### POST /api/chat
Text-based chat endpoint.

**Request:**
```json
{
  "message": "Hello, how are you?",
  "session_id": "optional-session-id",
  "device_locale": "en-IN",
  "voice_gender": "female"
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "user_message": "Hello, how are you?",
  "ai_response": "Hi! I'm doing great, thanks for asking!",
  "audio_url": "/audio/filename.mp3",
  "detected_language": {
    "language_code": "en",
    "language_name": "English",
    "is_mixed": false,
    "confidence": 0.99
  },
  "detected_country": "IN"
}
```

### POST /api/voice-chat
Voice-based chat endpoint (multipart/form-data).

**Request:**
- `audio`: Audio file (WebM, MP3, WAV)
- `session_id`: Optional session ID
- `device_locale`: Optional device locale
- `voice_gender`: Optional voice gender preference

**Response:** Same as /api/chat with additional `transcribed_text` field

### GET /api/health
Health check endpoint.

## Deployment

### Deploy to Railway

1. Create a new project on [Railway](https://railway.app)
2. Connect your GitHub repository
3. Add environment variables in Railway dashboard:
   - `OPENAI_API_KEY`
   - Other optional variables from `.env.example`
4. Railway will automatically detect and deploy using `Procfile`

### Deploy to Render

1. Create a new Web Service on [Render](https://render.com)
2. Connect your GitHub repository
3. Configure:
   - **Build Command:** `cd backend && pip install -r requirements.txt`
   - **Start Command:** `cd backend && uvicorn app:app --host 0.0.0.0 --port $PORT`
4. Add environment variables in Render dashboard:
   - `OPENAI_API_KEY`
   - Other optional variables from `.env.example`

## Project Structure

```
desifriend-ai/
├── backend/
│   ├── app.py                 # Main FastAPI application
│   ├── models.py              # Pydantic data models
│   ├── ai_engine.py           # AI conversation engine
│   ├── language_detector.py   # Language detection module
│   ├── country_detector.py    # Country detection module
│   ├── context_manager.py     # Conversation context manager
│   ├── speech_to_text.py      # Speech-to-text module
│   ├── text_to_speech.py      # Text-to-speech module
│   ├── config.py              # Configuration management
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Environment variables template
├── frontend/
│   ├── index.html             # Main HTML interface
│   ├── style.css              # Stylesheet
│   ├── chat.js                # Chat functionality
│   └── voice.js               # Voice functionality
├── Procfile                   # Railway/Render deployment config
├── runtime.txt                # Python version specification
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## Usage

1. **Text Chat**: Type your message in any supported language and press Send or Enter
2. **Voice Chat**: Click the microphone button, speak your message, then click again to stop recording
3. **Play Audio**: Click the "🔊 Play Audio" button on AI responses to hear the voice output
4. **Language Detection**: The detected language is displayed in the top-right corner

## Supported Languages

- English
- Hindi (हिन्दी)
- Kannada (ಕನ್ನಡ)
- Tamil (தமிழ்)
- Telugu (తెలుగు)
- Malayalam (മലയാളം)
- Bengali (বাংলা)
- Marathi (मराठी)
- Gujarati (ગુજરાતી)
- Punjabi (ਪੰਜਾਬੀ)
- Mixed languages (Hinglish, Kanglish, etc.)

## Troubleshooting

### Backend Issues

**Error: "Missing required environment variables"**
- Ensure `OPENAI_API_KEY` is set in your `.env` file

**Error: "Module not found"**
- Run `pip install -r requirements.txt` in the backend directory

### Frontend Issues

**Error: "Failed to fetch"**
- Ensure the backend is running on `http://localhost:8000`
- Check CORS settings in backend `.env` file

**Microphone not working**
- Grant microphone permissions in your browser
- Use HTTPS in production (required for microphone access)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Acknowledgments

- OpenAI for GPT, Whisper, and TTS APIs
- FastAPI for the excellent web framework
- The open-source community for various libraries used in this project
