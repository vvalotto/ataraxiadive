import { db } from './index'
import type { EstadoCompetenciaDto, GrillaAtletaDto } from '../api/competencia'
import type { ComandoQueueRecord, GrillaCacheRecord } from './schema'

interface GrillaCacheKey {
  competenciaId: string
  disciplina: string
}

function normalizeKey(key: GrillaCacheKey) {
  return [key.competenciaId, key.disciplina] as [string, string]
}

export async function getGrillaCache(key: GrillaCacheKey): Promise<GrillaCacheRecord | null> {
  const record = await db.grilla_cache
    .where('[competencia_id+disciplina]')
    .equals(normalizeKey(key))
    .first()

  return record ?? null
}

export async function setGrillaCache(
  key: GrillaCacheKey,
  payload: { grilla: GrillaAtletaDto[]; estado: EstadoCompetenciaDto; cachedAt?: number },
): Promise<GrillaCacheRecord> {
  const cachedAt = payload.cachedAt ?? Date.now()
  const existing = await getGrillaCache(key)

  const nextRecord: GrillaCacheRecord = {
    id: existing?.id,
    competencia_id: key.competenciaId,
    disciplina: key.disciplina,
    grilla: payload.grilla,
    estado: payload.estado,
    cached_at: cachedAt,
  }

  await db.grilla_cache.put(nextRecord)
  return nextRecord
}

export async function enqueueCommand(
  payload: Omit<ComandoQueueRecord, 'id' | 'estado' | 'creado_at' | 'intentos'>,
): Promise<number | undefined> {
  return db.comando_queue.add({
    tipo: payload.tipo,
    competencia_id: payload.competencia_id,
    payload: payload.payload,
    estado: 'pendiente',
    creado_at: Date.now(),
    intentos: 0,
  })
}

export async function getPendingCount(): Promise<number> {
  return db.comando_queue.where('estado').equals('pendiente').count()
}

export async function getErrorCount(): Promise<number> {
  return db.comando_queue.where('estado').equals('error').count()
}

export async function getCommandsByCompetencia(competenciaId: string): Promise<ComandoQueueRecord[]> {
  return db.comando_queue
    .filter((cmd) => cmd.competencia_id === competenciaId)
    .sortBy('id')
}

export async function getPendingCommands(): Promise<ComandoQueueRecord[]> {
  return db.comando_queue.where('estado').equals('pendiente').sortBy('id')
}

export async function markCommandSending(id: number): Promise<void> {
  await db.comando_queue.update(id, { estado: 'enviando' })
}

export async function markCommandPending(id: number, intentos: number): Promise<void> {
  await db.comando_queue.update(id, { estado: 'pendiente', intentos })
}

export async function markCommandError(id: number, errorMensaje: string, intentos: number): Promise<void> {
  await db.comando_queue.update(id, {
    estado: 'error',
    error_mensaje: errorMensaje,
    intentos,
  })
}

export async function removeCommand(id: number): Promise<void> {
  await db.comando_queue.delete(id)
}

export async function applyOptimisticEstadoToCache(input: {
  competenciaId: string
  disciplina: string
  participanteId: string
  nextEstado: GrillaAtletaDto['estado']
}): Promise<void> {
  const cached = await getGrillaCache({
    competenciaId: input.competenciaId,
    disciplina: input.disciplina,
  })
  if (!cached) return

  const nextGrilla = cached.grilla.map((atleta) =>
    atleta.atleta_id === input.participanteId ? { ...atleta, estado: input.nextEstado } : atleta,
  )

  await setGrillaCache(
    {
      competenciaId: input.competenciaId,
      disciplina: input.disciplina,
    },
    {
      grilla: nextGrilla,
      estado: cached.estado,
      cachedAt: cached.cached_at,
    },
  )
}
