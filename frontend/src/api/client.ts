/* Tiny typed fetch wrapper around the FastAPI backend.
   The Vite dev server proxies /api -> http://127.0.0.1:8000 (see vite.config). */

const BASE = import.meta.env.VITE_API_BASE ?? '/api'

export class ApiError extends Error {
  status: number
  detail: unknown
  constructor(status: number, message: string, detail: unknown) {
    super(message)
    this.status = status
    this.detail = detail
  }
}

const BACKEND_DOWN_HINT =
  'Cannot reach the API server. Make sure the backend is running: ' +
  'in backend/ run  py -m uvicorn app.main:app --reload  (it should be on http://127.0.0.1:8000).'

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  let res: Response
  // Guard against a request that never settles (e.g. a dev-proxy connection
  // reset mid-response) — without this the UI can "spin forever".
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 30_000)
  try {
    res = await fetch(`${BASE}${path}`, {
      method,
      headers: body !== undefined ? { 'Content-Type': 'application/json' } : undefined,
      body: body !== undefined ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    })
  } catch (e) {
    if ((e as Error)?.name === 'AbortError') {
      throw new ApiError(0, 'The request timed out. It may have saved — refresh to check.', null)
    }
    // Network-level failure (DNS/connection refused) — backend almost certainly down.
    throw new ApiError(0, BACKEND_DOWN_HINT, null)
  } finally {
    clearTimeout(timeout)
  }

  if (!res.ok) {
    let detail: unknown = null
    try {
      detail = await res.json()
    } catch {
      /* non-JSON error body (e.g. dev-proxy error page when backend is down) */
    }
    const apiDetail = (detail as { detail?: string } | null)?.detail
    let message: string
    if (typeof apiDetail === 'string') {
      // A real, structured error from FastAPI.
      message = apiDetail
    } else if (res.status >= 500) {
      // 5xx with no JSON body = the Vite proxy couldn't reach the backend.
      message = `${BACKEND_DOWN_HINT} (HTTP ${res.status})`
    } else {
      message = `Request failed (${res.status})`
    }
    throw new ApiError(res.status, message, detail)
  }

  if (res.status === 204) return undefined as T
  return (await res.json()) as T
}

export const api = {
  get: <T>(path: string) => request<T>('GET', path),
  post: <T>(path: string, body?: unknown) => request<T>('POST', path, body),
  put: <T>(path: string, body?: unknown) => request<T>('PUT', path, body),
  delete: <T>(path: string) => request<T>('DELETE', path),
}

export const API_BASE = BASE
