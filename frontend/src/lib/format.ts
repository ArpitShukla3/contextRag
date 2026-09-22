import type { DocumentStatus } from '@/api/types'

const SIZE_UNITS = ['B', 'KB', 'MB', 'GB']

export function formatBytes(bytes: number): string {
  if (!Number.isFinite(bytes) || bytes < 0) {
    return '—'
  }
  if (bytes === 0) {
    return '0 B'
  }
  const exponent = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), SIZE_UNITS.length - 1)
  const value = bytes / Math.pow(1024, exponent)
  const precision = exponent === 0 ? 0 : value >= 10 ? 1 : 2
  return `${value.toFixed(precision)} ${SIZE_UNITS[exponent]}`
}

export function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return iso
  }
}

export function fileExtension(name: string): string {
  const match = /\.([^.]+)$/.exec(name)
  return match ? match[1].toLowerCase() : ''
}

/** Human-readable label for common document content types. */
export function fileTypeLabel(name: string, contentType: string): string {
  const byContentType: Record<string, string> = {
    'application/pdf': 'PDF',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'DOCX',
    'application/msword': 'DOC',
    'text/markdown': 'Markdown',
    'text/plain': 'Text',
  }
  const label = byContentType[contentType.toLowerCase()]
  if (label) {
    return label
  }
  const ext = fileExtension(name)
  return ext ? ext.toUpperCase() : 'File'
}

export function isProcessingStatus(status: DocumentStatus): boolean {
  return status === 'uploaded' || status === 'processing'
}