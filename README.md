# Real-Time Multilingual Voice AI Agent (2Care.ai)

A professional, low-latency Voice AI Agent designed for clinical appointment booking. The system features full-duplex "Telecall" style interaction, native multilingual support (English, Hindi, Tamil), and a real-time analytics dashboard.

## 🚀 Key Features

- **Continuous Telecall Flow**: Seamless barge-in capabilities (interrupt the agent any time).
- **Multilingual Intelligence**: Native reasoning and responses in English, Hindi, and Tamil.
- **Appointment Tool Calling**: Automated scheduling, cancellation, and availability checks.
- **Premium Dashboard**: Live latency tracking, active appointment monitoring, and doctor directory.
- **Optimized Latency**: Targeted < 1.5s total processing time with 10-turn history truncation.

---

## 🛠 Setup Instructions

### 1. Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **Gemini API Key**: Obtain from [Google AI Studio](https://aistudio.google.com/).

### 2. Backend Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set Environment Variables
# Windows (PowerShell):
$env:GEMINI_API_KEY="your_api_key_here"
# Linux/Mac:
export GEMINI_API_KEY="your_api_key_here"

# Run the server
python -m uvicorn backend.main:app --reload
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Navigate to `http://localhost:5173`.

---

## 🏗 Architecture Explanation

The system follows a decoupled **Client-Server Architecture** optimized for real-time streaming:

1.  **Frontend (React/Vite)**:
    - Handles low-level VAD (Voice Activity Detection) using Web Audio API (RMS energy analysis).
    - Manages full-duplex WebSocket communication for raw PCM audio blocks and JSON telemetry.
2.  **Backend (FastAPI)**:
    - **STT Layer**: Uses `SpeechRecognition` (Google engine) to transcribe user intent and detect language.
    - **Agent Layer (Gemini 1.5 Flash)**: Acts as the "Brain." Uses Function Calling to interact with the SQLite clinical database.
    - **TTS Layer (Edge-TTS)**: High-quality synthesis with regional voice mapping (e.g., Google's Neural voices for Hindi/Tamil).
    - **Session Manager**: Maintains thread-safe history and patient context.

---

## 🧠 Memory Design

- **Short-Term Memory**: The agent uses a `session_history` list passed to Gemini's `start_chat` method.
- **Latency Optimization (Truncation)**: To maintain sub-second reasoning times, the system automatically **truncates history to the last 10 turns**. This prevents context-window bloat while retaining enough context for appointment scheduling.
- **Persistence**: While currently in-memory (per session), the database uses **SQLite** for final appointment state.

---

## ⏱ Latency Breakdown (Target: < 450ms Reasoning)

| Stage                  | Avg. Latency  | Technology           |
| :--------------------- | :------------ | :------------------- |
| **Speech Recognition** | 800ms - 1.5s  | Google Speech API    |
| **Agent Reasoning**    | 400ms - 700ms | Gemini 1.5 Flash     |
| **Speech Synthesis**   | 300ms - 500ms | Edge TTS (Streaming) |
| **Total Turnaround**   | ~1.5s - 2.5s  | (End-to-End)         |

---

## ⚖️ Trade-offs

1.  **Google STT vs Whisper**: I used Google SpeechRecognition for its robust multilingual detection out-of-the-box, though OpenAI Whisper (Local) would offer lower latency at the cost of higher CPU/GPU usage.
2.  **LLM Selection**: Gemini 1.5 Flash was chosen over Pro specifically for **speed**. The Flash model offers significantly lower tokens-per-second latency, which is critical for a "telecall" feel.
3.  **Client-Side VAD**: Performing VAD on the browser reduces server load and network traffic, but makes the system sensitive to the user's specific microphone noise floor settings.

---

## ⚠️ Known Limitations

- **Legacy SDK**: Currently uses the `google-generativeai` package; a migration to the newer `google-genai` package is recommended for future-proofing.
- **Background Noise**: In very noisy environments, the RMS-based VAD may trigger false positive "Barge-ins," interrupting the agent prematurely.
- **Database Scope**: The current SQLite schema is a simplified demonstration for clinical scheduling and lacks complex recurring appointment logic.

---

## 📂 Project Structure

```text
├── agent/            # Gemini reasoning & tool calling
├── backend/          # FastAPI server & WebSocket handlers
├── frontend/         # React (Vite) application
├── scheduler/        # SQLite Appointment DB & Logic
├── services/         # STT and TTS implementation
└── requirements.txt  # Python dependencies
```
