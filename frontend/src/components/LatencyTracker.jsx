import React from 'react';

export default function LatencyTracker({ metrics }) {
  if (!metrics) {
    return (
      <div className="panel-container">
        <h3 className="panel-title">System Latency</h3>
        <p className="empty-row" style={{padding: "2rem"}}>Awaiting telemetry...</p>
      </div>
    );
  }

  const targetMet = metrics.total < 450;

  return (
    <div className="panel-container">
      <h3 className="panel-title">
        Processing Time
        <span className={`target-badge ${targetMet ? "success" : "danger"}`} style={{fontSize: '0.7rem'}}>
            {targetMet ? "TARGET MET" : "OVER TARGET"}
        </span>
      </h3>
      
      <div className="latency-table-wrapper">
        <table className="latency-metrics-table">
          <thead>
            <tr>
              <th>Stage</th>
              <th>Time</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Speech recognition</td>
              <td>{metrics.stt} ms</td>
            </tr>
            <tr>
              <td>Agent reasoning</td>
              <td>{metrics.llm} ms</td>
            </tr>
            <tr>
              <td>Speech synthesis</td>
              <td>{metrics.tts} ms</td>
            </tr>
            <tr className="total-row">
              <td><strong>Total target:</strong></td>
              <td><strong>{metrics.total} ms</strong></td>
            </tr>
          </tbody>
        </table>
      </div>

      <div className="target-note">
        <strong>&lt; 450 ms</strong>
        <p>Log metrics in the system.</p>
      </div>
    </div>
  );
}
