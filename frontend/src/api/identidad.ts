import { getToken, handleUnauthorized } from './tokenProvider'

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

export type RolIdentidad = 'JUEZ' | 'ORGANIZADOR' | 'ATLETA' | 'ADMIN'
export type RolGestionUsuario = Exclude<RolIdentidad, 'ADMIN'>

export interface UsuarioDto {
  usuario_id: string
  nombre: string
  apellido: string
  email: string
  rol: RolIdentidad
  activo: boolean
}

export interface CrearUsuarioRequest {
  nombre: string
  apellido: string
  email: string
  password: string
  rol: RolGestionUsuario
}

export interface CrearUsuarioResponse {
  usuario_id: string
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

export async function listarUsuariosPorRol(rol: RolIdentidad): Promise<UsuarioDto[]> {
  const response = await fetch(`/auth/usuarios?rol=${encodeURIComponent(rol)}`, {
    headers: buildHeaders(),
  })
  return parseResponse<UsuarioDto[]>(response)
}

export async function listarTodosLosUsuarios(): Promise<UsuarioDto[]> {
  const response = await fetch('/auth/usuarios', {
    headers: buildHeaders(),
  })
  return parseResponse<UsuarioDto[]>(response)
}

export async function crearUsuario(body: CrearUsuarioRequest): Promise<CrearUsuarioResponse> {
  const response = await fetch('/auth/registro', {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify(body),
  })
  return parseResponse<CrearUsuarioResponse>(response)
}
