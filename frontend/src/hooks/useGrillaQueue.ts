import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { getCommandsByCompetencia } from '../db/queries'
import type { ComandoQueueRecord } from '../db/schema'
import type { GrillaAtletaDto } from '../api/competencia'

export type { ComandoQueueRecord }

function parsePayload(payload: string): Record<string, unknown> {
  try {
    return JSON.parse(payload) as Record<string, unknown>
  } catch {
    return {}
  }
}

export function projectedEstado(
  tipo: ComandoQueueRecord['tipo'],
  payload: Record<string, unknown>,
): GrillaAtletaDto['estado'] {
  if (tipo === 'llamar') return 'Llamada'
  if (tipo === 'resultado') return 'ResultadoRegistrado'
  if (tipo === 'dns') return 'DNS'
  if (tipo === 'resolver_revision') return 'Ejecutada'
  if (tipo === 'tarjeta') {
    return payload.tarjeta === 'Amarilla' ? 'EnRevision' : 'Ejecutada'
  }
  return 'AnunciadaAP'
}

export function useGrillaQueue(competenciaId: string | null | undefined) {
  const { data: queueData = [] } = useQuery({
    queryKey: ['comando-queue', competenciaId],
    enabled: Boolean(competenciaId),
    queryFn: () => getCommandsByCompetencia(competenciaId!),
    refetchInterval: 1000,
  })

  const pendingByAtleta = useMemo(() => {
    const map = new Map<string, number>()
    for (const cmd of queueData) {
      const payload = parsePayload(cmd.payload)
      const participanteId = String(payload.participante_id ?? '')
      if (!participanteId) continue
      map.set(participanteId, (map.get(participanteId) ?? 0) + 1)
    }
    return map
  }, [queueData])

  return { queueData, pendingByAtleta, projectedEstado }
}
