import { Link } from 'react-router-dom'
import { ArrowRight, FileText, MessageSquare, Settings } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Markdown } from '@/components/markdown'

const ABOUT = `
Contextual Retrieval improves RAG by giving every chunk short model-generated context — a
sentence describing *why* the chunk is relevant and where it fits within the document. Those
contextualized chunks are indexed with vector search **and** BM25, fused, and optionally
reranked before being presented to the model.
`

const STEPS = [
  {
    to: '/documents',
    icon: FileText,
    title: 'Upload documents',
    description:
      'Add PDFs, DOCX, and text files. The backend parses, chunks, and contextualizes them.',
  },
  {
    to: '/chat',
    icon: MessageSquare,
    title: 'Ask questions',
    description:
      'Query your documents and inspect exact sources and chunk scores behind every answer.',
  },
  {
    to: '/settings',
    icon: Settings,
    title: 'Compare & configure',
    description:
      'Compare baseline RAG against contextual RAG and tune models, fusion, and reranking.',
  },
]

export function HomePage() {
  return (
    <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="mb-12">
        <p className="mb-3 text-sm font-medium text-muted-foreground">Phase 1 · Application shell</p>
        <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
          Build, run, and inspect contextual retrieval over your own documents.
        </h2>
        <p className="mt-4 max-w-2xl text-muted-foreground">
          A production-oriented RAG stack implementing Anthropic&apos;s Contextual Retrieval
          technique — with transparent, inspectable retrieval at every step.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        {STEPS.map((step) => {
          const Icon = step.icon
          return (
            <Link key={step.to} to={step.to} className="group focus-visible:outline-none">
              <Card className="h-full transition-colors group-hover:border-primary/50 group-focus-visible:ring-2 group-focus-visible:ring-ring">
                <CardHeader>
                  <Icon className="mb-2 h-5 w-5 text-muted-foreground" />
                  <CardTitle className="flex items-center gap-1 text-base">
                    {step.title}
                    <ArrowRight className="h-4 w-4 opacity-0 transition-opacity group-hover:opacity-100" />
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription>{step.description}</CardDescription>
                </CardContent>
              </Card>
            </Link>
          )
        })}
      </div>

      <Card className="mt-8">
        <CardHeader>
          <CardTitle className="text-base">What is contextual retrieval?</CardTitle>
        </CardHeader>
        <CardContent>
          <Markdown>{ABOUT}</Markdown>
        </CardContent>
      </Card>
    </div>
  )
}