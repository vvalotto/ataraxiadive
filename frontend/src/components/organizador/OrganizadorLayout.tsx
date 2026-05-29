import { type ReactNode, useEffect } from 'react'
import type { EstadoTorneo } from '../../api/torneo'
import { Link, useLocation } from 'react-router-dom'
import useAuthStore from '../../stores/useAuthStore'

interface OrganizadorLayoutProps {
  title: string
  subtitle: string

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
    | 'mis-datos'
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
  { key: 'mis-datos', label: 'Mis Datos', to: '/organizador/mis-datos' },
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
  if (pathname.startsWith('/organizador/mis-datos')) return 'mis-datos'
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
  children,
  showTournamentNavigation = true,
  simpleHeader = false,
  activeTournamentId,
  activeTournamentState,
}: OrganizadorLayoutProps) {
  void activeTournamentState
  const location = useLocation()

  useEffect(() => {
    document.title = 'AtaraxiaDive · Organizador'
    return () => { document.title = 'AtaraxiaDive' }
  }, [])
  const logout = useAuthStore((s) => s.logout)
  const seccionActiva = currentSection(location.pathname)

  function shouldShowNavItem(item: NavItem): boolean {
    if (item.key === 'torneo') return Boolean(activeTournamentId)
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
      <header className="sticky top-0 z-40 border-b border-slate-800 bg-slate-950/95 backdrop-blur">
        <div className="mx-auto max-w-[1100px] px-5 lg:px-8">
          <div className="flex items-start justify-between gap-3 pt-3 pb-0">
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-sky-400">
                  AtaraxiaDive
                </p>
              </div>
              {!simpleHeader ? (
                <p className="mt-0.5 text-[11px] font-semibold uppercase tracking-[0.22em] text-sky-300/75">
                  Portal Organizador
                </p>
              ) : null}
              <h1 className="mt-2 text-xl font-semibold text-white">{title}</h1>
              {subtitle ? <p className="mt-1 text-sm text-slate-400">{subtitle}</p> : null}
            </div>
            <div className="flex shrink-0 items-start gap-2">
              <button
                type="button"
                onClick={logout}
                className="rounded-full border border-slate-700 px-3 py-2 text-xs font-semibold text-slate-400 hover:border-slate-500 hover:text-slate-200"
              >
                Salir
              </button>
            </div>
          </div>

          {showTournamentNavigation && !simpleHeader ? (
            <nav className="mt-3 flex overflow-x-auto border-t border-slate-800 scrollbar-thin scrollbar-track-transparent scrollbar-thumb-slate-700">
              {NAV_ITEMS.filter((item) => shouldShowNavItem(item)).map((item) => {
                const isActive = seccionActiva === item.key
                return (
                  <Link
                    key={item.key}
                    to={navHref(item)}
                    className={[
                      'flex h-10 shrink-0 items-center px-4 text-xs font-semibold whitespace-nowrap transition-colors',
                      isActive
                        ? 'border-b-2 border-sky-400 text-sky-300'
                        : 'border-b-2 border-transparent text-slate-400 hover:text-white',
                    ].join(' ')}
                  >
                    {item.label}
                  </Link>
                )
              })}
            </nav>
          ) : null}
        </div>
      </header>

      <div className="mx-auto max-w-[1100px] px-5 py-6 lg:px-8">
        <main className="flex flex-col gap-4">{children}</main>
      </div>
    </div>
  )
}
