import time
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import json

load_dotenv()

from services.stt import transcribe_audio
from services.tts import generate_speech
from agent.agent import get_agent_response
from memory.session import get_session, update_session
from scheduler.appointment import get_appointments

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "running"}


@app.get("/api/appointments/{patient_id}")
def api_get_appointments(patient_id: str):
    appointments = get_appointments(patient_id)
    return {"patient_id": patient_id, "appointments": appointments}


@app.get("/api/doctors")
def api_get_doctors():
    return {
        "doctors": [
            "Dr. Sharma (Cardiologist)",
            "Dr. Iyer (Dermatologist)",
            "Dr. Singh (Neurologist)",
            "Dr. Patel (Pediatrics)",
        ]
    }


@app.websocket("/ws/voice/{session_id}")
async def websocket_endpoint_voice(websocket: WebSocket, session_id: str):
    await websocket_endpoint(websocket, session_id)


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()

    greeting_text = (
        "Welcome to 2Care Clinic. How can I assist you with your appointments today?"
    )

    start_tts = time.perf_counter()
    audio_response = await generate_speech(greeting_text, "en")
    tts_latency = (time.perf_counter() - start_tts) * 1000

    # Initialize history
    history = [{"role": "model", "parts": [greeting_text]}]
    update_session(session_id, "history", history)

    await websocket.send_text(
        json.dumps(
            {
                "type": "metrics",
                "stt": 0,
                "llm": 0,
                "tts": round(tts_latency),
                "total": round(tts_latency),
            }
        )
    )
    await websocket.send_bytes(audio_response)

    try:
        while True:
            audio_bytes = await websocket.receive_bytes()

            stt_start = time.perf_counter()
            text, lang = transcribe_audio(audio_bytes)
            stt_end = time.perf_counter()
            stt_latency = (stt_end - stt_start) * 1000

            if not text.strip():
                # Fallback for silent chunks
                fallback_msg = (
                    "I'm sorry, I didn't quite catch that. Could you please repeat?"
                )
                if lang == "hi":
                    fallback_msg = "माफ़ कीजिये, मैं समझ नहीं पाया। क्या आप दोहरा सकते हैं?"
                if lang == "ta":
                    fallback_msg = "மன்னிக்கவும், எனக்கு புரியவில்லை. மீண்டும் சொல்ல முடியுமா?"

                audio_response = await generate_speech(fallback_msg, lang)
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "metrics",
                            "stt": round(stt_latency),
                            "llm": 0,
                            "tts": 100,
                            "total": round(stt_latency + 100),
                        }
                    )
                )
                await websocket.send_bytes(audio_response)
                continue

            update_session(session_id, "language", lang)
            session = get_session(session_id)
            patient_name = session.get("patient_name") or "Valued Patient"

            llm_start = time.perf_counter()
            llm_text, updated_history = get_agent_response(
                text, history, lang, patient_name
            )
            llm_end = time.perf_counter()
            llm_latency = (llm_end - llm_start) * 1000

            history = updated_history
            update_session(session_id, "history", history)

            tts_start = time.perf_counter()
            audio_response = await generate_speech(llm_text, lang)
            tts_end = time.perf_counter()
            tts_latency = (tts_end - tts_start) * 1000

            total_latency = stt_latency + llm_latency + tts_latency
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "metrics",
                        "stt": round(stt_latency),
                        "llm": round(llm_latency),
                        "tts": round(tts_latency),
                        "total": round(total_latency),
                    }
                )
            )

            await websocket.send_bytes(audio_response)

    except WebSocketDisconnect:
        print(f"Client {session_id} disconnected")
