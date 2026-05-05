import type { ReactNode } from 'react'
import { HealthCheck } from '../HealthCheck'
import { SyncStatusBadge } from './SyncStatusBadge'

interface JuezLayoutProps {
  title: string
  subtitle?: string
  actions?: ReactNode
  children: ReactNode
}

export function JuezLayout({ title, subtitle, actions, children }: JuezLayoutProps) {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto flex min-h-screen w-full max-w-sm flex-col px-4 py-6">
        <header className="mb-6 rounded-3xl border border-slate-800 bg-slate-900/80 p-4 shadow-lg shadow-slate-950/40">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h1 className="text-2xl font-semibold uppercase tracking-[0.18em] text-slate-50">
                {title}
              </h1>
              {subtitle ? <p className="mt-2 text-sm text-slate-400">{subtitle}</p> : null}
              <div className="mt-2 flex flex-wrap items-center gap-2">
                <HealthCheck compact />
                <SyncStatusBadge />
              </div>
            </div>
            {actions}
          </div>
        </header>
        <main className="flex flex-1 flex-col gap-4">{children}</main>
      </div>
    </div>
  )
}
