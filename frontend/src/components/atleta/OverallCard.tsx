import { type OverallDto } from '../../api/resultados'

interface OverallCardProps {
  overall: OverallDto | null
  atletaId: string
  nombresPorId: Map<string, string>
  categoriaAtleta: string
  categoriaLabel: string
}

function OverallEmpty() {
  return (
    <div className="rounded-[1.75rem] border border-slate-800 bg-slate-900 p-5 text-center">
      <p className="text-2xl">🏆</p>
      <p className="mt-2 text-sm font-semibold text-white">Ranking Overall</p>
      <p className="mt-1 text-sm text-slate-400">
        Disponible al finalizar todas las disciplinas del torneo
      </p>
    </div>
  )
}

export function OverallCard({
  overall,
  atletaId,
  nombresPorId,
  categoriaAtleta,
  categoriaLabel,
}: OverallCardProps) {
  if (!overall?.calculado || overall.rankings.length === 0) {
    return <OverallEmpty />
  }

  const miCategoria = overall.rankings.find((cat) => cat.categoria === categoriaAtleta)

  if (!miCategoria || miCategoria.entradas.length === 0) {
    return <OverallEmpty />
  }

  return (
    <div className="rounded-[1.75rem] border border-slate-800 bg-slate-900 p-4">
      <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">
        Ranking Overall {categoriaLabel}
      </p>
      <div className="mt-3 space-y-1">
        {miCategoria.entradas.map((entrada) => {
          const isSelf = entrada.atleta_id === atletaId
          return (
            <div
              key={entrada.atleta_id}
              className={`flex items-center gap-3 rounded-2xl px-3 py-2.5 ${
                isSelf ? 'border border-sky-500/30 bg-sky-500/10' : 'border border-transparent'
              }`}
            >
              <span className="w-6 text-center text-sm font-bold text-slate-400">
                {entrada.posicion}
              </span>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-1.5">
                  <span className="truncate text-sm font-semibold text-white">
                    {nombresPorId.get(entrada.atleta_id) ?? entrada.atleta_id.slice(0, 8)}
                  </span>
                  {isSelf ? (
                    <span className="rounded-full border border-sky-400/40 bg-sky-400/10 px-1.5 py-0.5 text-[10px] font-semibold text-sky-300">
                      Vos
                    </span>
                  ) : null}
                </div>
              </div>
              <span className="text-sm font-semibold text-white">{entrada.puntos_overall}</span>
            </div>
          )
        })}
      </div>
      <p className="mt-3 text-right text-xs text-slate-500">Ranking final</p>
    </div>
  )
}
