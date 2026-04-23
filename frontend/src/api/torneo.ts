import { getToken, handleUnauthorized } from './tokenProvider'

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
  estado: EstadoTorneo
}

type TorneoApiDto = Omit<TorneoDto, 'estado'> & {
  estado: unknown
}

export type EstadoTorneo =
  | 'CREADO'
  | 'INSCRIPCION_ABIERTA'
  | 'PREPARACION'
  | 'EJECUCION'
  | 'PREMIACION'
  | 'CERRADO'
  | 'CANCELADO'

const ESTADO_TORNEO_ALIASES: Record<string, EstadoTorneo> = {
  CREADO: 'CREADO',
  INSCRIPCION_ABIERTA: 'INSCRIPCION_ABIERTA',
  INSCRIPCIONABIERTA: 'INSCRIPCION_ABIERTA',
  PREPARACION: 'PREPARACION',
  EJECUCION: 'EJECUCION',
  ENEJECUCION: 'EJECUCION',
  PREMIACION: 'PREMIACION',
  CERRADO: 'CERRADO',
  CANCELADO: 'CANCELADO',
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

export interface DisciplinaTorneoDto {
  disciplina: DisciplinaCodigo
  juez_id: string | null
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

function normalizarClaveEstado(rawEstado: unknown): string {
  return String(rawEstado)
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-zA-Z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .toUpperCase()
}

function normalizarEstadoTorneo(rawEstado: unknown): EstadoTorneo {
  const normalized = normalizarClaveEstado(rawEstado)
  const compact = normalized.split('_').join('')
  const estado = ESTADO_TORNEO_ALIASES[normalized] ?? ESTADO_TORNEO_ALIASES[compact]

  if (!estado) {
    throw new ApiError(500, `Estado de torneo desconocido: ${String(rawEstado)}`)
  }

  return estado
}

function normalizarTorneo(torneo: TorneoApiDto): TorneoDto {
  return {
    ...torneo,
    estado: normalizarEstadoTorneo(torneo.estado),
  }
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
  const torneos = await parseResponse<TorneoApiDto[]>(response)
  return torneos.map(normalizarTorneo)
}

export async function fetchTorneo(torneoId: string): Promise<TorneoDto> {
  const response = await fetch(`/torneos/${torneoId}`)
  const torneo = await parseResponse<TorneoApiDto>(response)
  return normalizarTorneo(torneo)
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

export async function listarDisciplinasTorneo(
  torneoId: string,
): Promise<DisciplinaTorneoDto[]> {
  const response = await fetch(`/torneos/${torneoId}/disciplinas`)
  return parseResponse<DisciplinaTorneoDto[]>(response)
}

export async function asignarJuez(payload: {
  torneoId: string
  disciplina: DisciplinaCodigo
  juezId: string
}): Promise<{ juez_id: string }> {
  const response = await fetch(
    `/torneos/${payload.torneoId}/disciplinas/${payload.disciplina}/juez`,
    {
      method: 'PUT',
      headers: buildHeaders(),
      body: JSON.stringify({ juez_id: payload.juezId }),
    },
  )

  return parseResponse<{ juez_id: string }>(response)
}

async function transicionarTorneo(torneoId: string, endpoint: string): Promise<void> {
  const response = await fetch(`/torneos/${torneoId}/${endpoint}`, {
    method: 'PUT',
    headers: buildHeaders(),
  })

  await parseResponse<{ ok: boolean }>(response)
}

export async function abrirInscripcion(torneoId: string): Promise<void> {
  await transicionarTorneo(torneoId, 'abrir-inscripcion')
}

export async function cerrarInscripcion(torneoId: string): Promise<void> {
  await transicionarTorneo(torneoId, 'cerrar-inscripcion')
}

export async function iniciarEjecucion(torneoId: string): Promise<void> {
  await transicionarTorneo(torneoId, 'iniciar-ejecucion')
}

export async function volverPreparacion(torneoId: string): Promise<void> {
  await transicionarTorneo(torneoId, 'volver-preparacion')
}

export async function iniciarPremiacion(torneoId: string): Promise<void> {
  await transicionarTorneo(torneoId, 'iniciar-premiacion')
}

export async function cerrarTorneo(torneoId: string): Promise<void> {
  await transicionarTorneo(torneoId, 'cerrar')
}

export async function cancelarTorneo(torneoId: string): Promise<void> {
  await transicionarTorneo(torneoId, 'cancelar')
}

export async function fetchDisciplinasDeJuez(
  torneoId: string,
  juezId: string,
): Promise<string[]> {
  const response = await fetch(`/torneos/${torneoId}/jueces/${juezId}/disciplinas`)
  return parseResponse<string[]>(response)
}
