import { getToken } from './tokenProvider'

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

export interface TorneoDto {
  torneo_id: string
  nombre: string
  descripcion: string
  fecha_inicio: string
  fecha_fin: string
  sede: {
    nombre: string
    ciudad: string
    pais: string
  }
  entidad_organizadora: {
    nombre: string
    tipo: string
  }
  estado: string
}

export type DisciplinaCodigo =
  | 'STA'
  | 'DNF'
  | 'DYN'
  | 'DBF'
  | 'SPE_2X50'
  | 'SPE_4X50'
  | 'SPE_8X50'
  | 'SPE_16X50'

export interface CrearTorneoPayload {
  nombre: string
  descripcion: string
  fecha_inicio: string
  fecha_fin: string
  sede: {
    nombre: string
    ciudad: string
    pais: string
  }
  entidad_organizadora: {
    nombre: string
    tipo: string
  }
}

export interface CrearTorneoResponse {
  torneo_id: string
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

function formatDetail(detail: unknown, fallback: string): string {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (item && typeof item === 'object' && 'msg' in item) {
          return String((item as { msg: unknown }).msg)
        }
        return String(item)
      })
      .join('. ')
  }
  return fallback
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (response.ok) {
    if (response.status === 204) {
      return undefined as T
    }
    return response.json() as Promise<T>
  }

  const fallback = `Error de API: ${response.status}`

  try {
    const payload = (await response.json()) as { detail?: unknown }
    throw new ApiError(response.status, formatDetail(payload.detail, fallback))
  } catch (error) {
    if (error instanceof ApiError) throw error
    throw new ApiError(response.status, fallback)
  }
}

export async function fetchTorneos(): Promise<TorneoDto[]> {
  const response = await fetch('/torneos')
  return parseResponse<TorneoDto[]>(response)
}

export async function fetchTorneo(torneoId: string): Promise<TorneoDto> {
  const response = await fetch(`/torneos/${torneoId}`)
  return parseResponse<TorneoDto>(response)
}

export async function crearTorneo(payload: CrearTorneoPayload): Promise<CrearTorneoResponse> {
  const response = await fetch('/torneos', {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify(payload),
  })

  return parseResponse<CrearTorneoResponse>(response)
}

export async function asignarDisciplinas(
  torneoId: string,
  disciplinas: DisciplinaCodigo[],
): Promise<void> {
  const response = await fetch(`/torneos/${torneoId}/disciplinas`, {
    method: 'PUT',
    headers: buildHeaders(),
    body: JSON.stringify({ disciplinas }),
  })

  await parseResponse<{ ok: boolean }>(response)
}

export async function fetchDisciplinasDeJuez(
  torneoId: string,
  juezId: string,
): Promise<string[]> {
  const response = await fetch(`/torneos/${torneoId}/jueces/${juezId}/disciplinas`)
  return parseResponse<string[]>(response)
}
