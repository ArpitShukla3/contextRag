import ReactMarkdown from 'react-markdown'

export function Markdown({ children }: { children: string }) {
  return (
    <div className="prose-sm prose prose-slate max-w-none prose-headings:scroll-m-20 prose-p:leading-relaxed prose-pre:overflow-x-auto prose-pre:rounded-md prose-pre:bg-muted prose-pre:text-muted-foreground dark:prose-invert">
      <ReactMarkdown>{children}</ReactMarkdown>
    </div>
  )
}