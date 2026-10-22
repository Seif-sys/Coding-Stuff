import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { askStream } from '../api'
import type { Source } from '../api'

interface Message {
  id: number
  question: string
  answer: string
  sources?: Source[]
  error?: string
}

interface Props {
  selected: string[]
}

const errMsg = (e: unknown) => (e instanceof Error ? e.message : 'Unknown error')

export default function ChatPanel({ selected }: Props) {
  const [messages, setMessages] = useState<Message[]>([])
  const [question, setQuestion] = useState('')
  const [busy, setBusy] = useState(false)
  const abortRef = useRef<AbortController | null>(null)

  useEffect(() => () => abortRef.current?.abort(), [])

  const canAsk = !busy && selected.length > 0 && question.trim().length > 0

  function patch(id: number, fn: (m: Message) => Message) {
    setMessages((prev) => prev.map((m) => (m.id === id ? fn(m) : m)))
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!canAsk) return
    const q = question.trim()
    const id = Date.now()
    const controller = new AbortController()
    abortRef.current = controller

    setQuestion('')
    setBusy(true)
    setMessages((prev) => [...prev, { id, question: q, answer: '' }])
    try {
      await askStream(
        q,
        selected,
        {
          onSources: (sources) => patch(id, (m) => ({ ...m, sources })),
          onToken: (token) => patch(id, (m) => ({ ...m, answer: m.answer + token })),
        },
        controller.signal,
      )
    } catch (err) {
      if (!controller.signal.aborted) patch(id, (m) => ({ ...m, error: errMsg(err) }))
    } finally {
      setBusy(false)
    }
  }

  return (
    <section>
      <h2>Ask</h2>
      {selected.length === 0 && <p>Select at least one document to ask a question.</p>}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question about the selected documents"
          maxLength={1000}
          disabled={busy}
        />{' '}
        <button type="submit" disabled={!canAsk}>
          {busy ? 'Thinking…' : 'Ask'}
        </button>
        {busy && (
          <>
            {' '}
            <button type="button" onClick={() => abortRef.current?.abort()}>
              Stop
            </button>
          </>
        )}
      </form>
      {messages.map((m) => (
        <div key={m.id}>
          <p>
            <strong>Q:</strong> {m.question}
          </p>
          <p>
            <strong>A:</strong> {m.answer || (m.error ? '' : '…')}
          </p>
          {m.error && <p role="alert">{m.error}</p>}
        </div>
      ))}
    </section>
  )
}