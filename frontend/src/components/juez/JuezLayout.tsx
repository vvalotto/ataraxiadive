import type { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import useAuthStore from '../../stores/useAuthStore'
import { HealthCheck } from '../HealthCheck'
import { SyncStatusBadge } from './SyncStatusBadge'

interface JuezLayoutProps {
  title: string
  subtitle?: string
  actions?: ReactNode
  children: ReactNode
}

export function JuezLayout({ title, subtitle, actions, children }: JuezLayoutProps) {
  const logout = useAuthStore((s) => s.logout)
  const { pathname } = useLocation()
  const enMisDatos = pathname === '/juez/mis-datos'

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto flex min-h-screen w-full max-w-sm flex-col px-4 py-6">
        <header className="mb-6 rounded-3xl border border-slate-800 bg-slate-900/80 p-4 shadow-lg shadow-slate-950/40">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <h1 className="text-2xl font-semibold uppercase tracking-[0.18em] text-slate-50">
                {title}
              </h1>
              {subtitle ? <p className="mt-1 text-sm text-slate-400">{subtitle}</p> : null}
            </div>
            <div className="mt-1 flex shrink-0 items-center gap-2">
              <HealthCheck compact />
              <SyncStatusBadge />
            </div>
          </div>

          <div className="mt-3 flex gap-2">
            <Link
              to="/juez/mis-datos"
              className={
                enMisDatos
                  ? 'flex-1 rounded-full border border-sky-400/50 bg-sky-500/20 px-3 py-2 text-center text-xs font-semibold uppercase tracking-[0.14em] text-sky-300'
                  : 'flex-1 rounded-full border border-slate-600 bg-slate-800 px-3 py-2 text-center text-xs font-semibold uppercase tracking-[0.14em] text-slate-300 hover:bg-slate-700 hover:text-white'
              }
            >
              Mis Datos
            </Link>
            <button
              type="button"
              onClick={logout}
              className="flex-1 rounded-full border border-red-500/30 bg-red-500/10 px-3 py-2 text-xs font-semibold uppercase tracking-[0.14em] text-red-300 hover:bg-red-500/20 hover:text-red-200"
            >
              Salir
            </button>
          </div>

          {actions ? <div className="mt-2">{actions}</div> : null}
        </header>
        <main className="flex flex-1 flex-col gap-4">{children}</main>
      </div>
    </div>
  )
}
