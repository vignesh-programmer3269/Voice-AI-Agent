import speech_recognition as sr
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0

recognizer = sr.Recognizer()

def transcribe_audio(audio_bytes: bytes) -> tuple[str, str]:
    """Transcribes raw PCM audio (16-bit, mono, 48kHz) and detects its language.
    Returns (text, language_code).
    """
    try:
        # Load raw PCM directly (48kHz, 2 bytes for 16-bit)
        audio_for_sr = sr.AudioData(audio_bytes, sample_rate=48000, sample_width=2)
        
        # Recognize using Google Web API
        text = recognizer.recognize_google(audio_for_sr)
        
        try:
            lang = detect(text)
            if lang not in ["en", "hi", "ta"]:
                lang = "en" # Fallback
        except:
            lang = "en"
            
        return text, lang
    except sr.UnknownValueError:
        print("STT Error: Google Speech Recognition could not understand audio")
        return "", "en"
    except sr.RequestError as e:
        print(f"STT Error: Could not request results from Google Speech Recognition service; {e}")
        return "", "en"
    except Exception as e:
        print(f"STT Error: {e}")
        return "", "en"
