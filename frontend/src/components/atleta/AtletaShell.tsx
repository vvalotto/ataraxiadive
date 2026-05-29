import { type ReactNode, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import useAuthStore from '../../stores/useAuthStore'

interface AtletaShellProps {
  title: string
  subtitle?: string
  showBack?: boolean
  actions?: ReactNode
  children: ReactNode
}

const TABS = [
  { label: 'Inicio', to: '/atleta' },
  { label: 'Torneos', to: '/atleta/torneos' },
  { label: 'Inscripciones', to: '/atleta/mis-inscripciones' },
  { label: 'Resultados', to: '/atleta/resultados' },
  { label: 'Mis Datos', to: '/atleta/mis-datos' },
]

function isTabActive(pathname: string, to: string): boolean {
  if (to === '/atleta') {
    return pathname === '/atleta' || pathname === '/atleta/dashboard'
  }
  return pathname === to || pathname.startsWith(`${to}/`)
}

export function AtletaShell({
  title,
  subtitle,
  showBack = false,
  actions,
  children,
}: AtletaShellProps) {
  const location = useLocation()
  const navigate = useNavigate()
  const logout = useAuthStore((state) => state.logout)

  useEffect(() => {
    document.title = 'AtaraxiaDive · Atleta'
    return () => { document.title = 'AtaraxiaDive' }
  }, [])

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto flex min-h-screen w-full max-w-[430px] flex-col border-x border-slate-800 bg-slate-950">
        <header className="sticky top-0 z-20 border-b border-slate-800 bg-slate-950/95 backdrop-blur">
          <div className="flex items-start justify-between gap-3 px-4 pt-3 pb-0">
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                {showBack ? (
                  <button
                    type="button"
                    onClick={() => navigate(-1)}
                    className="rounded-full border border-slate-700 px-2 py-1 text-sm font-semibold text-slate-200"
                  >
                    ←
                  </button>
                ) : null}
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-sky-400">
                  AtaraxiaDive
                </p>
              </div>
              <p className="mt-0.5 text-[11px] font-semibold uppercase tracking-[0.22em] text-sky-300/75">
                Portal Atleta
              </p>
              <h1 className="mt-2 text-xl font-semibold text-white">{title}</h1>
              {subtitle ? <p className="mt-1 text-sm text-slate-400">{subtitle}</p> : null}
            </div>
            <div className="flex shrink-0 items-start gap-2">
              {actions ? <div>{actions}</div> : null}
              <button
                type="button"
                onClick={logout}
                className="rounded-full border border-slate-700 px-3 py-2 text-xs font-semibold text-slate-400 hover:border-slate-500 hover:text-slate-200"
              >
                Salir
              </button>
            </div>
          </div>

          <nav className="mt-3 grid grid-cols-5 border-t border-slate-800">
            {TABS.map((tab) => {
              const active = isTabActive(location.pathname, tab.to)
              return (
                <Link
                  key={tab.to}
                  to={tab.to}
                  className={[
                    'flex h-10 items-center justify-center text-center text-xs font-semibold transition-colors',
                    active
                      ? 'border-b-2 border-sky-400 text-sky-300'
                      : 'border-b-2 border-transparent text-slate-400',
                  ].join(' ')}
                >
                  {tab.label}
                </Link>
              )
            })}
          </nav>
        </header>

        <main className="flex-1 px-4 py-4">{children}</main>
      </div>
    </div>
  )
}
