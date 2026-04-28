import { FilaPodio, type FilaPodioData } from './FilaPodio'

interface PanelCategoriaProps {
  titulo: string
  filas: FilaPodioData[]
}

export function PanelCategoria({ titulo, filas }: PanelCategoriaProps) {
  return (
    <article className="rounded-[1.75rem] border border-stone-300/80 bg-stone-50/70 p-4">
      <div className="mb-4 flex items-center justify-between gap-2 border-b border-stone-200 pb-3">
        <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-stone-600">
          {titulo}
        </h3>
        <span className="text-xs text-stone-400">{filas.length}</span>
      </div>

      {filas.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-stone-300 bg-white/65 px-3 py-5 text-center text-sm text-stone-500">
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
