export type DocumentStatus = 'uploaded' | 'processing' | 'processed' | 'failed'

export interface Document {
  id: number
  /** Storage name on the backend (not meant for display). */
  filename: string
  original_filename: string
  content_type: string
  file_size: number
  status: DocumentStatus
  created_at: string
  updated_at: string
}

export interface DocumentChunk {
  id: number
  document_id: number
  chunk_index: number
  original_content: string
  contextual_content: string | null
  metadata: Record<string, unknown>
  created_at: string
}