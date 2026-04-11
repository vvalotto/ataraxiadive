export type RolUsuario = 'juez' | 'organizador'

export interface AuthState {
  token: string | null
  userId: string | null
  email: string | null
  rol: RolUsuario | null
  login: (token: string) => void
  logout: () => void
}
