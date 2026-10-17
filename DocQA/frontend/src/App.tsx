import { useEffect, useState } from 'react'
import { health } from './api'

type Status = 'checking' | 'ok' | 'down'

export default function App() {
  const [status, setStatus] = useState<Status>('checking')

  useEffect(() => {
    health()
      .then(() => setStatus('ok'))
      .catch(() => setStatus('down'))
  }, [])

  return (
    <main>
      <h1>DocQA</h1>
      <p>Backend: {status}</p>
    </main>
  )
}