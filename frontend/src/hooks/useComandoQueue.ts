import type { GrillaAtletaDto } from '../api/competencia'
import useConnectionStore from '../stores/useConnectionStore'
import {
  applyOptimisticEstadoToCache,
  enqueueCommand,
  getPendingCount,
} from '../db/queries'
import { ApiError } from '../api/competencia'

type ComandoTipo = 'llamar' | 'resultado' | 'tarjeta' | 'dns' | 'resolver_revision'
const ONLINE_CALL_TIMEOUT_MS = 2500

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
    const persistedPending = await getPendingCount()
    const enqueueWithOptimisticState = async (): Promise<{ encolado: boolean }> => {
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
    }

    const mustQueue = !isOnline || pendingCount > 0 || persistedPending > 0

    if (mustQueue) {
      try {
        return await enqueueWithOptimisticState()
      } catch {
        throw new Error('No se pudo guardar localmente — dispositivo sin espacio')
      }
    }

    try {
      await Promise.race([
        apiFn(),
        new Promise<never>((_, reject) => {
          setTimeout(() => reject(new Error('Timeout online, fallback a cola local')), ONLINE_CALL_TIMEOUT_MS)
        }),
      ])
      await applyOptimisticEstadoToCache({
        competenciaId,
        disciplina: payload.disciplina,
        participanteId: payload.participante_id,
        nextEstado: resolveOptimisticEstado(tipo, payload),
      })
      return { encolado: false }
    } catch (error) {
      if (error instanceof ApiError) {
        throw error
      }
      try {
        return await enqueueWithOptimisticState()
      } catch {
        throw new Error('No se pudo guardar localmente — dispositivo sin espacio')
      }
    }
  }

  return {
    ejecutar,
    refreshPendingCount,
  }
}
