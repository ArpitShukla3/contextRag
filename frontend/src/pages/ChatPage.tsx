import { SendHorizontal, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Textarea } from '@/components/ui/textarea'

export function ChatPage() {
  return (
    <div className="flex h-full flex-col">
      <ScrollArea className="flex-1">
        <div className="mx-auto flex h-full max-w-3xl items-center px-6 py-16">
          <div className="mx-auto max-w-md text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-secondary text-muted-foreground">
              <Sparkles className="h-6 w-6" />
            </div>
            <h3 className="text-xl font-semibold tracking-tight">Ask anything about your documents</h3>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
              Conversations are created and answers are streamed here — with the exact chunks and
              scores used to answer each question.
            </p>
            <p className="mt-8 text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Chat streaming arrives in a later phase
            </p>
          </div>
        </div>
      </ScrollArea>

      <div className="border-t bg-background/80 p-4 backdrop-blur sm:p-6">
        <div className="mx-auto max-w-3xl">
          <div className="flex items-end gap-2">
            <Textarea
              disabled
              rows={2}
              placeholder="Select a document and ask a question…"
              className="resize-none bg-background disabled:opacity-60"
            />
            <Button size="icon" disabled aria-label="Send message">
              <SendHorizontal className="h-5 w-5" />
            </Button>
          </div>
          <p className="mt-2 text-center text-xs text-muted-foreground">
            This interface is a placeholder — submissions are disabled until the streaming API is
            wired up.
          </p>
        </div>
      </div>
    </div>
  )
}