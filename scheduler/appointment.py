import sqlite3
import datetime

DB_FILE = "appointments.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS appointments
                 (id INTEGER PRIMARY KEY, patient_name TEXT, doctor TEXT, date TEXT, time TEXT, status TEXT)''')
    conn.commit()
    conn.close()

def check_availability(doctor: str, date: str, time: str) -> bool:
    """
    Checks if a doctor is available at the given date and time.
    :param doctor: Full name of the doctor (e.g. 'Dr. Sharma').
    :param date: The scheduled date (e.g. '2026-05-01' or 'tomorrow').
    :param time: The scheduled time (e.g. '10:00 AM').
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM appointments WHERE doctor=? AND date=? AND time=? AND status!='Cancelled'", (doctor, date, time))
    conflict = c.fetchone()
    conn.close()
    return conflict is None

def book_appointment(patient_name: str, doctor: str, date: str, time: str) -> str:
    """
    Books a new clinical appointment. Use this only when you have doc name, date, and time.
    :param patient_name: The name of the patient booking.
    :param doctor: The name of the doctor to book with.
    :param date: The date for the appointment.
    :param time: The specific time for the appointment.
    """
    if not check_availability(doctor, date, time):
        return "Slot is already booked. Please choose another time."
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO appointments (patient_name, doctor, date, time, status) VALUES (?, ?, ?, ?, ?)",
              (patient_name, doctor, date, time, "Booked"))
    conn.commit()
    conn.close()
    return f"SUCCESS: Appointment booked with {doctor} on {date} at {time}."

def get_appointments(patient_name: str) -> list:
    """Gets all appointments for a patient."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM appointments WHERE patient_name=?", (patient_name,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def cancel_appointment(patient_name: str, doctor: str, date: str, time: str) -> str:
    """Cancels an existing appointment."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE appointments SET status='Cancelled' WHERE patient_name=? AND doctor=? AND date=? AND time=?",
              (patient_name, doctor, date, time))
    changed = c.rowcount
    conn.commit()
    conn.close()
    if changed > 0:
        return "Appointment cancelled successfully."
    return "Appointment not found."

def reschedule_appointment(patient_name: str, doctor: str, old_date: str, old_time: str, new_date: str, new_time: str) -> str:
    """Reschedules an appointment to a new date and time."""
    if not check_availability(doctor, new_date, new_time):
        return f"New slot on {new_date} at {new_time} is not available."
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # verify old appointment exists
    c.execute("SELECT * FROM appointments WHERE patient_name=? AND doctor=? AND date=? AND time=? AND status!='Cancelled'", 
              (patient_name, doctor, old_date, old_time))
    if not c.fetchone():
        conn.close()
        return "Original appointment not found."

    c.execute("UPDATE appointments SET date=?, time=? WHERE patient_name=? AND doctor=? AND date=? AND time=?",
              (new_date, new_time, patient_name, doctor, old_date, old_time))
    conn.commit()
    conn.close()
    return "Appointment rescheduled successfully."

# Initialize the db on module load
init_db()
