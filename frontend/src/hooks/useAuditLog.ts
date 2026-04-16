import { useQuery } from '@tanstack/react-query'
import { fetchAuditLog } from '../api/competencia'

export function useAuditLog(competenciaId: string | undefined, atletaId: string | undefined) {
  return useQuery({
    queryKey: ['audit-log', competenciaId, atletaId],
    queryFn: () => fetchAuditLog(competenciaId!, atletaId!),
    enabled: Boolean(competenciaId && atletaId),
  })
}
