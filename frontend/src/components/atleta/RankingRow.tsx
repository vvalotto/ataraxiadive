interface RankingRowProps {
  posicion: number
  nombre: string
  rp: string
  puntos: string
  tarjeta: string | null
  esDns: boolean
  isSelf: boolean
}

const PODIO_ICONS: Record<number, string> = { 1: '🥇', 2: '🥈', 3: '🥉' }

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

export function RankingRow({ posicion, nombre, rp, puntos, tarjeta, esDns, isSelf }: RankingRowProps) {
  return (
    <div
      className={`flex items-center gap-3 rounded-2xl px-3 py-2.5 ${
        isSelf ? 'border border-sky-500/30 bg-sky-500/10' : 'border border-transparent'
      }`}
    >
      <span className="w-6 text-center text-sm font-bold text-slate-400">
        {PODIO_ICONS[posicion] ?? posicion}
      </span>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-1.5">
          <span className="truncate text-sm font-semibold text-white">{nombre}</span>
          {isSelf ? (
            <span className="rounded-full border border-sky-400/40 bg-sky-400/10 px-1.5 py-0.5 text-[10px] font-semibold text-sky-300">
              Vos
            </span>
          ) : null}
        </div>
        <span className="text-xs text-slate-400">{rp}</span>
      </div>
      <div className="flex flex-col items-end gap-1">
        <span className="text-sm font-semibold text-white">{puntos}</span>
        <ChipTarjeta tarjeta={tarjeta} esDns={esDns} />
      </div>
    </div>
  )
}
