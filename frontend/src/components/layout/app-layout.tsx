import { Outlet, useLocation } from 'react-router-dom'
import { Header } from '@/components/layout/header'
import { MobileSidebar, Sidebar } from '@/components/layout/sidebar'

export function AppLayout() {
  const { pathname } = useLocation()

  return (
    <div className="flex h-full overflow-hidden">
      <Sidebar />
      <MobileSidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Header pathname={pathname} />
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}