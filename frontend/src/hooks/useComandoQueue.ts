import type { GrillaAtletaDto } from '../api/competencia'
import useConnectionStore from '../stores/useConnectionStore'
import {
  applyOptimisticEstadoToCache,
  enqueueCommand,
  getPendingCount,
} from '../db/queries'

type ComandoTipo = 'llamar' | 'resultado' | 'tarjeta' | 'dns' | 'resolver_revision'

interface BasePayload {
  participante_id: string
  disciplina: string
  [key: string]: unknown
}

function resolveOptimisticEstado(
  tipo: ComandoTipo,
  payload: BasePayload,
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

export function useComandoQueue() {
  const isOnline = useConnectionStore((s) => s.isOnline)
  const pendingCount = useConnectionStore((s) => s.pendingCount)
  const setPendingCount = useConnectionStore((s) => s.setPendingCount)

  const refreshPendingCount = async () => {
    const count = await getPendingCount()
    setPendingCount(count)
  }

  async function ejecutar<T>(
    tipo: ComandoTipo,
    competenciaId: string,
    payload: BasePayload,
    apiFn: () => Promise<T>,
  ): Promise<{ encolado: boolean }> {
    const mustQueue = !isOnline || pendingCount > 0

    if (!mustQueue) {
      await apiFn()
      return { encolado: false }
    }

    try {
      await enqueueCommand({
        tipo,
        competencia_id: competenciaId,
        payload: JSON.stringify(payload),
      })
      await applyOptimisticEstadoToCache({
        competenciaId,
        disciplina: payload.disciplina,
        participanteId: payload.participante_id,
        nextEstado: resolveOptimisticEstado(tipo, payload),
      })
      await refreshPendingCount()
      return { encolado: true }
    } catch {
      throw new Error('No se pudo guardar localmente — dispositivo sin espacio')
    }
  }

  return {
    ejecutar,
    refreshPendingCount,
  }
}
