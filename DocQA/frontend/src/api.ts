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

export interface StreamHandlers {
  onSources?: (sources: Source[]) => void
  onToken?: (token: string) => void
  onDone?: () => void
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

async function errorFrom(res: Response): Promise<ApiError> {
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
  return new ApiError(res.status, detail)
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(BASE + path, init)
  if (!res.ok) throw await errorFrom(res)
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

function parseJson(raw: string): unknown {
  try {
    return JSON.parse(raw)
  } catch {
    return undefined
  }
}

// First string found: the payload itself, or one of the given keys of a JSON object.
function field(payload: unknown, keys: string[]): string | undefined {
  if (typeof payload === 'string') return payload
  if (payload && typeof payload === 'object') {
    for (const key of keys) {
      const value = (payload as Record<string, unknown>)[key]
      if (typeof value === 'string') return value
    }
  }
  return undefined
}

function dispatch(block: string, handlers: StreamHandlers) {
  let event = 'message'
  const data: string[] = []
  for (const line of block.split(/\r?\n/)) {
    if (line.startsWith(':')) continue // SSE comment / keep-alive
    if (line.startsWith('event:')) event = line.slice(6).trim()
    else if (line.startsWith('data:')) data.push(line.slice(5).replace(/^ /, ''))
  }
  if (data.length === 0 && event === 'message') return
  const raw = data.join('\n')
  const payload = parseJson(raw)

  switch (event) {
    case 'sources': {
      const list = Array.isArray(payload)
        ? payload
        : (payload as { sources?: unknown } | undefined)?.sources
      handlers.onSources?.(Array.isArray(list) ? (list as Source[]) : [])
      break
    }
    case 'token':
      handlers.onToken?.(field(payload, ['token', 'text', 'content']) ?? raw)
      break
    case 'done':
      handlers.onDone?.()
      break
    case 'error':
      throw new ApiError(500, field(payload, ['detail', 'message', 'error']) ?? (raw || 'Stream error'))
  }
}

export async function askStream(
  question: string,
  docIds: string[],
  handlers: StreamHandlers,
  signal?: AbortSignal,
  k = 3,
): Promise<void> {
  const res = await fetch(BASE + '/ask/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, doc_ids: docIds, k }),
    signal,
  })
  if (!res.ok) throw await errorFrom(res)
  if (!res.body) throw new ApiError(res.status, 'Empty response body')

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  for (;;) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const blocks = buffer.split(/\r?\n\r?\n/)
    buffer = blocks.pop() ?? ''
    for (const block of blocks) dispatch(block, handlers)
  }
  buffer += decoder.decode()
  if (buffer.trim()) dispatch(buffer, handlers)
}