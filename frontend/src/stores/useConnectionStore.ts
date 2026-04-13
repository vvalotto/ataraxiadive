import { create } from 'zustand'
import { useEffect } from 'react'
import { getPendingCount } from '../db/queries'

interface ConnectionState {
  isOnline: boolean
  pendingCount: number
  setOnline: (value: boolean) => void
  setPendingCount: (value: number) => void
}

const useConnectionStore = create<ConnectionState>((set) => ({
  isOnline: navigator.onLine,
  pendingCount: 0,
  setOnline: (value) => set({ isOnline: value }),
  setPendingCount: (value) => set({ pendingCount: value }),
}))

export function useConnectionSync(): void {
  const setOnline = useConnectionStore((s) => s.setOnline)
  const setPendingCount = useConnectionStore((s) => s.setPendingCount)

  useEffect(() => {
    const refreshPending = async () => {
      try {
        const count = await getPendingCount()
        setPendingCount(count)
      } catch {
        setPendingCount(0)
      }
    }

    const onOnline = () => setOnline(true)
    const onOffline = () => setOnline(false)
    window.addEventListener('online', onOnline)
    window.addEventListener('offline', onOffline)
    void refreshPending()
    return () => {
      window.removeEventListener('online', onOnline)
      window.removeEventListener('offline', onOffline)
    }
  }, [setOnline, setPendingCount])
}

export default useConnectionStore
