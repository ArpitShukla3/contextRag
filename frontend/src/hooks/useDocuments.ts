import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { deleteDocument, getDocument, listDocuments, uploadDocument } from '@/api/documents'
import { documentKeys } from '@/api/query-keys'
import type { Document } from '@/api/types'

function hasPendingWork(documents: Document[]): boolean {
  return documents.some((doc) => doc.status === 'uploaded' || doc.status === 'processing')
}

/** All documents. Polls while any document is still processing. */
export function useDocuments() {
  return useQuery({
    queryKey: documentKeys.all,
    queryFn: listDocuments,
    refetchInterval: (query) => (hasPendingWork(query.state.data ?? []) ? 2500 : false),
  })
}

/** A single document by id (enabled only once an id is provided). */
export function useDocument(id: number | null) {
  return useQuery({
    queryKey: documentKeys.detail(id ?? 0),
    queryFn: () => getDocument(id as number),
    enabled: id !== null,
  })
}

/** Upload a file. The mutation injects the returned document into the list cache. */
export function useUploadDocument() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ file, onProgress }: { file: File; onProgress?: (p: number) => void }) =>
      uploadDocument(file, onProgress),
    onSuccess: (document) => {
      queryClient.setQueryData<Document[]>(documentKeys.all, (current) => {
        const documents = current ?? []
        return [document, ...documents.filter((doc) => doc.id !== document.id)]
      })
    },
  })
}

/** Delete a document and remove it from the cache. */
export function useDeleteDocument() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => deleteDocument(id),
    onSuccess: (_result, id) => {
      queryClient.setQueryData<Document[]>(documentKeys.all, (current) =>
        (current ?? []).filter((doc) => doc.id !== id),
      )
    },
  })
}