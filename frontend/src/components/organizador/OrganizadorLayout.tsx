import type { ReactNode } from 'react'
import type { EstadoTorneo } from '../../api/torneo'
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
  activeTournamentId?: string
  activeTournamentState?: EstadoTorneo
}

interface NavItem {
  label: string
  to: string
  key:
    | 'inicio'
    | 'inscriptos'
    | 'panel'
    | 'grilla'
    | 'resultados'
    | 'podios'
    | 'jueces'
    | 'torneo'
    | 'audit'
  disabled?: boolean
}

const NAV_ITEMS: NavItem[] = [
  { key: 'inicio', label: 'Inicio', to: '/organizador/torneo' },
  { key: 'panel', label: 'Panel', to: '/organizador/panel' },
  { key: 'inscriptos', label: 'Inscriptos', to: '/organizador/inscriptos' },
  { key: 'grilla', label: 'Grilla', to: '/organizador/grilla' },
  { key: 'jueces', label: 'Jueces', to: '/organizador/jueces' },
  { key: 'resultados', label: 'Resultados', to: '/organizador/resultados' },
  { key: 'podios', label: 'Podios', to: '/organizador/podios' },
  { key: 'torneo', label: 'Torneo', to: '/organizador/torneo' },
  { key: 'audit', label: 'Audit Log', to: '/organizador/audit-log' },
]

function currentSection(pathname: string): NavItem['key'] {
  if (pathname === '/organizador' || pathname === '/organizador/dashboard') return 'inicio'
  if (pathname.startsWith('/organizador/inscriptos')) return 'inscriptos'
  if (pathname.startsWith('/organizador/panel')) return 'panel'
  if (pathname.startsWith('/organizador/grilla')) return 'grilla'
  if (pathname.startsWith('/organizador/resultados')) return 'resultados'
  if (pathname.startsWith('/organizador/podios')) return 'podios'
  if (pathname.startsWith('/organizador/jueces')) return 'jueces'
  if (pathname.startsWith('/organizador/audit-log')) return 'audit'
  if (pathname.startsWith('/organizador/torneos/') && pathname.endsWith('/competencias')) {
    return 'audit'
  }
  if (pathname.startsWith('/organizador/competencias/') && pathname.includes('/auditoria')) {
    return 'audit'
  }
  if (pathname.startsWith('/organizador/torneo/')) {
    return 'torneo'
  }
  if (
    pathname === '/organizador/torneo' ||
    pathname.startsWith('/organizador/torneos/') ||
    pathname.startsWith('/organizador/usuarios')
  ) {
    return 'inicio'
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
  activeTournamentId,
  activeTournamentState,
}: OrganizadorLayoutProps) {
  void activeTournamentState
  const location = useLocation()
  const email = useAuthStore((s) => s.email)
  const nombre = useAuthStore((s) => s.nombre)
  const apellido = useAuthStore((s) => s.apellido)
  const seccionActiva = currentSection(location.pathname)
  const usuarioLabel = [nombre, apellido].filter(Boolean).join(' ').trim() || email || 'Organizador'

  function shouldShowNavItem(item: NavItem): boolean {
    if (item.key === 'torneo') return Boolean(activeTournamentId)
    if (item.key === 'podios') return Boolean(activeTournamentId) || seccionActiva === 'podios'
    if (item.key === 'inscriptos') {
      return Boolean(activeTournamentId) || seccionActiva === 'inscriptos'
    }
    return true
  }

  function navHref(item: NavItem): string {
    if (item.key === 'inicio') return item.to
    if (!activeTournamentId) return item.to
    if (item.key === 'torneo') return `/organizador/torneo/${activeTournamentId}`
    return `${item.to}?torneo_id=${encodeURIComponent(activeTournamentId)}`
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="sticky top-0 z-40 border-b border-slate-700/80 bg-slate-900/95 backdrop-blur">
        <div className="mx-auto flex max-w-[1100px] flex-col px-5 lg:px-8">
          <div
            className={
              showTournamentNavigation && !simpleHeader
                ? 'flex flex-col gap-2 py-2 xl:flex-row xl:items-center xl:justify-between'
                : 'flex flex-col gap-2 py-3 xl:flex-row xl:items-center xl:justify-between'
            }
          >
            <div className="flex min-w-0 flex-1 items-center">
              {showTournamentNavigation ? (
                <nav className="-mx-1 flex min-w-0 flex-1 items-center gap-1 overflow-x-auto px-1 scrollbar-thin scrollbar-track-transparent scrollbar-thumb-slate-700">
                  {NAV_ITEMS.filter((item) => shouldShowNavItem(item)).map((item) => {
                    const isActive = seccionActiva === item.key
                    const baseClass =
                      'inline-flex h-10 items-center rounded-full border border-transparent px-3 text-xs font-semibold tracking-[0.02em] transition whitespace-nowrap'

                    return (
                      <Link
                        key={item.key}
                        to={navHref(item)}
                        className={
                          isActive
                            ? `${baseClass} border-sky-400/40 bg-sky-400/10 text-sky-200`
                            : `${baseClass} text-slate-400 hover:border-slate-700 hover:bg-slate-800/70 hover:text-white`
                        }
                      >
                        {item.label}
                      </Link>
                    )
                  })}
                </nav>
              ) : null}
            </div>

            <div className="ml-auto flex flex-wrap items-center gap-2">
              {!simpleHeader ? <HealthCheck compact /> : null}
              <span className="text-xs text-slate-400">
                {usuarioLabel}
              </span>
            </div>
          </div>

          <div className="flex flex-col gap-2 border-t border-slate-800/80 py-3 xl:flex-row xl:items-end xl:justify-between">
            <div className="max-w-3xl">
              {!simpleHeader ? (
                <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-sky-300/75">
                  Organizador
                </p>
              ) : null}
              <h1 className="mt-1 text-2xl font-semibold tracking-tight text-white">{title}</h1>
              {subtitle ? <p className="mt-1 text-sm text-slate-300">{subtitle}</p> : null}
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
