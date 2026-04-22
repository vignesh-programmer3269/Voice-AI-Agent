import React, { useState, useEffect } from "react";

export default function Appointments() {
  const [appointments, setAppointments] = useState([]);
  const patientId = "patient_001"; // Hardcoded for demo

  const fetchData = async () => {
    try {
      const respApt = await fetch(
        `http://localhost:8000/api/appointments/${patientId}`,
      );
      if (respApt.ok) {
        const data = await respApt.json();
        setAppointments(data.appointments);
      }
    } catch (err) {
      console.error("Fetch error:", err);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Auto refresh every 5s
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <div className="panel-container">
        <h3 className="panel-title">Active Appointments</h3>
        <div className="table-responsive">
          <table className="appointments-table">
            <thead>
              <tr>
                <th>Doctor</th>
                <th>Date</th>
                <th>Time</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {appointments.length === 0 ? (
                <tr>
                  <td colSpan="4" className="empty-row">
                    No appointments found.
                  </td>
                </tr>
              ) : (
                appointments.map((apt, i) => (
                  <tr
                    key={i}
                    className={
                      apt.status === "Cancelled" ? "cancelled-row" : ""
                    }
                  >
                    <td>{apt.doctor}</td>
                    <td>{apt.date}</td>
                    <td>{apt.time}</td>
                    <td>
                      <span
                        className={`status-badge ${apt.status.toLowerCase()}`}
                      >
                        {apt.status}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
