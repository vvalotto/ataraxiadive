import { useQuery } from '@tanstack/react-query'
import { fetchHealth } from '../api/health'

export function HealthCheck() {
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

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium"
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
