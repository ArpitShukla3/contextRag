import type React from 'react'
import { useEffect } from 'react'
import { useUiStore } from '@/stores/uiStore'

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const theme = useUiStore((s) => s.theme)

  useEffect(() => {
    const root = document.documentElement
    root.classList.remove('light', 'dark')
    root.classList.add(theme)
    root.style.colorScheme = theme
  }, [theme])

  return children
}