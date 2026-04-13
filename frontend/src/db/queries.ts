import { db } from './index'
import type { EstadoCompetenciaDto, GrillaAtletaDto } from '../api/competencia'
import type { GrillaCacheRecord } from './schema'

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
