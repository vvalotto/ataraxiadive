import { create } from 'zustand'
import { decodeJwtPayload } from '../api/auth'
import type { AuthState, RolUsuario } from '../types/auth'

const useAuthStore = create<AuthState>((set) => ({
  token: null,
  email: null,
  rol: null,

  login: (token: string) => {
    const payload = decodeJwtPayload(token)
    set({ token, email: payload.email as string, rol: (payload.rol as string).toLowerCase() as RolUsuario })
  },

  logout: () => {
    set({ token: null, email: null, rol: null })
  },
}))

export default useAuthStore
