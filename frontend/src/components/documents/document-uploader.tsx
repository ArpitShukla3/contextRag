import { useRef, useState } from 'react'
import { CloudUpload, FileUp } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { useUploadDocument } from '@/hooks/useDocuments'
import { UploadProgress } from './upload-progress'

const ACCEPTED_EXTENSIONS = '.pdf,.docx,.md,.txt'

interface ActiveUpload {
  key: string
  name: string
  percent: number
}

function fileKey(file: File): string {
  return `${file.name}:${file.size}:${file.lastModified}`
}

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : 'The upload failed.'
}

export function DocumentUploader() {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragActive, setDragActive] = useState(false)
  const [uploads, setUploads] = useState<ActiveUpload[]>([])
  const [errors, setErrors] = useState<string[]>([])
  const upload = useUploadDocument()
  const isUploading = uploads.length > 0 || upload.isPending

  async function handleFiles(files: File[]) {
    if (files.length === 0) {
      return
    }
    setErrors([])
    for (const file of files) {
      const key = fileKey(file)
      setUploads((current) => [...current, { key, name: file.name, percent: 0 }])
      try {
        await upload.mutateAsync({
          file,
          onProgress: (percent) =>
            setUploads((current) =>
              current.map((item) => (item.key === key ? { ...item, percent } : item)),
            ),
        })
        setUploads((current) => current.filter((item) => item.key !== key))
      } catch (error) {
        setUploads((current) => current.filter((item) => item.key !== key))
        setErrors((current) => [
          ...current,
          `${file.name}: ${errorMessage(error)}`,
        ])
      }
    }
  }

  return (
    <div className="space-y-0">
      <div
        onDragOver={(event) => {
          event.preventDefault()
          setDragActive(true)
        }}
        onDragLeave={(event) => {
          if (event.currentTarget === event.target) {
            setDragActive(false)
          }
        }}
        onDrop={(event) => {
          event.preventDefault()
          setDragActive(false)
          void handleFiles(Array.from(event.dataTransfer.files))
        }}
        className={cn(
          'flex flex-col items-center justify-center rounded-lg border-2 border-dashed px-6 py-10 text-center transition-colors',
          dragActive
            ? 'border-primary bg-primary/5'
            : 'border-muted-foreground/25 hover:border-muted-foreground/50',
        )}
      >
        <input
          ref={inputRef}
          type="file"
          multiple
          accept={ACCEPTED_EXTENSIONS}
          className="hidden"
          onChange={(event) => {
            const files = Array.from(event.target.files ?? [])
            void handleFiles(files)
            event.target.value = ''
          }}
        />
        <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-full bg-secondary text-muted-foreground">
          <CloudUpload className="h-5 w-5" />
        </div>
        <p className="text-sm font-medium text-foreground">
          Drop files here, or{' '}
          <button
            type="button"
            onClick={() => inputRef.current?.click()}
            disabled={isUploading}
            className="font-semibold text-primary underline-offset-2 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded-sm disabled:pointer-events-none disabled:opacity-50"
          >
            browse
          </button>
        </p>
        <p className="mt-1 text-xs text-muted-foreground">
          PDF, DOCX, Markdown, and text files are supported.
        </p>
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="mt-4"
          onClick={() => inputRef.current?.click()}
          disabled={isUploading}
        >
          <FileUp className="h-4 w-4" />
          Choose files
        </Button>
      </div>

      {uploads.length > 0 ? (
        <div className="mt-3 space-y-2">
          {uploads.map((item) => (
            <UploadProgress key={item.key} fileName={item.name} percent={item.percent} />
          ))}
        </div>
      ) : null}

      {errors.length > 0 ? (
        <div role="alert" className="mt-3 rounded-md border border-destructive/50 bg-destructive/5 px-3 py-2.5">
          <p className="mb-1 text-xs font-semibold text-destructive">Some uploads failed</p>
          <ul className="list-inside list-disc space-y-0.5 text-sm text-destructive">
            {errors.map((message, index) => (
              <li key={index} className="text-xs">
                {message}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  )
}