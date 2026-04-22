import React, { useState, useEffect } from 'react';

export default function DoctorsList() {
  const [doctors, setDoctors] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/api/doctors')
      .then(res => res.json())
      .then(data => setDoctors(data.doctors))
      .catch(err => console.error("Doctors fetch failed:", err));
  }, []);

  return (
    <div className="panel-container">
      <h3 className="panel-title">Available Doctors</h3>
      <div className="doctors-grid">
        {doctors.map((doc, i) => {
          const [name, specialty] = doc.split(' (');
          return (
            <div key={i} className="doctor-card">
              <div className="doctor-avatar">
                {name.split(' ')[1]?.[0] || 'D'}
              </div>
              <div className="doctor-info">
                <div className="doc-name">{name}</div>
                <div className="doc-spec">{specialty?.replace(')', '') || 'Specialist'}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
