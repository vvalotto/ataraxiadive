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

export interface InscriptoDisciplinaDetalleDto {
  disciplina: string
  ap: string | null
  unidad: string | null
}

export interface InscripcionApDto {
  disciplina: string
  ap: string | null
  unidad: string | null
}

export interface InscriptoDetalleDto {
  inscripcion_id: string
  atleta_id: string
  torneo_id: string
  estado: string
  fecha_inscripcion: string
  nombre: string
  apellido: string
  categoria: string
  club: string
  disciplinas: InscriptoDisciplinaDetalleDto[]
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

export interface CrearAtletaPayload {
  atletaId: string
  nombre: string
  apellido: string
  email: string
  fechaNacimiento: string
  categoria: string
  club: string
  brevet?: string
}

export interface InscribirAtletaPayload {
  atletaId: string
  torneoId: string
  disciplinas: DisciplinaCodigo[]
}

export interface InscribirAtletaResponse {
  inscripcion_id: string
}

export interface RegistroPasoUnoPayload {
  nombre_completo: string
  fecha_nacimiento: string
  genero: string
  documento_tipo: string
  documento_numero: string
  telefono: string
}

export interface RegistroPasoDosPayload {
  disciplinas: DisciplinaCodigo[]
  categoria: string
  brevet: string
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

function buildFileHeaders(): Record<string, string> {
  const token = getToken()
  const headers: Record<string, string> = {}

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

export interface InscriptoInfoDto {
  atleta_id: string
  nombre: string
  club: string
}

export async function listarInscriptosInfo(torneoId: string): Promise<InscriptoInfoDto[]> {
  const response = await fetch(`/registro/torneos/${torneoId}/inscriptos-info`)
  return parseResponse<InscriptoInfoDto[]>(response)
}

export async function listarInscriptos(torneoId: string): Promise<InscriptoDto[]> {
  const response = await fetch(`/registro/torneos/${torneoId}/inscriptos`, {
    headers: buildHeaders(),
  })
  return parseResponse<InscriptoDto[]>(response)
}

export async function listarInscriptosDetalle(
  torneoId: string,
): Promise<InscriptoDetalleDto[]> {
  const response = await fetch(`/registro/torneos/${torneoId}/inscriptos-detalle`, {
    headers: buildHeaders(),
  })
  return parseResponse<InscriptoDetalleDto[]>(response)
}

export async function fetchAtletaMe(): Promise<AtletaDto> {
  const response = await fetch('/registro/atletas/me', {
    headers: buildHeaders(),
  })
  return parseResponse<AtletaDto>(response)
}

export async function fetchAtletaMeOrNull(): Promise<AtletaDto | null> {
  const response = await fetch('/registro/atletas/me', {
    headers: buildHeaders(),
  })
  if (response.status === 404) return null
  return parseResponse<AtletaDto>(response)
}

export async function crearAtleta(payload: CrearAtletaPayload): Promise<{ atleta_id: string }> {
  const response = await fetch('/registro/atletas', {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify({
      atleta_id: payload.atletaId,
      nombre: payload.nombre,
      apellido: payload.apellido,
      email: payload.email,
      fecha_nacimiento: payload.fechaNacimiento,
      categoria: payload.categoria,
      club: payload.club,
      brevet: payload.brevet ?? null,
    }),
  })
  return parseResponse<{ atleta_id: string }>(response)
}

export async function fetchAtleta(atletaId: string): Promise<AtletaDto> {
  const response = await fetch(`/registro/atletas/${atletaId}`, {
    headers: buildHeaders(),
  })
  return parseResponse<AtletaDto>(response)
}

export async function listarInscripcionesDeAtleta(atletaId: string): Promise<InscriptoDto[]> {
  const response = await fetch(`/registro/atletas/${atletaId}/inscripciones`, {
    headers: buildHeaders(),
  })
  return parseResponse<InscriptoDto[]>(response)
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

export async function fetchApInscripcion(
  inscripcionId: string,
  disciplina: string,
): Promise<InscripcionApDto> {
  const response = await fetch(
    `/registro/inscripciones/${inscripcionId}/ap?disciplina=${encodeURIComponent(disciplina)}`,
    {
      headers: buildHeaders(),
    },
  )
  return parseResponse<InscripcionApDto>(response)
}

export async function guardarApInscripcion(payload: {
  inscripcionId: string
  disciplina: string
  valorAp: string
}): Promise<InscripcionApDto> {
  const response = await fetch(`/registro/inscripciones/${payload.inscripcionId}/ap`, {
    method: 'PUT',
    headers: buildHeaders(),
    body: JSON.stringify({
      disciplina: payload.disciplina,
      valor_ap: payload.valorAp,
    }),
  })
  return parseResponse<InscripcionApDto>(response)
}

export async function subirAptoMedico(
  inscripcionId: string,
  archivo: File,
): Promise<{ path: string }> {
  const formData = new FormData()
  formData.append('archivo', archivo)
  const response = await fetch(`/registro/inscripciones/${inscripcionId}/apto-medico`, {
    method: 'POST',
    headers: buildFileHeaders(),
    body: formData,
  })
  return parseResponse<{ path: string }>(response)
}

export async function subirConstanciaPago(
  inscripcionId: string,
  archivo: File,
): Promise<{ path: string }> {
  const formData = new FormData()
  formData.append('archivo', archivo)
  const response = await fetch(`/registro/inscripciones/${inscripcionId}/constancia-pago`, {
    method: 'POST',
    headers: buildFileHeaders(),
    body: formData,
  })
  return parseResponse<{ path: string }>(response)
}
