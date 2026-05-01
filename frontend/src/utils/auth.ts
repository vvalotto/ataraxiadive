import type { RolUsuario } from '../types/auth'

export const HOME_BY_ROL: Record<RolUsuario, string> = {
  juez: '/juez/disciplinas',
  organizador: '/organizador/dashboard',
  atleta: '/atleta',
}
