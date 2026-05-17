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
      roles: null,

      login: (token: string) => {
        const payload = decodeJwtPayload(token)
        const rolActivo = payload.rol.toLowerCase() as RolUsuario
        const rolesCompletos: RolUsuario[] = payload.roles
          ? payload.roles.map((r) => r.toLowerCase() as RolUsuario)
          : [rolActivo]
        set({
          token,
          userId: payload.sub,
          email: payload.email,
          nombre: payload.nombre,
          apellido: payload.apellido,
          rol: rolActivo,
          roles: rolesCompletos,
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
          roles: null,
        })
      },

      setRol: (rol: RolUsuario) => {
        set({ rol })
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
        roles: state.roles,
      }),
    },
  ),
)

export default useAuthStore
