import { type RankingEntradaDto } from '../../api/resultados'
import { formatMarca } from '../../utils/marca'
import { RankingRow } from './RankingRow'

interface RankingCardProps {
  categoriaLabel: string
  entradas: RankingEntradaDto[]
  unidad: string | null
  nombresPorId: Map<string, string>
  atletaId: string
  calculado: boolean
}

function formatRp(entrada: RankingEntradaDto, unidad: string | null): string {
  if (entrada.es_dns || !entrada.rp) return '-'
  return formatMarca(entrada.rp, unidad ?? entrada.unidad ?? 'Metros')
}

export function RankingCard({
  categoriaLabel,
  entradas,
  unidad,
  nombresPorId,
  atletaId,
  calculado,
}: RankingCardProps) {
  if (entradas.length === 0) return null

  return (
    <div className="rounded-[1.75rem] border border-slate-800 bg-slate-900 overflow-hidden">
      <p className="px-4 pt-4 text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">
        Ranking {categoriaLabel}
      </p>
      <div className="mt-3 overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-slate-800">
              <th className="px-4 pb-2 text-center text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Pos</th>
              <th className="px-0 pb-2 text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Atleta</th>
              <th className="px-4 pb-2 text-center text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Marca</th>
              <th className="px-4 pb-2 text-right text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Tarjeta</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {entradas.map((entrada) => (
              <RankingRow
                key={entrada.atleta_id}
                posicion={entrada.posicion}
                nombre={nombresPorId.get(entrada.atleta_id) ?? entrada.atleta_id.slice(0, 8)}
                rp={formatRp(entrada, unidad)}
                tarjeta={entrada.tarjeta}
                esDns={entrada.es_dns}
                isSelf={entrada.atleta_id === atletaId}
              />
            ))}
          </tbody>
        </table>
      </div>
      <p className="px-4 py-3 text-right text-xs text-slate-500">
        {calculado ? 'Ranking final' : 'Ranking parcial'}
      </p>
    </div>
  )
}
