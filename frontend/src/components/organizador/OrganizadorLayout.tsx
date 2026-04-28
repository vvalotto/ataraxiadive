import type { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { HealthCheck } from '../HealthCheck'
import useAuthStore from '../../stores/useAuthStore'

interface OrganizadorLayoutProps {
  title: string
  subtitle: string
  actions?: ReactNode
  children: ReactNode
}

interface NavItem {
  label: string
  to: string
  key: 'panel' | 'grilla' | 'resultados' | 'jueces' | 'torneo' | 'audit'
  disabled?: boolean
}

const NAV_ITEMS: NavItem[] = [
  { key: 'panel', label: '📊 Panel', to: '/organizador/dashboard' },
  { key: 'grilla', label: '📋 Grilla', to: '/organizador/dashboard', disabled: true },
  { key: 'resultados', label: '🏆 Resultados', to: '/organizador/resultados' },
  { key: 'jueces', label: '👥 Jueces', to: '/organizador/dashboard', disabled: true },
  { key: 'torneo', label: '📝 Torneo', to: '/organizador/dashboard' },
  { key: 'audit', label: '🔍 Audit Log', to: '/organizador/dashboard', disabled: true },
]

function currentSection(pathname: string): NavItem['key'] {
  if (pathname.startsWith('/organizador/resultados')) return 'resultados'
  if (pathname.startsWith('/organizador/competencias/') && pathname.includes('/auditoria')) {
    return 'audit'
  }
  if (
    pathname.startsWith('/organizador/torneo/') ||
    pathname.startsWith('/organizador/torneos/') ||
    pathname.startsWith('/organizador/usuarios')
  ) {
    return 'torneo'
  }
  return 'panel'
}

export function OrganizadorLayout({
  title,
  subtitle,
  actions,
  children,
}: OrganizadorLayoutProps) {
  const location = useLocation()
  const email = useAuthStore((s) => s.email)
  const nombre = useAuthStore((s) => s.nombre)
  const apellido = useAuthStore((s) => s.apellido)
  const seccionActiva = currentSection(location.pathname)
  const usuarioLabel = [nombre, apellido].filter(Boolean).join(' ').trim() || email || 'Organizador'

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="sticky top-0 z-40 border-b border-slate-700/80 bg-slate-900/95 backdrop-blur">
        <div className="mx-auto flex max-w-[1100px] flex-col gap-4 px-5 py-4 lg:px-8">
          <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
            <div className="flex items-center gap-6">
              <span className="text-lg font-black tracking-tight text-sky-400">
                AtaraxiaDive
              </span>
              <nav className="flex flex-wrap items-center gap-2">
                {NAV_ITEMS.map((item) => {
                  const isActive = seccionActiva === item.key
                  const baseClass =
                    'rounded-full border px-3 py-2 text-xs font-semibold uppercase tracking-[0.16em] transition'

                  if (item.disabled) {
                    return (
                      <span
                        key={item.key}
                        className={`${baseClass} cursor-not-allowed border-slate-700 bg-slate-800 text-slate-500`}
                        aria-disabled="true"
                        title="Seccion a normalizar en siguientes US de SP-ADJ-09"
                      >
                        {item.label}
                      </span>
                    )
                  }

                  return (
                    <Link
                      key={item.key}
                      to={item.to}
                      className={
                        isActive
                          ? `${baseClass} border-sky-400 bg-sky-400/10 text-sky-300`
                          : `${baseClass} border-slate-700 bg-slate-800 text-slate-300 hover:border-slate-500 hover:text-white`
                      }
                    >
                      {item.label}
                    </Link>
                  )
                })}
              </nav>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <HealthCheck compact />
              <span className="rounded-full border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.14em] text-slate-300">
                {usuarioLabel}
              </span>
            </div>
          </div>

          <div className="flex flex-col gap-3 xl:flex-row xl:items-end xl:justify-between">
            <div className="max-w-3xl">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-sky-300/80">
                Organizador
              </p>
              <h1 className="mt-2 text-3xl font-semibold tracking-tight text-white">{title}</h1>
              <p className="mt-2 text-sm text-slate-300">{subtitle}</p>
            </div>
            {actions ? <div className="flex flex-wrap gap-2">{actions}</div> : null}
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-[1100px] px-5 py-6 lg:px-8">
        <main className="flex flex-col gap-4">{children}</main>
      </div>
    </div>
  )
}
