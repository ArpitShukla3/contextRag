export function UploadProgress({ fileName, percent }: { fileName: string; percent: number }) {
  return (
    <div className="mt-3 rounded-md border px-3 py-2.5">
      <div className="mb-1.5 flex items-center justify-between gap-3">
        <span className="truncate text-xs font-medium">{fileName}</span>
        <span className="shrink-0 text-xs tabular-nums text-muted-foreground">{percent}%</span>
      </div>
      <div
        className="h-1.5 w-full overflow-hidden rounded-full bg-muted"
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={percent}
        aria-label={`Uploading ${fileName}`}
      >
        <div
          className="h-full rounded-full bg-primary transition-[width] duration-200"
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  )
}