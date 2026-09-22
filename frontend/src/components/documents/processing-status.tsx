import { AlertTriangle, CheckCircle2, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { DocumentStatus } from '@/api/types'

const CONFIG: Record<DocumentStatus, { label: string; className: string }> = {
  uploaded: { label: 'Uploaded', className: 'text-muted-foreground' },
  processing: { label: 'Processing', className: 'text-muted-foreground' },
  processed: { label: 'Ready', className: 'text-emerald-600 dark:text-emerald-500' },
  failed: { label: 'Failed', className: 'text-destructive' },
}

export function ProcessingStatus({ status }: { status: DocumentStatus }) {
  const config = CONFIG[status]
  const pending = status === 'uploaded' || status === 'processing'

  return (
    <span className={cn('inline-flex items-center gap-1.5 text-xs font-medium', config.className)}>
      {pending ? (
        <Loader2 className="h-3.5 w-3.5 animate-spin" />
      ) : status === 'processed' ? (
        <CheckCircle2 className="h-3.5 w-3.5" />
      ) : (
        <AlertTriangle className="h-3.5 w-3.5" />
      )}
      {config.label}
    </span>
  )
}