export interface FilaResultadoData {
  posicion_ot: number
  atleta_id: string
  nombre: string
  genero: 'M' | 'F' | '?'
  categoria_corta: string
  club: string
  ap: string
  ot: string
  linea: string
  rp: string | null
  unidad: string | null
  tarjeta: string | null
  puntos: string | null
}

interface FilaResultadoProps {
  fila: FilaResultadoData
}

function ChipTarjeta({ tarjeta }: { tarjeta: string | null }) {
  if (!tarjeta) {
    return (
      <span className="rounded-full border border-slate-700 bg-slate-800 px-2 py-0.5 text-xs font-semibold text-slate-300">
        PENDIENTE
      </span>
    )
  }

  if (tarjeta === 'DNS' || tarjeta === 'Dns') {
    return (
      <span className="rounded-full border border-slate-500/40 bg-slate-500/20 px-2 py-0.5 text-xs font-semibold text-slate-100">
        DNS
      </span>
    )
  }

  if (tarjeta === 'Roja' || tarjeta === 'ROJA') {
    return (
      <span className="rounded-full border border-red-500/40 bg-red-500/20 px-2 py-0.5 text-xs font-semibold text-red-100">
        ROJA
      </span>
    )
  }

  if (tarjeta === 'Blanca' || tarjeta === 'BlancaConPenalizaciones') {
    return (
      <span className="rounded-full border border-emerald-500/40 bg-emerald-500/20 px-2 py-0.5 text-xs font-semibold text-emerald-100">
        BLANCA
      </span>
    )
  }

  if (tarjeta === 'Amarilla') {
    return (
      <span className="rounded-full border border-amber-500/40 bg-amber-500/20 px-2 py-0.5 text-xs font-semibold text-amber-100">
        EN REVISION
      </span>
    )
  }

  return (
    <span className="rounded-full border border-slate-700 bg-slate-800 px-2 py-0.5 text-xs font-semibold text-slate-300">
      {tarjeta}
    </span>
  )
}

export function FilaResultado({ fila }: FilaResultadoProps) {
  const rpDisplay = fila.rp ? `${fila.rp} ${fila.unidad ?? ''}`.trim() : '—'
  const puntosDisplay = fila.puntos ?? '—'

  return (
    <tr className="border-b border-slate-800 text-sm transition hover:bg-slate-800/60">
      <td className="px-3 py-3 text-center font-mono text-xs text-slate-400">
        {fila.posicion_ot}
      </td>
      <td className="px-3 py-3 font-medium text-slate-100">{fila.nombre}</td>
      <td className="px-3 py-3 text-center text-slate-300">{fila.genero}</td>
      <td className="px-3 py-3 text-slate-300">{fila.categoria_corta}</td>
      <td className="px-3 py-3 text-slate-400">{fila.club || '—'}</td>
      <td className="px-3 py-3 font-mono text-slate-300">{fila.ap}</td>
      <td className="px-3 py-3 font-mono text-xs text-slate-400">{fila.ot}</td>
      <td className="px-3 py-3 text-center text-slate-400">{fila.linea}</td>
      <td className="px-3 py-3 font-mono font-semibold text-white">{rpDisplay}</td>
      <td className="px-3 py-3">
        <ChipTarjeta tarjeta={fila.tarjeta} />
      </td>
      <td className="px-3 py-3 text-right font-mono font-bold text-sky-300">
        {puntosDisplay}
      </td>
    </tr>
  )
}
