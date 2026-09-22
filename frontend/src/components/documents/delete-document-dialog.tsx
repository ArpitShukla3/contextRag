import { useState } from 'react'
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog'
import { ApiError } from '@/api/client'
import type { Document } from '@/api/types'
import { useDeleteDocument } from '@/hooks/useDocuments'

interface DeleteDocumentDialogProps {
  document: Document | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onDeleted?: (id: number) => void
}

export function DeleteDocumentDialog({
  document,
  open,
  onOpenChange,
  onDeleted,
}: DeleteDocumentDialogProps) {
  const deleteMutation = useDeleteDocument()
  const [error, setError] = useState<string | null>(null)

  function handleConfirm() {
    if (!document) {
      return
    }
    setError(null)
    deleteMutation.mutate(document.id, {
      onSuccess: () => {
        onDeleted?.(document.id)
        onOpenChange(false)
      },
      onError: (err) => {
        setError(err instanceof ApiError ? err.message : 'The document could not be deleted.')
      },
    })
  }

  return (
    <AlertDialog
      open={open}
      onOpenChange={(next) => {
        if (!deleteMutation.isPending) {
          setError(null)
          onOpenChange(next)
        }
      }}
    >
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Delete &ldquo;{document?.original_filename ?? 'document'}&rdquo;?</AlertDialogTitle>
          <AlertDialogDescription>
            The document and its chunks will be permanently removed from the backend. This action
            cannot be undone.
          </AlertDialogDescription>
        </AlertDialogHeader>

        {error ? (
          <p role="alert" className="text-sm text-destructive">
            {error}
          </p>
        ) : null}

        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction
            onClick={(event) => {
              event.preventDefault()
              handleConfirm()
            }}
            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
          >
            {deleteMutation.isPending ? 'Deleting…' : 'Delete document'}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}