import type { RolUsuario } from '../types/auth'

interface LoginResponse {
  access_token: string
  token_type: string
}

interface JwtPayload {
  sub: string
  rol: RolUsuario
  [key: string]: unknown
}

export async function loginApi(email: string, password: string): Promise<LoginResponse> {
  const response = await fetch('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
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
