import { FileText } from 'lucide-react'

export function EmptyDocumentsState() {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-dashed px-6 py-16 text-center">
      <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-secondary text-muted-foreground">
        <FileText className="h-6 w-6" />
      </div>
      <h3 className="text-base font-semibold">No documents yet</h3>
      <p className="mt-2 max-w-sm text-sm leading-relaxed text-muted-foreground">
        Upload a PDF, DOCX, Markdown, or text file to get started. The backend parses and chunks
        it, and the list is kept up to date as processing completes.
      </p>
    </div>
  )
}