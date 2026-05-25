const AlertOverlay = ({ isDrowsy }) => {
  if (!isDrowsy) return null;

  return (
    <div className="alert-overlay">
      <div className="alert-box">
        <h2>⚠️ DROWSY ⚠️</h2>
        <p style={{ color: '#ff0044', fontSize: '1.2rem', letterSpacing: '2px' }}>
          WAKE UP IMMEDIATELY
        </p>
      </div>
    </div>
  );
};

export default AlertOverlay;
