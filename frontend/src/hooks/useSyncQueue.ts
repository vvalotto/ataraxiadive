import { useCallback, useEffect, useRef } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import useConnectionStore from '../stores/useConnectionStore'
import useCompetenciaStore from '../stores/useCompetenciaStore'
import { fetchEstadoCompetencia, fetchGrillaCompetencia } from '../api/competencia'
import {
  getErrorCount,
  getPendingCommands,
  getPendingCount,
  markCommandError,
  markCommandPending,
  markCommandSending,
  removeCommand,
  setGrillaCache,
} from '../db/queries'
import { getToken } from '../api/tokenProvider'

const SYNC_TAG = 'ataraxia-sync-queue'

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function isHttpClientError(status: number): boolean {
  return status >= 400 && status < 500
}

function isNetworkError(error: unknown): boolean {
  if (error instanceof DOMException && error.name === 'AbortError') return true
  if (error instanceof TypeError && error.message.toLowerCase().includes('network')) return true
  if (error instanceof Error && error.message === 'Network timeout') return true
  return false
}

function buildHeaders(): Record<string, string> {
  const token = getToken()
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }
  return headers
}

const POST_TIMEOUT_MS = 5000

async function postCommand(path: string, payload: object): Promise<Response> {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), POST_TIMEOUT_MS)
  try {
    return await fetch(path, {
      method: 'POST',
      headers: buildHeaders(),
      body: JSON.stringify(payload),
      signal: controller.signal,
    })
  } finally {
    clearTimeout(timer)
  }
}

function parsePayload(raw: string): Record<string, unknown> {
  try {
    return JSON.parse(raw) as Record<string, unknown>
  } catch {
    return {}
  }
}

function commandToRequest(tipo: string, competenciaId: string, payload: Record<string, unknown>) {
  if (tipo === 'llamar') {
    return {
      path: `/competencia/${competenciaId}/llamar`,
      body: payload,
    }
  }
  if (tipo === 'resultado') {
    return {
      path: `/competencia/${competenciaId}/registrar-resultado`,
      body: payload,
    }
  }
  if (tipo === 'tarjeta') {
    return {
      path: `/competencia/${competenciaId}/asignar-tarjeta`,
      body: payload,
    }
  }
  if (tipo === 'dns') {
    return {
      path: `/competencia/${competenciaId}/registrar-dns`,
      body: payload,
    }
  }
  return {
    path: `/competencia/${competenciaId}/resolver-revision`,
    body: payload,
  }
}

async function readErrorMessage(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as { detail?: string }
    return data.detail ?? `HTTP ${response.status}`
  } catch {
    return `HTTP ${response.status}`
  }
}

export function useSyncQueue() {
  const isOnline = useConnectionStore((s) => s.isOnline)
  const pendingCount = useConnectionStore((s) => s.pendingCount)
  const setPendingCount = useConnectionStore((s) => s.setPendingCount)
  const setErrorCount = useConnectionStore((s) => s.setErrorCount)
  const setSyncing = useConnectionStore((s) => s.setSyncing)
  const setSyncError = useConnectionStore((s) => s.setSyncError)
  const setSyncOkVisible = useConnectionStore((s) => s.setSyncOkVisible)
  const competenciaId = useCompetenciaStore((s) => s.competenciaId)
  const disciplinaActiva = useCompetenciaStore((s) => s.disciplinaActiva)
  const queryClient = useQueryClient()
  const syncInProgress = useRef(false)
  const successTimeoutRef = useRef<number | null>(null)

  const refreshCounters = useCallback(async () => {
    const [pending, errors] = await Promise.all([getPendingCount(), getErrorCount()])
    setPendingCount(pending)
    setErrorCount(errors)
  }, [setPendingCount, setErrorCount])

  const tryRegisterBackgroundSync = useCallback(async () => {
    if (!('serviceWorker' in navigator)) return
    try {
      const registration = await navigator.serviceWorker.ready
      const hasSync = 'sync' in registration
      if (hasSync) {
        await (registration as ServiceWorkerRegistration & {
          sync: { register: (tag: string) => Promise<void> }
        }).sync.register(SYNC_TAG)
      }
    } catch {
      // fallback por evento online desde la app
    }
  }, [])

  const refetchGrilla = useCallback(async () => {
    if (!competenciaId || !disciplinaActiva || !isOnline) return

    const [grilla, estado] = await Promise.all([
      fetchGrillaCompetencia(competenciaId, disciplinaActiva),
      fetchEstadoCompetencia(competenciaId, disciplinaActiva),
    ])

    await setGrillaCache(
      { competenciaId, disciplina: disciplinaActiva },
      { grilla, estado, cachedAt: Date.now() },
    )

    queryClient.setQueryData(
      ['precarga', competenciaId, disciplinaActiva],
      {
        grilla,
        estado,
        cachedAt: Date.now(),
        source: 'server',
        cacheAgeMinutes: 0,
        isCacheExpired: false,
        errorCode: null,
      },
    )
    await queryClient.invalidateQueries({ queryKey: ['precarga', competenciaId, disciplinaActiva] })
    await queryClient.invalidateQueries({ queryKey: ['performance-actual', competenciaId] })
    await queryClient.invalidateQueries({ queryKey: ['comando-queue', competenciaId] })
  }, [competenciaId, disciplinaActiva, isOnline, queryClient])

  const failCommand = useCallback(
    async (id: number, message: string, intentos: number) => {
      await markCommandError(id, message, intentos)
      await refreshCounters()
      setSyncError(message)
    },
    [refreshCounters, setSyncError],
  )

  const syncQueue = useCallback(async () => {
    if (syncInProgress.current) return
    syncInProgress.current = true
    setSyncing(true)
    setSyncError(null)
    setSyncOkVisible(false)

    try {
      while (true) {
        const pending = await getPendingCommands()
        const next = pending[0]
        if (!next || typeof next.id !== 'number') break

        const payload = parsePayload(next.payload)
        const request = commandToRequest(next.tipo, next.competencia_id, payload)
        await markCommandSending(next.id)

        let succeeded = false
        for (let attempt = 0; attempt < 3; attempt += 1) {
          try {
            const response = await postCommand(request.path, request.body)
            if (response.ok) {
              await removeCommand(next.id)
              succeeded = true
              break
            }

            if (isHttpClientError(response.status) || attempt === 2) {
              const message = await readErrorMessage(response)
              await failCommand(next.id, message, next.intentos + attempt + 1)
              return
            }

            await sleep(1000 * 2 ** attempt)
          } catch (error) {
            if (attempt === 2) {
              if (isNetworkError(error)) {
                // Red inalcanzable (timeout, abort, sin ruta) — no es un error permanente.
                // Volver a pendiente para reintentar cuando haya conexión real.
                await markCommandPending(next.id, next.intentos + attempt + 1)
                await refreshCounters()
                return
              }
              const msg = error instanceof Error ? error.message : 'Error de red'
              await failCommand(next.id, msg, next.intentos + attempt + 1)
              return
            }
            await sleep(1000 * 2 ** attempt)
          }
        }

        if (!succeeded) break
      }

      await refreshCounters()
      const remaining = await getPendingCount()
      if (remaining === 0) {
        await refetchGrilla()
        setSyncOkVisible(true)
        if (successTimeoutRef.current !== null) {
          window.clearTimeout(successTimeoutRef.current)
        }
        successTimeoutRef.current = window.setTimeout(() => setSyncOkVisible(false), 3000)
      }
    } finally {
      setSyncing(false)
      syncInProgress.current = false
    }
  }, [failCommand, refetchGrilla, refreshCounters, setSyncError, setSyncOkVisible, setSyncing])

  useEffect(() => {
    void refreshCounters()
  }, [refreshCounters])

  useEffect(() => {
    if (pendingCount > 0) {
      void tryRegisterBackgroundSync()
    }
  }, [pendingCount, tryRegisterBackgroundSync])

  useEffect(() => {
    if (!isOnline || pendingCount === 0) return
    void syncQueue()
  }, [isOnline, pendingCount, syncQueue])

  useEffect(() => {
    if (!('serviceWorker' in navigator)) return
    const onMessage = (event: MessageEvent) => {
      const type = (event.data as { type?: string } | null)?.type
      if (type === 'SYNC_QUEUE_REQUEST') {
        void syncQueue()
      }
    }
    navigator.serviceWorker.addEventListener('message', onMessage)
    return () => navigator.serviceWorker.removeEventListener('message', onMessage)
  }, [syncQueue])

  useEffect(() => {
    return () => {
      if (successTimeoutRef.current !== null) {
        window.clearTimeout(successTimeoutRef.current)
      }
    }
  }, [])

  return { syncQueue, refreshCounters }
}
