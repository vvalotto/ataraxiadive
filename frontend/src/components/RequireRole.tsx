import type { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import useAuthStore from '../stores/useAuthStore'
import type { RolUsuario } from '../types/auth'
import { HOME_BY_ROL } from '../utils/auth'

interface RequireRoleProps {
  role: RolUsuario
  children: ReactNode
}

export function RequireRole({ role, children }: RequireRoleProps) {
  const token = useAuthStore((s) => s.token)
  const rol = useAuthStore((s) => s.rol)

  if (!token || !rol) {
    return <Navigate to="/login" replace />
  }

  if (rol !== role && rol !== 'admin') {
    return <Navigate to={HOME_BY_ROL[rol]} replace />
  }

  return <>{children}</>
}
