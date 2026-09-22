import { request, uploadFile } from './client'
import type { Document, DocumentChunk } from './types'

/** List all documents, newest first. */
export function listDocuments(): Promise<Document[]> {
  return request<Document[]>('/api/documents')
}

/** Fetch a single document by id. */
export function getDocument(id: number): Promise<Document> {
  return request<Document>(`/api/documents/${id}`)
}

/** Delete a document and its chunks. */
export function deleteDocument(id: number): Promise<void> {
  return request<void>(`/api/documents/${id}`, { method: 'DELETE' })
}

/** Fetch the chunks belonging to a document. */
export function listDocumentChunks(id: number): Promise<DocumentChunk[]> {
  return request<DocumentChunk[]>(`/api/documents/${id}/chunks`)
}

/** Upload a single file and run the backend ingestion pipeline. */
export function uploadDocument(
  file: File,
  onProgress?: (percent: number) => void,
): Promise<Document> {
  return uploadFile<Document>('/api/documents', file, 'file', file.name, onProgress)
}