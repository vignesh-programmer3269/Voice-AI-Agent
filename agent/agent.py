import json
import os
import time
import google.generativeai as genai
from scheduler.appointment import (
    check_availability,
    book_appointment,
    cancel_appointment,
    reschedule_appointment,
)

if "GEMINI_API_KEY" not in os.environ:
    print("Critical: GEMINI_API_KEY not set.")

genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))

# Agent configuration
SYSTEM_INSTRUCTIONS = """You are a professional appointment booking agent for '2Care Clinic'.
You manage clinical appointments including booking, cancellations, and status checks.

Clinical Directory:
- Dr. Sharma (Cardiologist)
- Dr. Iyer (Dermatologist)
- Dr. Singh (Neurologist)
- Dr. Patel (Pediatrics)

Operational Rules:
1. When a patient specifies a doctor and time, use 'book_appointment' immediately.
2. Use the provided [Patient Name] from context; do not ask for it.
3. Respond exclusively in the requested language (English, Hindi, or Tamil).
4. Maintain a concise, professional tone suitable for a healthcare environment.
"""

tools = [
    check_availability,
    book_appointment,
    cancel_appointment,
    reschedule_appointment,
]


def get_agent_response(
    user_text: str,
    session_history: list,
    user_lang: str = "en",
    patient_name: str = "Valued Patient",
) -> tuple[str, list]:
    # Maintain low latency by limiting context history
    MAX_HISTORY = 10
    if len(session_history) > MAX_HISTORY:
        session_history = session_history[-MAX_HISTORY:]

    lang_map = {"en": "English", "hi": "Hindi", "ta": "Tamil"}
    target_lang = lang_map.get(user_lang, "English")

    context_instruction = (
        f"{SYSTEM_INSTRUCTIONS}\n\n" f"[Patient Name]: {patient_name}\n"
    )

    try:
        model = genai.GenerativeModel(
            model_name="gemini-flash-latest",
            tools=tools,
            system_instruction=context_instruction,
        )

        chat = model.start_chat(history=session_history)

        # Format input message with language constraint
        message = (
            f"User Message: {user_text}\n\nLanguage Policy: Respond in {target_lang}."
        )
        response = chat.send_message(message)

        # Process automated tool execution loop
        while True:
            function_call = None
            if hasattr(response, "parts") and response.parts:
                for part in response.parts:
                    if hasattr(part, "function_call") and part.function_call:
                        function_call = part.function_call
                        break

            if not function_call:
                break

            func_name = function_call.name
            func_args = {k: v for k, v in function_call.args.items()}

            # Execute tool logic
            if func_name == "book_appointment":
                result = book_appointment(**func_args)
            elif func_name == "check_availability":
                result = check_availability(**func_args)
            elif func_name == "cancel_appointment":
                result = cancel_appointment(**func_args)
            elif func_name == "reschedule_appointment":
                result = reschedule_appointment(**func_args)
            else:
                result = "Unsupported tool call."

            # Resume conversation with tool output
            response = chat.send_message(
                genai.types.Part.from_function_response(
                    name=func_name, response={"result": result}
                )
            )

        updated_history = list(chat.history)
        return response.text, updated_history

    except Exception as e:
        print(f"Error processing agent request: {e}")
        return (
            "I am currently experiencing service interruptions. Please try again shortly.",
            session_history,
        )
