import { useState, useEffect, useRef } from 'react'
import VideoFeed from './components/VideoFeed'
import StatusSection from './components/StatusSection'
import AlertOverlay from './components/AlertOverlay'
import './index.css'

function App() {
  const [data, setData] = useState({
    status: 'Waiting...',
    confidence: 0,
    is_drowsy: false,
    duration: 0,
    alert_count: 0,
    session_time: 0,
    drowsy_counter: 0
  })

  const [alertHistory, setAlertHistory] = useState([])
  const prevAlertCount = useRef(0)

  useEffect(() => {
    const fetchPrediction = async () => {
      try {
        const response = await fetch('/predict')
        const json = await response.json()
        setData(json)

        // Add to history if alert count increased
        if (json.alert_count > prevAlertCount.current) {
          setAlertHistory(prev => [
            { id: Date.now(), time: new Date().toLocaleTimeString() },
            ...prev
          ].slice(0, 10))
          prevAlertCount.current = json.alert_count
        }
      } catch (error) { }
    }

    const interval = setInterval(fetchPrediction, 500)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="app-container">
      <header>
        <h1>Safety<span className="highlight">Guard</span></h1>
        <p>Real time Driver Drowsiness detection system</p>
      </header>

      <main className="dashboard">
        <section className="video-container">
          <VideoFeed />
        </section>

        <section className="metrics-section">
          <StatusSection data={data} alertHistory={alertHistory} />
        </section>
      </main>

      <footer>
        <p>safety guard project 2026</p>
      </footer>

      {data.is_drowsy && <AlertOverlay isDrowsy={true} />}
    </div>
  )
}

export default App
