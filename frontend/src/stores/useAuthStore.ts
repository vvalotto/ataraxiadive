import { create } from 'zustand'
import { decodeJwtPayload } from '../api/auth'
import type { AuthState } from '../types/auth'

const useAuthStore = create<AuthState>((set) => ({
  token: null,
  email: null,
  rol: null,

  login: (token: string) => {
    const payload = decodeJwtPayload(token)
    set({ token, email: payload.sub, rol: payload.rol })
  },

  logout: () => {
    set({ token: null, email: null, rol: null })
  },
}))

export default useAuthStore
