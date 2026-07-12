export const API_BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api'

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options.headers },
  })
  if (!res.ok) {
    const detail = await res.text()
    throw new ApiError(res.status, detail || res.statusText)
  }
  if (res.status === 204) {
    return undefined as T
  }
  return (await res.json()) as T
}

async function requestText(path: string): Promise<string> {
  const res = await fetch(`${API_BASE_URL}${path}`)
  if (!res.ok) {
    const detail = await res.text()
    throw new ApiError(res.status, detail || res.statusText)
  }
  return res.text()
}

async function requestFile<T>(path: string, file: File): Promise<T> {
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch(`${API_BASE_URL}${path}`, { method: 'POST', body: formData })
  if (!res.ok) {
    const detail = await res.text()
    throw new ApiError(res.status, detail || res.statusText)
  }
  return (await res.json()) as T
}

export const apiClient = {
  get: <T>(path: string): Promise<T> => request<T>(path),
  getText: (path: string): Promise<string> => requestText(path),
  post: <T>(path: string, body: unknown): Promise<T> =>
    request<T>(path, { method: 'POST', body: JSON.stringify(body) }),
  postFile: <T>(path: string, file: File): Promise<T> => requestFile<T>(path, file),
  patch: <T>(path: string, body: unknown): Promise<T> =>
    request<T>(path, { method: 'PATCH', body: JSON.stringify(body) }),
  put: <T>(path: string, body: unknown): Promise<T> =>
    request<T>(path, { method: 'PUT', body: JSON.stringify(body) }),
  delete: (path: string): Promise<void> => request<void>(path, { method: 'DELETE' }),
}
