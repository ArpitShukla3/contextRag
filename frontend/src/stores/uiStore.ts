import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type Theme = 'light' | 'dark'

interface UiState {
  theme: Theme
  sidebarOpen: boolean
  setTheme: (theme: Theme) => void
  openSidebar: () => void
  closeSidebar: () => void
}

export const useUiStore = create<UiState>()(
  persist(
    (set) => ({
      theme: 'light',
      sidebarOpen: false,
      setTheme: (theme) => set({ theme }),
      openSidebar: () => set({ sidebarOpen: true }),
      closeSidebar: () => set({ sidebarOpen: false }),
    }),
    {
      name: 'contextual-rag-ui',
      partialize: (s) => ({ theme: s.theme }),
    },
  ),
)