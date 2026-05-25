const StatusSection = ({ data, alertHistory }) => {
  const { status, confidence, duration, alert_count, session_time, drowsy_counter } = data;

  const isDrowsy = status === 'Drowsy';
  const statusClass = isDrowsy ? 'indicator alert' : 'indicator safe';

  return (
    <div className="metrics-grid">
      <div className="card status-card">
        <h2>Driver Status</h2>
        <div className={statusClass}>{status}</div>
      </div>

      <div className="card confidence-card">
        <h2>Detection Confidence</h2>
        <div className="progress-bar-container">
          <div
            className="progress-bar"
            style={{ width: `${confidence}%` }}
          ></div>
        </div>
        <div className="confidence-value">{confidence}%</div>
      </div>

      <div className="card info-card">
        <h2>Active Session</h2>
        <div className="confidence-value" style={{ color: 'var(--accent-primary)' }}>{session_time}s</div>
      </div>

      <div className="card info-card">
        <h2>Alert Count</h2>
        <div className="confidence-value" style={{ color: alert_count > 0 ? 'var(--accent-danger)' : 'var(--accent-secondary)' }}>
          {alert_count}
        </div>
      </div>

      <div className="card info-card">
        <h2>Last Alert Duration</h2>
        <div className="confidence-value" style={{ color: 'var(--accent-danger)' }}>{duration}s</div>
      </div>

      <div className="card history-panel">
        <h2>Recent Detection Log</h2>
        <div className="history-list">
          {alertHistory.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', padding: '1rem' }}>No detections recorded.</p>
          ) : (
            alertHistory.map((alert) => (
              <div key={alert.id} className="history-item">
                <span className="time">{alert.time}</span>
                <span className="tag">DETECTION</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default StatusSection;
