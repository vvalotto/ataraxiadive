import type { GrillaAtletaDto } from '../api/competencia'
import useConnectionStore from '../stores/useConnectionStore'
import {
  applyOptimisticEstadoToCache,
  enqueueCommand,
  getErrorCount,
  getPendingCount,
} from '../db/queries'
import { ApiError } from '../api/competencia'

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
  const errorCount = useConnectionStore((s) => s.errorCount)
  const setPendingCount = useConnectionStore((s) => s.setPendingCount)
  const setErrorCount = useConnectionStore((s) => s.setErrorCount)
  const setSyncError = useConnectionStore((s) => s.setSyncError)
  const setSyncOkVisible = useConnectionStore((s) => s.setSyncOkVisible)

  const refreshPendingCount = async () => {
    const [pending, errors] = await Promise.all([getPendingCount(), getErrorCount()])
    setPendingCount(pending)
    setErrorCount(errors)
  }

  async function ejecutar<T>(
    tipo: ComandoTipo,
    competenciaId: string,
    payload: BasePayload,
    apiFn: () => Promise<T>,
  ): Promise<{ encolado: boolean }> {
    const persistedPending = await getPendingCount()
    const persistedErrors = await getErrorCount()
    const mustQueue =
      !isOnline ||
      pendingCount > 0 ||
      errorCount > 0 ||
      persistedPending > 0 ||
      persistedErrors > 0

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
      setSyncError(null)
      setSyncOkVisible(false)
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
