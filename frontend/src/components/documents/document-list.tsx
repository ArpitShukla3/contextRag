import type { Document } from '@/api/types'
import { DocumentCard } from './document-card'

interface DocumentListProps {
  documents: Document[]
  selectedId: number | null
  onSelect: (id: number) => void
  onDelete: (document: Document) => void
}

export function DocumentList({ documents, selectedId, onSelect, onDelete }: DocumentListProps) {
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {documents.map((document) => (
        <DocumentCard
          key={document.id}
          document={document}
          selected={document.id === selectedId}
          onSelect={() => onSelect(document.id)}
          onRequestDelete={() => onDelete(document)}
        />
      ))}
    </div>
  )
}