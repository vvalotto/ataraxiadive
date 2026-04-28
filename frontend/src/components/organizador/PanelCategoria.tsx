import { FilaPodio, type FilaPodioData } from './FilaPodio'

interface PanelCategoriaProps {
  titulo: string
  filas: FilaPodioData[]
}

export function PanelCategoria({ titulo, filas }: PanelCategoriaProps) {
  return (
    <article className="rounded-[1.75rem] border border-slate-700 bg-slate-950/60 p-4">
      <div className="mb-4 flex items-center justify-between gap-2 border-b border-slate-800 pb-3">
        <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-300">
          {titulo}
        </h3>
        <span className="text-xs text-slate-500">{filas.length}</span>
      </div>

      {filas.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-900/80 px-3 py-5 text-center text-sm text-slate-400">
          Sin participantes
        </div>
      ) : (
        <ol className="space-y-2">
          {filas.map((fila) => (
            <FilaPodio key={fila.atleta_id} fila={fila} />
          ))}
        </ol>
      )}
    </article>
  )
}
