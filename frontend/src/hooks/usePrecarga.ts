import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  fetchEstadoCompetencia,
  fetchGrillaCompetencia,
  type EstadoCompetenciaDto,
  type GrillaAtletaDto,
} from '../api/competencia'
import { getGrillaCache, setGrillaCache } from '../db/queries'

const CACHE_MAX_AGE_MS = 24 * 60 * 60 * 1000

type PrecargaErrorCode = 'NO_CACHE_OFFLINE' | 'PRECARGA_FAILED'

export interface PrecargaPayload {
  grilla: GrillaAtletaDto[]
  estado: EstadoCompetenciaDto
  cachedAt: number
  source: 'server' | 'cache'
  cacheAgeMinutes: number
  isCacheExpired: boolean
  errorCode: PrecargaErrorCode | null
}

interface PrecargaError extends Error {
  code: PrecargaErrorCode
}

function createPrecargaError(code: PrecargaErrorCode, message: string): PrecargaError {
  const error = new Error(message) as PrecargaError
  error.code = code
  return error
}

interface UsePrecargaInput {
  competenciaId: string | null
  disciplina: string | null
  isOnline: boolean
}

export function usePrecarga({ competenciaId, disciplina, isOnline }: UsePrecargaInput) {
  const query = useQuery({
    queryKey: ['precarga', competenciaId, disciplina, isOnline],
    enabled: Boolean(competenciaId && disciplina),
    queryFn: async (): Promise<PrecargaPayload> => {
      const key = {
        competenciaId: competenciaId!,
        disciplina: disciplina!,
      }

      if (!isOnline) {
        const cached = await getGrillaCache(key)
        if (!cached) {
          throw createPrecargaError(
            'NO_CACHE_OFFLINE',
            'Sin datos disponibles. Conectate a internet para cargar la disciplina por primera vez.',
          )
        }

        const ageMs = Date.now() - cached.cached_at
        return {
          grilla: cached.grilla,
          estado: cached.estado,
          cachedAt: cached.cached_at,
          source: 'cache',
          cacheAgeMinutes: Math.floor(ageMs / 60000),
          isCacheExpired: ageMs > CACHE_MAX_AGE_MS,
          errorCode: null,
        }
      }

      try {
        const [grilla, estado] = await Promise.all([
          fetchGrillaCompetencia(competenciaId!, disciplina!),
          fetchEstadoCompetencia(competenciaId!, disciplina!),
        ])
        const cached = await setGrillaCache(key, { grilla, estado })

        return {
          grilla,
          estado,
          cachedAt: cached.cached_at,
          source: 'server',
          cacheAgeMinutes: 0,
          isCacheExpired: false,
          errorCode: null,
        }
      } catch {
        const cached = await getGrillaCache(key)
        if (!cached) {
          throw createPrecargaError(
            'PRECARGA_FAILED',
            'No se pudo cargar la grilla ni recuperar cache local.',
          )
        }

        const ageMs = Date.now() - cached.cached_at
        return {
          grilla: cached.grilla,
          estado: cached.estado,
          cachedAt: cached.cached_at,
          source: 'cache',
          cacheAgeMinutes: Math.floor(ageMs / 60000),
          isCacheExpired: ageMs > CACHE_MAX_AGE_MS,
          errorCode: 'PRECARGA_FAILED',
        }
      }
    },
  })

  const cacheAgeLabel = useMemo(() => {
    if (!query.data) return null
    const minutes = query.data.cacheAgeMinutes
    if (minutes < 1) return 'Datos actualizados hace instantes'
    if (minutes < 60) return `Datos actualizados hace ${minutes} min`
    const hours = Math.floor(minutes / 60)
    return `Datos actualizados hace ${hours}h`
  }, [query.data])

  const errorCode = query.error && 'code' in query.error ? (query.error.code as PrecargaErrorCode) : null

  return {
    ...query,
    payload: query.data ?? null,
    isCacheExpired: query.data?.isCacheExpired ?? false,
    cacheAgeLabel,
    errorCode,
  }
}
