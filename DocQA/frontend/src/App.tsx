import { useEffect, useState } from 'react'
import { health } from './api'
import DocumentPanel from './components/DocumentPanel'

type Status = 'checking' | 'ok' | 'down'

export default function App() {
  const [status, setStatus] = useState<Status>('checking')
  const [selected, setSelected] = useState<string[]>([])

  useEffect(() => {
    health()
      .then(() => setStatus('ok'))
      .catch(() => setStatus('down'))
  }, [])

  return (
    <main>
      <h1>DocQA</h1>
      <p>Backend: {status}</p>
      <DocumentPanel selected={selected} onSelectedChange={setSelected} />
    </main>
  )
}