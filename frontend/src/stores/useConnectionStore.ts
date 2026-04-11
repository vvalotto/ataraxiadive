import { create } from 'zustand'
import { useEffect } from 'react'

interface ConnectionState {
  isOnline: boolean
  setOnline: (value: boolean) => void
}

const useConnectionStore = create<ConnectionState>((set) => ({
  isOnline: navigator.onLine,
  setOnline: (value) => set({ isOnline: value }),
}))

export function useConnectionSync(): void {
  const setOnline = useConnectionStore((s) => s.setOnline)

  useEffect(() => {
    const onOnline = () => setOnline(true)
    const onOffline = () => setOnline(false)
    window.addEventListener('online', onOnline)
    window.addEventListener('offline', onOffline)
    return () => {
      window.removeEventListener('online', onOnline)
      window.removeEventListener('offline', onOffline)
    }
  }, [setOnline])
}

export default useConnectionStore
