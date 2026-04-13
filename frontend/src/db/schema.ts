import type { EstadoCompetenciaDto, GrillaAtletaDto } from '../api/competencia'

export interface GrillaCacheRecord {
  id?: number
  competencia_id: string
  disciplina: string
  grilla: GrillaAtletaDto[]
  estado: EstadoCompetenciaDto
  cached_at: number
}

export interface ComandoQueueRecord {
  id?: number
  tipo: 'llamar' | 'resultado' | 'tarjeta' | 'dns' | 'resolver_revision'
  competencia_id: string
  payload: string
  estado: 'pendiente' | 'enviando' | 'error'
  creado_at: number
  intentos: number
  error_mensaje?: string
}
