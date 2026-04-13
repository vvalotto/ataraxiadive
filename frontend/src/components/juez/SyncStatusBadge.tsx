import useConnectionStore from '../../stores/useConnectionStore'

export function SyncStatusBadge() {
  const pendingCount = useConnectionStore((s) => s.pendingCount)
  const errorCount = useConnectionStore((s) => s.errorCount)
  const isSyncing = useConnectionStore((s) => s.isSyncing)
  const syncError = useConnectionStore((s) => s.syncError)
  const syncOkVisible = useConnectionStore((s) => s.syncOkVisible)

  if (syncError || errorCount > 0) {
    return (
      <span className="rounded-full border border-red-400/40 bg-red-500/15 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-red-100">
        ⚠ Error {errorCount > 0 ? `(${errorCount})` : ''}
      </span>
    )
  }

  if (isSyncing) {
    return (
      <span className="rounded-full border border-cyan-300/40 bg-cyan-400/15 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-cyan-100">
        ↻ Sincronizando
      </span>
    )
  }

  if (pendingCount > 0) {
    return (
      <span className="rounded-full border border-amber-300/40 bg-amber-400/15 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-amber-100">
        ⏳ {pendingCount} pendientes
      </span>
    )
  }

  if (syncOkVisible) {
    return (
      <span className="rounded-full border border-emerald-300/40 bg-emerald-400/15 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-emerald-100">
        ✓ Sincronizado
      </span>
    )
  }

  return null
}
