import type { ReactNode } from 'react'

interface OrganizadorLayoutProps {
  title: string
  subtitle: string
  actions?: ReactNode
  children: ReactNode
}

export function OrganizadorLayout({
  title,
  subtitle,
  actions,
  children,
}: OrganizadorLayoutProps) {
  return (
    <div className="min-h-screen bg-[linear-gradient(180deg,#f7f1e3_0%,#f2e9da_45%,#e7dcc9_100%)] text-stone-900">
      <div className="mx-auto max-w-6xl px-5 py-6 sm:px-8 lg:px-10">
        <header className="rounded-[2rem] border border-stone-300/80 bg-white/80 p-6 shadow-[0_20px_60px_rgba(120,93,54,0.08)] backdrop-blur">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div className="max-w-3xl">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-800">
                Organizador
              </p>
              <h1 className="mt-2 text-3xl font-semibold tracking-tight text-stone-900">
                {title}
              </h1>
              <p className="mt-2 text-sm text-stone-600">{subtitle}</p>
            </div>
            {actions ? <div className="flex flex-wrap gap-2">{actions}</div> : null}
          </div>
        </header>

        <main className="mt-6 flex flex-col gap-4">{children}</main>
      </div>
    </div>
  )
}
