import type { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { HealthCheck } from '../HealthCheck'
import useAuthStore from '../../stores/useAuthStore'

interface OrganizadorLayoutProps {
  title: string
  subtitle: string
  actions?: ReactNode
  children: ReactNode
  showTournamentNavigation?: boolean
  simpleHeader?: boolean
}

interface NavItem {
  label: string
  to: string
  key: 'panel' | 'grilla' | 'resultados' | 'jueces' | 'torneo' | 'audit'
  disabled?: boolean
}

const NAV_ITEMS: NavItem[] = [
  { key: 'panel', label: 'Panel', to: '/organizador/panel' },
  { key: 'grilla', label: 'Grilla', to: '/organizador/grilla' },
  { key: 'resultados', label: 'Resultados', to: '/organizador/resultados' },
  { key: 'jueces', label: 'Jueces', to: '/organizador/jueces' },
  { key: 'torneo', label: 'Torneo', to: '/organizador/torneo' },
  { key: 'audit', label: 'Audit Log', to: '/organizador/audit-log' },
]

function currentSection(pathname: string): NavItem['key'] {
  if (pathname === '/organizador' || pathname === '/organizador/dashboard') return 'torneo'
  if (pathname.startsWith('/organizador/panel')) return 'panel'
  if (pathname.startsWith('/organizador/grilla')) return 'grilla'
  if (pathname.startsWith('/organizador/resultados')) return 'resultados'
  if (pathname.startsWith('/organizador/jueces')) return 'jueces'
  if (pathname.startsWith('/organizador/audit-log')) return 'audit'
  if (pathname.startsWith('/organizador/torneos/') && pathname.endsWith('/competencias')) {
    return 'audit'
  }
  if (pathname.startsWith('/organizador/competencias/') && pathname.includes('/auditoria')) {
    return 'audit'
  }
  if (pathname.startsWith('/organizador/torneo/')) {
    return 'panel'
  }
  if (
    pathname === '/organizador/torneo' ||
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
  showTournamentNavigation = true,
  simpleHeader = false,
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
              {!simpleHeader ? (
                <span className="text-lg font-black tracking-tight text-sky-400">
                  AtaraxiaDive
                </span>
              ) : null}
              {showTournamentNavigation ? (
                <nav className="flex flex-wrap items-center gap-2">
                  {NAV_ITEMS.map((item) => {
                    const isActive = seccionActiva === item.key
                    const baseClass =
                      'rounded-full border px-3 py-2 text-xs font-semibold uppercase tracking-[0.16em] transition'

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
              ) : null}
            </div>

            <div className="flex flex-wrap items-center gap-3">
              {!simpleHeader ? <HealthCheck compact /> : null}
              <span className="rounded-full border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.14em] text-slate-300">
                {usuarioLabel}
              </span>
            </div>
          </div>

          <div className="flex flex-col gap-3 xl:flex-row xl:items-end xl:justify-between">
            <div className="max-w-3xl">
              {!simpleHeader ? (
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-sky-300/80">
                  Organizador
                </p>
              ) : null}
              <h1 className="mt-2 text-3xl font-semibold tracking-tight text-white">{title}</h1>
              {subtitle ? <p className="mt-2 text-sm text-slate-300">{subtitle}</p> : null}
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
