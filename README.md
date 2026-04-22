# Voice AI Agent (2Care.ai)

Low-latency clinical appointment booking system with full-duplex interaction and multilingual support (English, Hindi, Tamil).

## Quick Start

### 1. Prerequisites

- Python 3.10+
- Node.js 18+
- [Gemini API Key](https://aistudio.google.com/)

### 2. Setup Environment Variables

```bash
Rename .env.example to .env
Add GEMINI_API_KEY="your_key" and OPENAI_API_KEY="your_key" to .env file

```

### 3. Installation

```bash
# Backend
pip install -r requirements.txt

python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

uvicorn backend.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

Access dashboard at `http://localhost:5173`.

## Architecture

- **Frontend**: React/Vite, Web Audio API (VAD), WebSockets.
- **Backend**: FastAPI, SQLite.
- **Pipeline**:
  - **STT**: Google SpeechRecognition.
  - **LLM**: Gemini 1.5 Flash (Function Calling).
  - **TTS**: Edge-TTS (Regional neural voices).

## System Design

- **Memory**: Session-based with 10-turn truncation for <500ms reasoning latency.
- **Database**: SQLite for persistent appointment state.
- **Concurrency**: Full-duplex WebSocket stream allowing barge-in/interruptions.

## Latency Metrics (Target: < 1.5s total)

| Stage         | Avg. Time     | Tech              |
| :------------ | :------------ | :---------------- |
| Transcription | 800ms - 1.2s  | Google Speech API |
| Reasoning     | 400ms - 600ms | Gemini 1.5 Flash  |
| Synthesis     | 300ms - 400ms | Edge TTS          |

## Technical Decisions

- **Gemini Flash**: Prioritized over Pro for token-generation speed.
- **Client-side VAD**: Reduced server processing overhead.
- **History Truncation**: Prevents context-window bloat and latency spikes.

## Known Limitations

- Background noise can trigger false-positive barge-ins.
- SQLite used for demonstration; production may require PostgreSQL.
- Requires stable internet for cloud-based STT/LLM components.

## Project Structure

```text
├── agent/            # Logic & tool calling
├── backend/          # API & WebSocket handlers
├── frontend/         # React Dashboard
├── scheduler/        # Database & Business logic
├── services/         # STT/TTS modules
└── requirements.txt  # Dependencies
```
