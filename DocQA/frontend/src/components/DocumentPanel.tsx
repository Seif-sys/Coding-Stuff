import { useEffect, useState } from 'react'
import { deleteDocument, listDocuments, uploadDocument } from '../api'
import type { DocumentInfo } from '../api'

interface Props {
  selected: string[]
  onSelectedChange: (ids: string[]) => void
}

const errMsg = (e: unknown) => (e instanceof Error ? e.message : 'Unknown error')

export default function DocumentPanel({ selected, onSelectedChange }: Props) {
  const [docs, setDocs] = useState<DocumentInfo[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    listDocuments()
      .then(setDocs)
      .catch((e) => setError(errMsg(e)))
  }, [])

  async function handleFiles(e: React.ChangeEvent<HTMLInputElement>) {
    const input = e.currentTarget
    const files = Array.from(input.files ?? [])
    input.value = ''
    if (files.length === 0) return

    setBusy(true)
    setError(null)
    const added: DocumentInfo[] = []
    for (const file of files) {
      try {
        added.push(await uploadDocument(file))
      } catch (err) {
        setError(`${file.name}: ${errMsg(err)}`)
      }
    }
    setDocs((prev) => [...prev, ...added])
    onSelectedChange([...selected, ...added.map((d) => d.doc_id)])
    setBusy(false)
  }

  async function handleDelete(docId: string) {
    setError(null)
    try {
      await deleteDocument(docId)
      setDocs((prev) => prev.filter((d) => d.doc_id !== docId))
      onSelectedChange(selected.filter((id) => id !== docId))
    } catch (err) {
      setError(errMsg(err))
    }
  }

  function toggle(docId: string) {
    onSelectedChange(
      selected.includes(docId) ? selected.filter((id) => id !== docId) : [...selected, docId],
    )
  }

  return (
    <section>
      <h2>Documents</h2>
      <input type="file" accept="application/pdf" multiple disabled={busy} onChange={handleFiles} />
      {busy && <p>Uploading…</p>}
      {error && <p role="alert">{error}</p>}
      {docs.length === 0 ? (
        <p>No documents yet.</p>
      ) : (
        <ul>
          {docs.map((d) => (
            <li key={d.doc_id}>
              <label>
                <input
                  type="checkbox"
                  checked={selected.includes(d.doc_id)}
                  onChange={() => toggle(d.doc_id)}
                />{' '}
                {d.filename} ({d.n_chunks} chunks)
              </label>{' '}
              <button type="button" onClick={() => handleDelete(d.doc_id)}>
                Delete
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}