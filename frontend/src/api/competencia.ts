import type { EstadoPerformance } from '../types/auth'
import { getToken } from './tokenProvider'

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

export interface CompetenciaResumenDto {
  competencia_id: string
  disciplina: string
  torneo_id: string
}

export interface CrearCompetenciaPayload {
  competenciaId: string
  disciplina: string
  intervaloMinutos: number
  configuradoPor: string
  torneoId: string
}

export interface CrearCompetenciaResponse {
  competencia_id: string
}

export interface CambioGrillaPayload {
  performance_id: string
  campo: 'posicion_grilla' | 'andarivel'
  valor_nuevo: number
}

export interface EstadoCompetenciaDto {
  estado: string
  intervalo_minutos: number | null
  grilla_confirmada: boolean
  torneo_id: string | null
  hash_sha256: string | null
}

export interface GrillaAtletaDto {
  performance_id: string
  atleta_id: string
  nombre_atleta: string
  posicion: number
  andarivel: number
  ot_programado: string
  ap_declarado: string
  unidad: string
  estado: EstadoPerformance
  tarjeta_asignada: string | null
}

export interface PerformanceActualDto {
  performance_id: string
  nombre_atleta: string
  ap_declarado: string
  unidad: string
  unidad_esperada: string
  andarivel: number
  estado: EstadoPerformance
}

export interface PenalizacionPayload {
  tipo: string
  deduccion: string
}

export interface AuditLogEventoDto {
  sequence: number
  tipo: string
  timestamp: string
  datos: Record<string, unknown>
}

export interface AuditLogDto {
  competencia_id: string
  atleta_id: string
  atleta_nombre: string
  disciplina: string
  eventos: AuditLogEventoDto[]
}

function buildHeaders() {
  const token = getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  return headers
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (response.ok) {
    if (response.status === 204) {
      return undefined as T
    }
    return response.json() as Promise<T>
  }

  let detail = `Error de API: ${response.status}`

  try {
    const payload = (await response.json()) as { detail?: string }
    if (payload.detail) {
      detail = payload.detail
    }
  } catch {
    // sin body JSON util
  }

  throw new ApiError(response.status, detail)
}

export async function fetchCompetenciasPorTorneo(
  torneoId: string,
): Promise<CompetenciaResumenDto[]> {
  const response = await fetch(`/competencia?torneo_id=${torneoId}`)
  return parseResponse<CompetenciaResumenDto[]>(response)
}

export async function crearCompetencia(
  payload: CrearCompetenciaPayload,
): Promise<CrearCompetenciaResponse> {
  const response = await fetch('/competencia', {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify({
      competencia_id: payload.competenciaId,
      disciplina: payload.disciplina,
      intervalo_minutos: payload.intervaloMinutos,
      configurado_por: payload.configuradoPor,
      torneo_id: payload.torneoId,
    }),
  })

  return parseResponse<CrearCompetenciaResponse>(response)
}

export async function fetchEstadoCompetencia(
  competenciaId: string,
  disciplina: string,
): Promise<EstadoCompetenciaDto> {
  const response = await fetch(
    `/competencia/${competenciaId}/estado?disciplina=${encodeURIComponent(disciplina)}`,
  )
  return parseResponse<EstadoCompetenciaDto>(response)
}

export async function fetchAuditLog(
  competenciaId: string,
  atletaId: string,
): Promise<AuditLogDto> {
  const response = await fetch(
    `/competencia/${competenciaId}/performances/${atletaId}/audit-log`,
    {
      headers: buildHeaders(),
    },
  )
  return parseResponse<AuditLogDto>(response)
}

export async function fetchGrillaCompetencia(
  competenciaId: string,
  disciplina: string,
): Promise<GrillaAtletaDto[]> {
  const response = await fetch(
    `/competencia/${competenciaId}/grilla?disciplina=${encodeURIComponent(disciplina)}`,
  )
  return parseResponse<GrillaAtletaDto[]>(response)
}

export async function generarGrilla(payload: {
  competenciaId: string
  disciplina: string
  otInicio: string
  andariveles?: number
}): Promise<void> {
  const response = await fetch(`/competencia/${payload.competenciaId}/generar-grilla`, {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify({
      disciplina: payload.disciplina,
      ot_inicio: payload.otInicio,
      andariveles: payload.andariveles ?? 1,
    }),
  })

  await parseResponse<void>(response)
}

export async function ajustarGrilla(payload: {
  competenciaId: string
  disciplina: string
  cambios: CambioGrillaPayload[]
}): Promise<void> {
  const response = await fetch(`/competencia/${payload.competenciaId}/ajustar-grilla`, {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify({
      disciplina: payload.disciplina,
      cambios: payload.cambios,
    }),
  })

  await parseResponse<void>(response)
}

export async function confirmarGrilla(payload: {
  competenciaId: string
  disciplina: string
}): Promise<void> {
  const response = await fetch(`/competencia/${payload.competenciaId}/confirmar-grilla`, {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify({
      disciplina: payload.disciplina,
    }),
  })

  await parseResponse<void>(response)
}

export async function fetchPerformanceActual(
  competenciaId: string,
): Promise<PerformanceActualDto | null> {
  const response = await fetch(`/competencia/${competenciaId}/performance/actual`)
  return parseResponse<PerformanceActualDto | null>(response)
}

export async function llamarAtleta(payload: {
  competenciaId: string
  participanteId: string
  disciplina: string
  otProgramado: string
  posicionGrilla: number
  andarivel: number
}): Promise<void> {
  const response = await fetch(`/competencia/${payload.competenciaId}/llamar`, {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify({
      participante_id: payload.participanteId,
      disciplina: payload.disciplina,
      ot_programado: payload.otProgramado,
      posicion_grilla: payload.posicionGrilla,
      andarivel: payload.andarivel,
    }),
  })

  await parseResponse<void>(response)
}

export async function registrarResultado(payload: {
  competenciaId: string
  participanteId: string
  disciplina: string
  valorRp: string
  unidad: string
}): Promise<void> {
  const response = await fetch(`/competencia/${payload.competenciaId}/registrar-resultado`, {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify({
      participante_id: payload.participanteId,
      disciplina: payload.disciplina,
      valor_rp: payload.valorRp,
      unidad: payload.unidad,
    }),
  })

  await parseResponse<void>(response)
}

export async function registrarDns(payload: {
  competenciaId: string
  participanteId: string
  disciplina: string
}): Promise<void> {
  const response = await fetch(`/competencia/${payload.competenciaId}/registrar-dns`, {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify({
      participante_id: payload.participanteId,
      disciplina: payload.disciplina,
    }),
  })

  await parseResponse<void>(response)
}

export async function asignarTarjeta(payload: {
  competenciaId: string
  participanteId: string
  disciplina: string
  tarjeta: 'Blanca' | 'Roja' | 'BlancaConPenalizaciones' | 'Amarilla'
  motivoDq?: string
  motivoTexto?: string
  distanciaBlackout?: string
  penalizaciones?: PenalizacionPayload[]
}): Promise<void> {
  const response = await fetch(`/competencia/${payload.competenciaId}/asignar-tarjeta`, {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify({
      participante_id: payload.participanteId,
      disciplina: payload.disciplina,
      tarjeta: payload.tarjeta,
      motivo_dq: payload.motivoDq ?? null,
      motivo_texto: payload.motivoTexto ?? null,
      distancia_blackout: payload.distanciaBlackout ?? null,
      penalizaciones: payload.penalizaciones ?? [],
    }),
  })

  await parseResponse<void>(response)
}

export async function resolverRevision(payload: {
  competenciaId: string
  participanteId: string
  disciplina: string
  resolucion: 'Blanca' | 'Roja'
  motivoDq?: string
}): Promise<void> {
  const response = await fetch(`/competencia/${payload.competenciaId}/resolver-revision`, {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify({
      participante_id: payload.participanteId,
      disciplina: payload.disciplina,
      resolucion: payload.resolucion,
      motivo_dq: payload.motivoDq ?? null,
      penalizaciones: [],
    }),
  })

  await parseResponse<void>(response)
}
