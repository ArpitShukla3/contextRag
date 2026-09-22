/** Base URL of the backend, read from VITE_API_URL. */
export const API_BASE_URL = (import.meta.env.VITE_API_URL ?? '').replace(/\/+$/, '')

/** Backend origin the Vite dev/preview server proxies `/api` to. */
export const DEV_PROXY_TARGET = 'http://localhost:8000'

/**
 * Human-facing view of where API requests resolve. Empty base URL means
 * same-origin requests that Vite forwards through its `/api` proxy in dev.
 */
export function apiDisplayUrl(): string {
  if (API_BASE_URL) {
    return API_BASE_URL
  }
  return import.meta.env.DEV ? `${DEV_PROXY_TARGET}/api` : '/api'
}

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export interface RequestOptions extends Omit<RequestInit, 'body'> {
  body?: unknown
  query?: Record<string, string | number | boolean | undefined>
}

function toQueryString(query: RequestOptions['query']): string {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(query ?? {})) {
    if (value !== undefined) {
      params.set(key, String(value))
    }
  }
  const str = params.toString()
  return str ? `?${str}` : ''
}

function extractErrorMessage(response: Response, payload: unknown): string {
  if (payload && typeof payload === 'object' && 'detail' in payload) {
    const detail = (payload as { detail?: unknown }).detail
    if (typeof detail === 'string') {
      return detail
    }
    if (Array.isArray(detail)) {
      const parts = detail
        .map((item) => {
          if (item && typeof item === 'object' && 'msg' in item) {
            return String((item as { msg: unknown }).msg)
          }
          return null
        })
        .filter(Boolean)
      if (parts.length > 0) {
        return parts.join(', ')
      }
    }
  }
  return response.statusText || `Request failed (${response.status}).`
}

/**
 * Thin typed wrapper around fetch. All API modules should go through this so
 * the base URL, headers, and error handling stay in one place.
 */
export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { body, query, headers, ...rest } = options

  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}${toQueryString(query)}`, {
      ...rest,
      headers: {
        ...(body !== undefined ? { 'Content-Type': 'application/json' } : {}),
        ...headers,
      },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  } catch {
    throw new ApiError(0, `Could not reach the backend at ${apiDisplayUrl()}.`)
  }

  if (!response.ok) {
    let payload: unknown = null
    try {
      payload = await response.json()
    } catch {
      // non-JSON error body; fall back to statusText
    }
    throw new ApiError(response.status, extractErrorMessage(response, payload))
  }

  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}

/**
 * Multipart upload using XMLHttpRequest so progress events are available.
 * `fieldName` matches the FastAPI `UploadFile` parameter name.
 */
export async function uploadFile<T>(
  path: string,
  file: Blob,
  fieldName: string,
  filename: string,
  onProgress?: (percent: number) => void,
): Promise<T> {
  const form = new FormData()
  form.append(fieldName, file, filename)

  return new Promise<T>((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('POST', `${API_BASE_URL}${path}`)
    xhr.responseType = 'json'

    if (onProgress) {
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          onProgress(Math.round((event.loaded / event.total) * 100))
        }
      }
    }

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(xhr.response as T)
        return
      }
      const payload: unknown = xhr.response
      const message =
        payload && typeof payload === 'object' && 'detail' in payload
          ? String((payload as { detail: unknown }).detail)
          : xhr.statusText
      reject(new ApiError(xhr.status, message || `Upload failed (${xhr.status}).`))
    }

    xhr.onerror = () =>
      reject(new ApiError(0, `Could not reach the backend at ${apiDisplayUrl()}.`))
    xhr.ontimeout = () => reject(new ApiError(0, 'The upload timed out.'))
    xhr.timeout = 0

    xhr.send(form)
  })
}