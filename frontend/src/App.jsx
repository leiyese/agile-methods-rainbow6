import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Chat from './components/Chat/Chat'
import LandingPage from './components/LandingPage/LandingPage'
import './App.css'

function App() {
  return (
    <Router>
      <div className="app-container">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
