import type { ReactNode } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'

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
  { label: 'Mis inscr.', to: '/atleta/mis-inscripciones' },
  { label: 'Resultados', to: '/atleta/resultados' },
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

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto flex min-h-screen w-full max-w-[430px] flex-col border-x border-slate-800 bg-slate-950">
        <header className="sticky top-0 z-20 border-b border-slate-800 bg-slate-950/95 px-4 py-3 backdrop-blur">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
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
                <span className="flex items-center gap-1 text-xs font-semibold text-emerald-400">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                  En línea
                </span>
              </div>
              <h1 className="mt-2 text-xl font-semibold text-white">{title}</h1>
              {subtitle ? <p className="mt-1 text-sm text-slate-400">{subtitle}</p> : null}
            </div>
            {actions ? <div className="shrink-0">{actions}</div> : null}
          </div>
        </header>

        <main className="flex-1 px-4 py-4 pb-24">{children}</main>

        <nav className="sticky bottom-0 z-20 grid h-14 grid-cols-4 border-t border-slate-800 bg-slate-900/95 backdrop-blur">
          {TABS.map((tab) => {
            const active = isTabActive(location.pathname, tab.to)
            return (
              <Link
                key={tab.to}
                to={tab.to}
                className={[
                  'flex items-center justify-center text-center text-xs font-semibold transition-colors',
                  active ? 'text-sky-300' : 'text-slate-400',
                ].join(' ')}
              >
                {tab.label}
              </Link>
            )
          })}
        </nav>
      </div>
    </div>
  )
}
