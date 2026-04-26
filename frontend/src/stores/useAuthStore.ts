import { create } from 'zustand'
import { createJSONStorage, persist } from 'zustand/middleware'
import { decodeJwtPayload } from '../api/auth'
import type { AuthState, RolUsuario } from '../types/auth'

const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      userId: null,
      email: null,
      nombre: null,
      apellido: null,
      rol: null,

      login: (token: string) => {
        const payload = decodeJwtPayload(token)
        set({
          token,
          userId: payload.sub,
          email: payload.email,
          nombre: payload.nombre,
          apellido: payload.apellido,
          rol: payload.rol.toLowerCase() as RolUsuario,
        })
      },

      logout: () => {
        set({
          token: null,
          userId: null,
          email: null,
          nombre: null,
          apellido: null,
          rol: null,
        })
      },
    }),
    {
      name: 'ataraxiadive-auth',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        token: state.token,
        userId: state.userId,
        email: state.email,
        nombre: state.nombre,
        apellido: state.apellido,
        rol: state.rol,
      }),
    },
  ),
)

export default useAuthStore
