import type { DisciplinaCodigo } from './torneo'
import { getToken, handleUnauthorized } from './tokenProvider'

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

export interface InscriptoDto {
  inscripcion_id: string
  atleta_id: string
  torneo_id: string
  disciplinas: string[]
  estado: string
  fecha_inscripcion: string
}

export interface AtletaDto {
  atleta_id: string
  nombre: string
  apellido: string
  email: string
  fecha_nacimiento: string
  categoria: string
  club: string
  brevet: string | null
}

export interface InscriptoDetalleDto {
  inscripcion_id: string
  atleta_id: string
  nombre: string
  apellido: string
  categoria: string
  club: string
  disciplinas: string[]
  estado: string
}

export interface InscribirAtletaPayload {
  atletaId: string
  torneoId: string
  disciplinas: DisciplinaCodigo[]
}

export interface InscribirAtletaResponse {
  inscripcion_id: string
}

function buildHeaders(): Record<string, string> {
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

  if (response.status === 401) {
    handleUnauthorized()
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

export async function listarInscriptos(torneoId: string): Promise<InscriptoDto[]> {
  const response = await fetch(`/registro/torneos/${torneoId}/inscriptos`, {
    headers: buildHeaders(),
  })
  return parseResponse<InscriptoDto[]>(response)
}

export async function listarInscriptosDetalle(torneoId: string): Promise<InscriptoDetalleDto[]> {
  const response = await fetch(`/registro/torneos/${torneoId}/inscriptos-detalle`, {
    headers: buildHeaders(),
  })
  return parseResponse<InscriptoDetalleDto[]>(response)
}

export async function fetchAtleta(atletaId: string): Promise<AtletaDto> {
  const response = await fetch(`/registro/atletas/${atletaId}`, {
    headers: buildHeaders(),
  })
  return parseResponse<AtletaDto>(response)
}

export async function inscribirAtleta(
  payload: InscribirAtletaPayload,
): Promise<InscribirAtletaResponse> {
  const response = await fetch('/registro/inscripciones', {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify({
      atleta_id: payload.atletaId,
      torneo_id: payload.torneoId,
      disciplinas: payload.disciplinas,
    }),
  })
  return parseResponse<InscribirAtletaResponse>(response)
}
