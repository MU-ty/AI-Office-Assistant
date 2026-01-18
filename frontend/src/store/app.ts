import { create } from 'zustand'

interface AppState {
  theme: 'light' | 'dark'
  isLoading: boolean
  setTheme: (theme: 'light' | 'dark') => void
  setLoading: (loading: boolean) => void
}

export const useAppStore = create<AppState>((set) => ({
  theme: 'light',
  isLoading: false,
  setTheme: (theme) => set({ theme }),
  setLoading: (isLoading) => set({ isLoading }),
}))
