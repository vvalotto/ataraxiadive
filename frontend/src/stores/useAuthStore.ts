import { create } from 'zustand'
import { decodeJwtPayload } from '../api/auth'
import type { AuthState, RolUsuario } from '../types/auth'

const useAuthStore = create<AuthState>((set) => ({
  token: null,
  userId: null,
  email: null,
  rol: null,

  login: (token: string) => {
    const payload = decodeJwtPayload(token)
    set({
      token,
      userId: payload.sub,
      email: payload.email,
      rol: payload.rol.toLowerCase() as RolUsuario,
    })
  },

  logout: () => {
    set({ token: null, userId: null, email: null, rol: null })
  },
}))

export default useAuthStore
