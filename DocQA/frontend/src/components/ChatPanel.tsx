import { useState } from 'react'
import type { FormEvent } from 'react'
import { ask } from '../api'
import type { Source } from '../api'

interface Message {
  id: number
  question: string
  answer?: string
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

  const canAsk = !busy && selected.length > 0 && question.trim().length > 0

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!canAsk) return
    const q = question.trim()
    const id = Date.now()
    setQuestion('')
    setBusy(true)
    setMessages((prev) => [...prev, { id, question: q }])
    try {
      const res = await ask(q, selected)
      setMessages((prev) =>
        prev.map((m) => (m.id === id ? { ...m, answer: res.answer, sources: res.sources } : m)),
      )
    } catch (err) {
      setMessages((prev) => prev.map((m) => (m.id === id ? { ...m, error: errMsg(err) } : m)))
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
      </form>
      {messages.map((m) => (
        <div key={m.id}>
          <p>
            <strong>Q:</strong> {m.question}
          </p>
          {m.error ? (
            <p role="alert">{m.error}</p>
          ) : m.answer !== undefined ? (
            <p>
              <strong>A:</strong> {m.answer}
            </p>
          ) : (
            <p>…</p>
          )}
        </div>
      ))}
    </section>
  )
}