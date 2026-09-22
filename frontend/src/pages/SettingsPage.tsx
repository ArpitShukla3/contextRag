import { useQuery } from '@tanstack/react-query'
import { CheckCircle2, CircleDashed, RefreshCw } from 'lucide-react'
import { apiDisplayUrl, ApiError, DEV_PROXY_TARGET, request } from '@/api/client'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Separator } from '@/components/ui/separator'
import { useUiStore } from '@/stores/uiStore'

async function checkBackend(): Promise<{ ok: boolean }> {
  try {
    await request('/api/health')
    return { ok: true }
  } catch (error) {
    if (error instanceof ApiError) {
      return { ok: false }
    }
    throw error
  }
}

export function SettingsPage() {
  const theme = useUiStore((s) => s.theme)
  const setTheme = useUiStore((s) => s.setTheme)

  const health = useQuery({
    queryKey: ['backend-health'],
    queryFn: checkBackend,
    retry: false,
    refetchInterval: 30_000,
  })

  return (
    <div className="mx-auto max-w-2xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h2 className="text-2xl font-bold tracking-tight">Settings</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Preferences are stored locally for now. Model, fusion, and retrieval tuning arrive with
          the backend phases.
        </p>
      </div>

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Appearance</CardTitle>
            <CardDescription>Switch between light and dark mode.</CardDescription>
          </CardHeader>
          <CardContent className="flex gap-2">
            <Button
              variant={theme === 'light' ? 'secondary' : 'outline'}
              onClick={() => setTheme('light')}
            >
              Light
            </Button>
            <Button
              variant={theme === 'dark' ? 'secondary' : 'outline'}
              onClick={() => setTheme('dark')}
            >
              Dark
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Backend connection</CardTitle>
            <CardDescription>
              Requests resolve to{' '}
              <code className="rounded bg-muted px-1 py-0.5">{apiDisplayUrl()}</code>. During local
              development the Vite dev server proxies <code className="rounded bg-muted px-1 py-0.5">/api</code>{' '}
              to <code className="rounded bg-muted px-1 py-0.5">{DEV_PROXY_TARGET}</code>; set{' '}
              <code className="rounded bg-muted px-1 py-0.5">VITE_API_URL</code> to target a
              different backend.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input value={apiDisplayUrl()} readOnly aria-label="Backend API URL" />

            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-2 text-sm">
                {health.isLoading && (
                  <>
                    <CircleDashed className="h-4 w-4 animate-pulse text-muted-foreground" />
                    <span className="text-muted-foreground">Checking…</span>
                  </>
                )}
                {health.isSuccess && health.data.ok && (
                  <>
                    <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                    <span>Connected to {apiDisplayUrl()}</span>
                  </>
                )}
                {(health.isError || (health.isSuccess && !health.data.ok)) && (
                  <>
                    <CircleDashed className="h-4 w-4 text-destructive" />
                    <span className="text-destructive">
                      Unreachable — start the backend or set VITE_API_URL.
                    </span>
                  </>
                )}
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => void health.refetch()}
                disabled={health.isFetching}
              >
                <RefreshCw className={health.isFetching ? 'h-4 w-4 animate-spin' : 'h-4 w-4'} />
                Check again
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Retrieval defaults</CardTitle>
            <CardDescription>
              Placeholders for pipeline configuration that will be backed by the API.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1">
              <label className="text-xs font-medium text-muted-foreground" htmlFor="llm-model">
                LLM model (openrouter/)
              </label>
              <Input id="llm-model" placeholder="anthropic/claude-sonnet-4" disabled />
            </div>
            <Separator />
            <p className="text-xs text-muted-foreground">
              Fusion strategy, reranker selection, chunk size, and contextual model settings will
              appear here once the retrieval API ships.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}