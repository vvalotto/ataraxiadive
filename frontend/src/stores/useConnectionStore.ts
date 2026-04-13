import { create } from 'zustand'
import { useEffect } from 'react'
import { getErrorCount, getPendingCount } from '../db/queries'

interface ConnectionState {
  isOnline: boolean
  pendingCount: number
  errorCount: number
  isSyncing: boolean
  syncError: string | null
  syncOkVisible: boolean
  setOnline: (value: boolean) => void
  setPendingCount: (value: number) => void
  setErrorCount: (value: number) => void
  setSyncing: (value: boolean) => void
  setSyncError: (value: string | null) => void
  setSyncOkVisible: (value: boolean) => void
}

const useConnectionStore = create<ConnectionState>((set) => ({
  isOnline: navigator.onLine,
  pendingCount: 0,
  errorCount: 0,
  isSyncing: false,
  syncError: null,
  syncOkVisible: false,
  setOnline: (value) => set({ isOnline: value }),
  setPendingCount: (value) => set({ pendingCount: value }),
  setErrorCount: (value) => set({ errorCount: value }),
  setSyncing: (value) => set({ isSyncing: value }),
  setSyncError: (value) => set({ syncError: value }),
  setSyncOkVisible: (value) => set({ syncOkVisible: value }),
}))

export function useConnectionSync(): void {
  const setOnline = useConnectionStore((s) => s.setOnline)
  const setPendingCount = useConnectionStore((s) => s.setPendingCount)
  const setErrorCount = useConnectionStore((s) => s.setErrorCount)

  useEffect(() => {
    const refreshPending = async () => {
      try {
        const [pending, errors] = await Promise.all([getPendingCount(), getErrorCount()])
        setPendingCount(pending)
        setErrorCount(errors)
      } catch {
        setPendingCount(0)
        setErrorCount(0)
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
  }, [setOnline, setPendingCount, setErrorCount])
}

export default useConnectionStore
