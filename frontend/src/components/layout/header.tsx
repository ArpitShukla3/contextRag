import { Menu, Moon, Sun } from 'lucide-react'
import { apiDisplayUrl } from '@/api/client'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useUiStore, type Theme } from '@/stores/uiStore'

const TITLES: Record<string, string> = {
  '/': 'Overview',
  '/chat': 'Chat',
  '/documents': 'Documents',
  '/settings': 'Settings',
}

export function Header({ pathname }: { pathname: string }) {
  const theme = useUiStore((s) => s.theme)
  const setTheme = useUiStore((s) => s.setTheme)
  const openSidebar = useUiStore((s) => s.openSidebar)

  const title = TITLES[pathname] ?? 'Contextual RAG'
  const nextTheme: Theme = theme === 'light' ? 'dark' : 'light'

  return (
    <header className="flex h-16 shrink-0 items-center gap-3 border-b bg-background/80 px-4 backdrop-blur sm:px-6">
      <Button
        variant="ghost"
        size="icon"
        className="lg:hidden"
        onClick={openSidebar}
        aria-label="Open navigation"
      >
        <Menu className="h-5 w-5" />
      </Button>

      <h1 className="text-base font-semibold tracking-tight">{title}</h1>

      <div className="ml-auto flex items-center gap-2">
        <Badge variant="secondary" className="hidden font-normal sm:inline-flex">
          <span className="mr-1.5 inline-block h-1.5 w-1.5 rounded-full bg-emerald-500" />
          {apiDisplayUrl()}
        </Badge>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setTheme(nextTheme)}
          aria-label={`Switch to ${nextTheme} mode`}
        >
          <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
        </Button>
      </div>
    </header>
  )
}