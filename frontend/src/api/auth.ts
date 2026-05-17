import type { RolUsuario } from '../types/auth'

export interface LoginResponseToken {
  access_token: string
  token_type: string
}

export interface LoginResponseRoleSelection {
  requires_role_selection: true
  roles: string[]
}

export type LoginResponse = LoginResponseToken | LoginResponseRoleSelection

interface JwtPayload {
  sub: string
  email: string
  nombre: string
  apellido: string
  rol: RolUsuario
  roles?: string[]
  [key: string]: unknown
}

export async function loginApi(
  email: string,
  password: string,
  rolElegido?: string,
): Promise<LoginResponse> {
  const body: Record<string, string> = { email, password }
  if (rolElegido) body.rol_elegido = rolElegido

  const response = await fetch('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

  if (response.status === 401) {
    throw new Error('Credenciales inválidas')
  }
  if (!response.ok) {
    throw new Error(`Error del servidor: ${response.status}`)
  }

  return response.json() as Promise<LoginResponse>
}

export function decodeJwtPayload(token: string): JwtPayload {
  const [, payloadB64] = token.split('.')
  const padded = payloadB64 + '=='.slice((payloadB64.length % 4) || 4)
  const decoded = atob(padded.replace(/-/g, '+').replace(/_/g, '/'))
  return JSON.parse(decoded) as JwtPayload
}
