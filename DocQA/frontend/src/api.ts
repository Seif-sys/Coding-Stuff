export interface DocumentInfo {
  doc_id: string
  filename: string
  n_chunks: number
}

export interface Source {
  doc_id: string
  doc: string
  page: number
  text: string
}

export interface AskResult {
  answer: string
  sources?: Source[]
}

// Empty in dev (the Vite proxy forwards to the backend); set VITE_API_URL for a deployed backend.
const BASE: string = import.meta.env.VITE_API_URL ?? ''

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(BASE + path, init)
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      if (typeof body.detail === 'string') {
        detail = body.detail
      } else if (Array.isArray(body.detail)) {
        detail = body.detail.map((d: { msg: string }) => d.msg).join('; ') // pydantic 422
      }
    } catch {
      // body was not JSON; keep statusText
    }
    throw new ApiError(res.status, detail)
  }
  return res.status === 204 ? (undefined as T) : ((await res.json()) as T)
}

export const health = () => request<{ ok: boolean }>('/health')

export const listDocuments = () => request<DocumentInfo[]>('/documents')

export function uploadDocument(file: File): Promise<DocumentInfo> {
  const form = new FormData()
  form.append('file', file)
  return request<DocumentInfo>('/documents', { method: 'POST', body: form })
}

export const deleteDocument = (docId: string) =>
  request<void>(`/documents/${docId}`, { method: 'DELETE' })

export const ask = (question: string, docIds: string[], k = 3) =>
  request<AskResult>('/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, doc_ids: docIds, k }),
  })