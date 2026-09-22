import { createBrowserRouter } from 'react-router-dom'
import { AppLayout } from '@/components/layout/app-layout'
import { ChatPage } from '@/pages/ChatPage'
import { DocumentsPage } from '@/pages/DocumentsPage'
import { HomePage } from '@/pages/HomePage'
import { SettingsPage } from '@/pages/SettingsPage'

export const router = createBrowserRouter([
  {
    element: <AppLayout />,
    children: [
      { path: '/', element: <HomePage /> },
      { path: '/chat', element: <ChatPage /> },
      { path: '/documents', element: <DocumentsPage /> },
      { path: '/settings', element: <SettingsPage /> },
    ],
  },
])