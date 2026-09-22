import { Link, NavLink } from 'react-router-dom'
import { Boxes, FileText, LayoutGrid, MessageSquare, Settings } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useUiStore } from '@/stores/uiStore'
import { Separator } from '@/components/ui/separator'

const NAV_ITEMS = [
  { to: '/chat', label: 'Chat', icon: MessageSquare, end: false },
  { to: '/documents', label: 'Documents', icon: FileText, end: false },
  { to: '/settings', label: 'Settings', icon: Settings, end: false },
]

function NavLinks({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <nav className="flex flex-col gap-1 px-3">
      <NavLink
        to="/"
        end
        onClick={onNavigate}
        className={({ isActive }) =>
          cn(
            'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
            isActive
              ? 'bg-sidebar-accent text-accent-foreground'
              : 'text-sidebar-muted hover:bg-sidebar-accent/60 hover:text-sidebar-foreground',
          )
        }
      >
        <LayoutGrid className="h-4 w-4" />
        Overview
      </NavLink>
      {NAV_ITEMS.map((item) => {
        const Icon = item.icon
        return (
          <NavLink
            key={item.to}
            to={item.to}
            onClick={onNavigate}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-sidebar-accent text-accent-foreground'
                  : 'text-sidebar-muted hover:bg-sidebar-accent/60 hover:text-sidebar-foreground',
              )
            }
          >
            <Icon className="h-4 w-4" />
            {item.label}
          </NavLink>
        )
      })}
    </nav>
  )
}

function Brand() {
  return (
    <Link to="/" className="flex items-center gap-2.5 px-6 py-5">
      <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary text-primary-foreground">
        <Boxes className="h-4 w-4" />
      </div>
      <div className="leading-tight">
        <p className="text-sm font-semibold">Contextual RAG</p>
        <p className="text-[11px] text-sidebar-muted">Retrieval you can inspect</p>
      </div>
    </Link>
  )
}

function SidebarFooter() {
  return (
    <div className="px-6 py-4">
      <Separator className="mb-4" />
      <p className="text-[11px] leading-relaxed text-sidebar-muted">
        Built on the{' '}
        <a
          href="https://www.anthropic.com/engineering/contextual-retrieval"
          target="_blank"
          rel="noreferrer"
          className="font-medium text-sidebar-foreground underline-offset-2 hover:underline"
        >
          Contextual Retrieval
        </a>{' '}
        technique.
      </p>
    </div>
  )
}

export function Sidebar() {
  return (
    <aside className="hidden h-full w-64 shrink-0 flex-col border-r border-sidebar-border bg-sidebar lg:flex">
      <Brand />
      <NavLinks />
      <div className="flex-1" />
      <SidebarFooter />
    </aside>
  )
}

/** Off-canvas sidebar for small screens. */
export function MobileSidebar() {
  const sidebarOpen = useUiStore((s) => s.sidebarOpen)
  const closeSidebar = useUiStore((s) => s.closeSidebar)

  if (!sidebarOpen) {
    return null
  }

  return (
    <div className="fixed inset-0 z-50 lg:hidden">
      <div
        className="absolute inset-0 bg-black/50"
        aria-hidden="true"
        onClick={closeSidebar}
      />
      <aside className="absolute inset-y-0 left-0 flex w-64 flex-col border-r border-sidebar-border bg-sidebar shadow-xl">
        <Brand />
        <NavLinks onNavigate={closeSidebar} />
        <div className="flex-1" />
        <SidebarFooter />
      </aside>
    </div>
  )
}