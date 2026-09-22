import { useState } from 'react'
import { AlertCircle, Loader2, RefreshCw } from 'lucide-react'
import { ApiError } from '@/api/client'
import type { Document } from '@/api/types'
import { DeleteDocumentDialog } from '@/components/documents/delete-document-dialog'
import { DocumentList } from '@/components/documents/document-list'
import { DocumentUploader } from '@/components/documents/document-uploader'
import { EmptyDocumentsState } from '@/components/documents/empty-documents-state'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { useDocuments } from '@/hooks/useDocuments'
import { useDocumentStore } from '@/stores/documentStore'

function DocumentListSkeleton() {
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {Array.from({ length: 4 }).map((_, index) => (
        <div key={index} className="rounded-lg border p-4">
          <div className="flex items-start gap-3">
            <Skeleton className="h-9 w-9 rounded-md" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-3 w-1/2" />
            </div>
          </div>
          <Skeleton className="mt-4 h-6 w-full" />
        </div>
      ))}
    </div>
  )
}

export function DocumentsPage() {
  const documentsQuery = useDocuments()
  const [documentToDelete, setDocumentToDelete] = useState<Document | null>(null)

  const selectedDocumentId = useDocumentStore((s) => s.selectedDocumentId)
  const setSelectedDocumentId = useDocumentStore((s) => s.setSelectedDocumentId)
  const clearSelectedDocument = useDocumentStore((s) => s.clearSelectedDocument)

  const documents = documentsQuery.data ?? []
  const selectedDocument =
    selectedDocumentId !== null
      ? documents.find((doc) => doc.id === selectedDocumentId) ?? null
      : null

  const fatalError =
    documentsQuery.isError && !documentsQuery.isFetching && documents.length === 0
      ? documentsQuery.error
      : null

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold tracking-tight">Documents</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Upload files to the backend. Each document is parsed, chunked, and its status tracked
          here until processing completes.
        </p>
      </div>

      <DocumentUploader />

      <div className="mb-3 mt-8 flex items-center justify-between">
        <h3 className="text-sm font-medium text-muted-foreground">
          {documents.length > 0
            ? `${documents.length} document${documents.length === 1 ? '' : 's'}`
            : 'Documents'}
        </h3>
        {selectedDocument ? (
          <button
            type="button"
            onClick={clearSelectedDocument}
            className="text-xs font-medium text-primary underline-offset-2 hover:underline"
          >
            Clear selection
          </button>
        ) : null}
      </div>

      {fatalError ? (
        <div className="rounded-lg border border-destructive/50 bg-destructive/5 p-6 text-center">
          <AlertCircle className="mx-auto mb-3 h-8 w-8 text-destructive" />
          <h3 className="text-sm font-semibold">Could not load documents</h3>
          <p className="mx-auto mt-1 max-w-md text-sm text-muted-foreground">
            {fatalError instanceof ApiError
              ? fatalError.message
              : 'Something went wrong while fetching documents.'}
          </p>
          <Button variant="outline" size="sm" className="mt-4" onClick={() => documentsQuery.refetch()}>
            <RefreshCw className="h-4 w-4" />
            Try again
          </Button>
        </div>
      ) : documentsQuery.isLoading ? (
        <DocumentListSkeleton />
      ) : documents.length === 0 ? (
        <EmptyDocumentsState />
      ) : (
        <>
          <DocumentList
            documents={documents}
            selectedId={selectedDocumentId}
            onSelect={(id) => setSelectedDocumentId(selectedDocumentId === id ? null : id)}
            onDelete={(document) => setDocumentToDelete(document)}
          />
          {documentsQuery.isRefetching ? (
            <p className="mt-3 flex items-center justify-center gap-1.5 text-xs text-muted-foreground">
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
              Checking processing status…
            </p>
          ) : null}
        </>
      )}

      <DeleteDocumentDialog
        document={documentToDelete}
        open={documentToDelete !== null}
        onOpenChange={(open) => {
          if (!open) {
            setDocumentToDelete(null)
          }
        }}
        onDeleted={(id) => {
          if (selectedDocumentId === id) {
            clearSelectedDocument()
          }
        }}
      />
    </div>
  )
}