# Simple in-memory storage to satisfy requirements minimally.

sessions = {}

def get_session(session_id: str) -> dict:
    """Retrieve session context, creating if it doesnt exist."""
    if session_id not in sessions:
        sessions[session_id] = {
            "history": [],
            "patient_name": None,
            "language": "en"
        }
    return sessions[session_id]

def update_session(session_id: str, key: str, value):
    """Update a specific key in the session."""
    session = get_session(session_id)
    session[key] = value

def add_message(session_id: str, role: str, content: str):
    """Add a message to the session history."""
    session = get_session(session_id)
    session["history"].append({"role": role, "content": content})
