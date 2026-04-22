import edge_tts
import io

# Map languages to appropriate edge-tts voices
VOICES = {
    "en": "en-IN-NeerjaNeural", # Indian English
    "hi": "hi-IN-SwaraNeural",  # Hindi
    "ta": "ta-IN-PallaviNeural" # Tamil
}

async def generate_speech(text: str, language: str = "en") -> bytes:
    """Generates speech audio bytes from text using edge-tts."""
    voice = VOICES.get(language, VOICES["en"])
    communicate = edge_tts.Communicate(text, voice)
    
    audio_data = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.extend(chunk["data"])
            
    return bytes(audio_data)
