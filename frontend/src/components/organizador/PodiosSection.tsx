import { PanelCategoria } from './PanelCategoria'
import type { FilaPodioData } from './FilaPodio'

export interface PodioCategoriaGroup {
  categoria: string
  titulo: string
  filas: FilaPodioData[]
}

interface PodiosSectionProps {
  title: string
  subtitle?: string
  groups: PodioCategoriaGroup[]
  emptyState?: {
    title: string
    detail?: string
  } | null
}

export function PodiosSection({
  title,
  subtitle,
  groups,
  emptyState = null,
}: PodiosSectionProps) {
  return (
    <section className="rounded-[2rem] border border-slate-700 bg-slate-900/85 p-5 shadow-[0_20px_60px_rgba(2,6,23,0.24)]">
      <div className="mb-5 flex flex-col gap-2 border-b border-slate-800 pb-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">
            {title}
          </h2>
          {subtitle ? <p className="mt-2 text-sm text-slate-300">{subtitle}</p> : null}
        </div>
      </div>

      {emptyState ? (
        <div className="rounded-[1.75rem] border border-dashed border-slate-700 bg-slate-950/60 px-5 py-8 text-center">
          <p className="text-base font-semibold text-white">{emptyState.title}</p>
          {emptyState.detail ? <p className="mt-2 text-sm text-slate-400">{emptyState.detail}</p> : null}
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {groups.map((group) => (
            <PanelCategoria key={group.categoria} titulo={group.titulo} filas={group.filas} />
          ))}
        </div>
      )}
    </section>
  )
}
