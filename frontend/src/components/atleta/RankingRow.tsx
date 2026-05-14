interface RankingRowProps {
  posicion: number
  nombre: string
  rp: string
  tarjeta: string | null
  esDns: boolean
  isSelf: boolean
}

function ChipTarjeta({ tarjeta, esDns }: { tarjeta: string | null; esDns: boolean }) {
  if (esDns) {
    return (
      <span className="rounded-full border border-slate-600 bg-slate-800 px-2 py-0.5 text-[10px] font-semibold text-slate-300">
        DNS
      </span>
    )
  }
  if (tarjeta?.toLowerCase().includes('roja')) {
    return (
      <span className="rounded-full border border-red-500/40 bg-red-500/10 px-2 py-0.5 text-[10px] font-semibold text-red-300">
        ROJA
      </span>
    )
  }
  if (tarjeta?.toLowerCase().includes('blanca')) {
    return (
      <span className="rounded-full border border-emerald-500/40 bg-emerald-500/10 px-2 py-0.5 text-[10px] font-semibold text-emerald-300">
        BLANCA
      </span>
    )
  }
  return null
}

export function RankingRow({ posicion, nombre, rp, tarjeta, esDns, isSelf }: RankingRowProps) {
  return (
    <tr className={isSelf ? 'bg-sky-500/10' : undefined}>
      <td className="py-2 pr-3 text-center text-xs font-semibold text-slate-400">{posicion}</td>
      <td className="py-2 pr-3">
        <div className="flex items-center gap-1.5">
          <span className={`text-sm font-semibold ${isSelf ? 'text-sky-300' : 'text-white'}`}>
            {nombre}
          </span>
          {isSelf ? (
            <span className="rounded-full border border-sky-400/40 bg-sky-400/10 px-1.5 py-0.5 text-[10px] font-semibold text-sky-300">
              Vos
            </span>
          ) : null}
        </div>
      </td>
      <td className="py-2 pr-3 text-center text-sm font-semibold text-slate-200">{rp}</td>
      <td className="py-2 text-right">
        <ChipTarjeta tarjeta={tarjeta} esDns={esDns} />
      </td>
    </tr>
  )
}
