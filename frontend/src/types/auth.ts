export type RolUsuario = 'juez' | 'organizador'

export type EstadoPerformance =
  | 'AnunciadaAP'
  | 'Llamada'
  | 'ResultadoRegistrado'
  | 'EnRevision'
  | 'Ejecutada'
  | 'DNS'

export interface AuthState {
  token: string | null
  userId: string | null
  email: string | null
  rol: RolUsuario | null
  login: (token: string) => void
  logout: () => void
}
