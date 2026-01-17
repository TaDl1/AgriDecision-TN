import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

// Add error boundary for development
const root = ReactDOM.createRoot(document.getElementById('root'))

try {
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  )
} catch (error) {
  console.error('Failed to render React app:', error)
  root.render(
    <div style={{padding: '20px', fontFamily: 'sans-serif'}}>
      <h1>⚠️ Application Error</h1>
      <p>Error: {error.message}</p>
      <p>Check browser console for details.</p>
    </div>
  )
}