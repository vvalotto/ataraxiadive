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
    <div className="rounded-[1.75rem] border border-slate-800 bg-slate-900 p-4">
      <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">
        Ranking {categoriaLabel}
      </p>
      <div className="mt-3 space-y-1">
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
      </div>
      <p className="mt-3 text-right text-xs text-slate-500">
        {calculado ? 'Ranking final' : 'Ranking parcial'}
      </p>
    </div>
  )
}
