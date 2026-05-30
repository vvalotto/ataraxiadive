import { type ReactNode, useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import useAuthStore from '../../stores/useAuthStore'

interface JuezLayoutProps {
  title: string
  subtitle?: string
  actions?: ReactNode
  children: ReactNode
}

const TABS = [
  { label: 'Mis Asignaciones', to: '/juez/disciplinas' },
  { label: 'Mis Datos', to: '/juez/mis-datos' },
]

function isTabActive(pathname: string, to: string): boolean {
  if (to === '/juez/disciplinas') {
    return pathname === '/juez/disciplinas' || pathname.startsWith('/juez/grilla') || pathname.startsWith('/juez/performance')
  }
  return pathname === to || pathname.startsWith(`${to}/`)
}

export function JuezLayout({ title, subtitle, actions, children }: JuezLayoutProps) {
  const logout = useAuthStore((s) => s.logout)
  const { pathname } = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    document.title = 'AtaraxiaDive · Juez'
    return () => { document.title = 'AtaraxiaDive' }
  }, [])

  useEffect(() => { setMenuOpen(false) }, [pathname])

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto flex min-h-screen w-full max-w-[430px] flex-col border-x border-slate-800 bg-slate-950">
        <header className="sticky top-0 z-20 border-b border-slate-800 bg-slate-950/95 backdrop-blur">
          <div className="flex items-start justify-between gap-3 px-4 pt-3 pb-0">
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-sky-400">
                  AtaraxiaDive
                </p>
              </div>
              <p className="mt-0.5 text-[11px] font-semibold uppercase tracking-[0.22em] text-sky-300/75">
                Portal Juez
              </p>
              <h1 className="mt-2 text-xl font-semibold text-white">{title}</h1>
              {subtitle ? <p className="mt-1 text-sm text-slate-400">{subtitle}</p> : null}
            </div>
            <div className="flex shrink-0 items-start gap-2">
              {actions ? <div>{actions}</div> : null}
              <button
                type="button"
                onClick={() => setMenuOpen((v) => !v)}
                className="rounded-full border border-slate-700 px-3 py-2 text-xs font-semibold text-slate-400 hover:border-slate-500 hover:text-slate-200"
                aria-label="Menú de navegación"
              >
                {menuOpen ? '✕' : '☰'}
              </button>
              <button
                type="button"
                onClick={logout}
                className="rounded-full border border-slate-700 px-3 py-2 text-xs font-semibold text-slate-400 hover:border-slate-500 hover:text-slate-200"
              >
                Salir
              </button>
            </div>
          </div>

          {/* Menú vertical desplegable */}
          {menuOpen ? (
            <nav className="flex flex-col border-t border-slate-800 px-4">
              {TABS.map((tab) => {
                const active = isTabActive(pathname, tab.to)
                return (
                  <Link
                    key={tab.to}
                    to={tab.to}
                    className={[
                      'flex items-center border-b border-slate-800/60 py-3.5 text-sm font-semibold transition-colors',
                      active ? 'text-sky-400' : 'text-slate-300 hover:text-white',
                    ].join(' ')}
                  >
                    {active ? (
                      <span className="mr-3 h-1.5 w-1.5 rounded-full bg-sky-400" />
                    ) : (
                      <span className="mr-3 h-1.5 w-1.5 rounded-full bg-transparent" />
                    )}
                    {tab.label}
                  </Link>
                )
              })}
            </nav>
          ) : null}
        </header>

        <main className="flex-1 px-4 py-4">{children}</main>
      </div>
    </div>
  )
}
