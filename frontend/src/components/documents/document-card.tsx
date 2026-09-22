import { FileText, Trash2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { fileTypeLabel, formatBytes, formatDate } from '@/lib/format'
import type { Document } from '@/api/types'
import { ProcessingStatus } from './processing-status'

interface DocumentCardProps {
  document: Document
  selected: boolean
  onSelect: () => void
  onRequestDelete: () => void
}

export function DocumentCard({ document, selected, onSelect, onRequestDelete }: DocumentCardProps) {
  return (
    <Card
      className={cn(
        'h-full transition-all',
        selected ? 'border-primary ring-1 ring-primary' : 'group/card hover:border-primary/40',
      )}
    >
      <button
        type="button"
        onClick={onSelect}
        aria-pressed={selected}
        className="block w-full text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-ring rounded-t-lg"
      >
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-secondary text-muted-foreground">
              <FileText className="h-4 w-4" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium" title={document.original_filename}>
                {document.original_filename}
              </p>
              <p className="mt-1.5 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-muted-foreground">
                <Badge variant="secondary" className="font-normal">
                  {fileTypeLabel(document.original_filename, document.content_type)}
                </Badge>
                <span>{formatBytes(document.file_size)}</span>
                <span className="whitespace-nowrap">{formatDate(document.created_at)}</span>
              </p>
            </div>
          </div>
        </CardContent>
      </button>

      <div className="flex items-center justify-between rounded-b-lg border-t bg-muted/40 px-4 py-2">
        <ProcessingStatus status={document.status} />
        <Button
          variant="ghost"
          size="sm"
          onClick={onRequestDelete}
          className="text-muted-foreground hover:text-destructive"
        >
          <Trash2 className="h-4 w-4" />
          Delete
        </Button>
      </div>
    </Card>
  )
}