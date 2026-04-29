import { useQuery } from '@tanstack/react-query'
import { fetchHealth } from '../api/health'

interface HealthCheckProps {
  compact?: boolean
}

export function HealthCheck({ compact = false }: HealthCheckProps) {
  const { data, isError, isPending } = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
    refetchInterval: 30_000,
    retry: 1,
  })

  const isOnline = !isError && !isPending && data?.status === 'ok'
  const label = isPending
    ? 'Backend: comprobando...'
    : isOnline
      ? 'Backend: ✓ online'
      : 'Backend: ✗ sin conexión'

  if (compact) {
    return (
      <div
        className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[12px] font-semibold"
        style={{
          backgroundColor: isPending ? 'rgba(51, 65, 85, 0.9)' : isOnline ? 'rgba(34, 197, 94, 0.15)' : 'rgba(239, 68, 68, 0.16)',
          color: isPending ? '#cbd5e1' : isOnline ? '#4ade80' : '#fca5a5',
        }}
      >
        <span
          className="h-2 w-2 rounded-full"
          style={{
            backgroundColor: isPending ? '#94a3b8' : isOnline ? '#22c55e' : '#ef4444',
          }}
        />
        {isOnline ? 'En línea' : isPending ? 'Comprobando' : 'Sin conexión'}
      </div>
    )
  }

  return (
    <div
      className="flex items-center gap-2 rounded-full px-3 py-1.5 text-sm font-medium"
      style={{
        backgroundColor: isPending ? '#f3f4f6' : isOnline ? '#dcfce7' : '#fee2e2',
        color: isPending ? '#6b7280' : isOnline ? '#166534' : '#991b1b',
      }}
    >
      <span
        className="w-2 h-2 rounded-full"
        style={{
          backgroundColor: isPending ? '#d1d5db' : isOnline ? '#16a34a' : '#dc2626',
        }}
      />
      {label}
    </div>
  )
}
