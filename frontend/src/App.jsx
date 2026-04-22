import React, { useState } from 'react';
import VoiceAgent from './components/VoiceAgent';
import Appointments from './components/Appointments';
import DoctorsList from './components/DoctorsList';
import LatencyTracker from './components/LatencyTracker';
import './App.css';

function App() {
  const [metrics, setMetrics] = useState(null);

  return (
    <div className="telecall-dashboard">
      <div className="telecall-header">
        <h1>Voice AI Agent</h1>
        <p>Real-Time Multilingual Clinical Dashboard</p>
      </div>
      
      <div className="dashboard-grid">
        <div className="main-col">
          <div className="glass-panel interface-panel">
            <h2 className="panel-header">Telecall Interface</h2>
            <VoiceAgent onMetricsUpdate={setMetrics} />
          </div>
          
          <div className="glass-panel info-panel">
            <DoctorsList />
          </div>
        </div>
        
        <div className="side-col">
          <LatencyTracker metrics={metrics} />
          <Appointments />
        </div>
      </div>
    </div>
  );
}

export default App;
