import type { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import useAuthStore from '../stores/useAuthStore'

interface RequireAuthProps {
  children: ReactNode
}

export function RequireAuth({ children }: RequireAuthProps) {
  const token = useAuthStore((s) => s.token)
  const rol = useAuthStore((s) => s.rol)

  if (!token || !rol) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}
