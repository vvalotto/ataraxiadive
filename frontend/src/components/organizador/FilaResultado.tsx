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
      <span className="rounded-full bg-stone-200 px-2 py-0.5 text-xs font-semibold text-stone-500">
        PENDIENTE
      </span>
    )
  }

  if (tarjeta === 'DNS' || tarjeta === 'Dns') {
    return (
      <span className="rounded-full bg-slate-500 px-2 py-0.5 text-xs font-semibold text-white">
        DNS
      </span>
    )
  }

  if (tarjeta === 'Roja' || tarjeta === 'ROJA') {
    return (
      <span className="rounded-full bg-red-500 px-2 py-0.5 text-xs font-semibold text-white">
        ROJA
      </span>
    )
  }

  if (tarjeta === 'Blanca' || tarjeta === 'BlancaConPenalizaciones') {
    return (
      <span className="rounded-full bg-emerald-500 px-2 py-0.5 text-xs font-semibold text-white">
        BLANCA
      </span>
    )
  }

  if (tarjeta === 'Amarilla') {
    return (
      <span className="rounded-full bg-amber-400 px-2 py-0.5 text-xs font-semibold text-stone-900">
        REVISIÓN
      </span>
    )
  }

  return (
    <span className="rounded-full bg-stone-200 px-2 py-0.5 text-xs font-semibold text-stone-500">
      {tarjeta}
    </span>
  )
}

export function FilaResultado({ fila }: FilaResultadoProps) {
  const rpDisplay = fila.rp ? `${fila.rp} ${fila.unidad ?? ''}`.trim() : '—'
  const puntosDisplay = fila.puntos ?? '—'

  return (
    <tr className="border-b border-stone-200 text-sm hover:bg-stone-50">
      <td className="px-3 py-2 text-center font-mono text-xs text-stone-500">
        {fila.posicion_ot}
      </td>
      <td className="px-3 py-2 font-medium text-stone-900">{fila.nombre}</td>
      <td className="px-3 py-2 text-center text-stone-700">{fila.genero}</td>
      <td className="px-3 py-2 text-stone-700">{fila.categoria_corta}</td>
      <td className="px-3 py-2 text-stone-600">{fila.club || '—'}</td>
      <td className="px-3 py-2 font-mono text-stone-700">{fila.ap}</td>
      <td className="px-3 py-2 font-mono text-xs text-stone-500">{fila.ot}</td>
      <td className="px-3 py-2 text-center text-stone-500">{fila.linea}</td>
      <td className="px-3 py-2 font-mono font-semibold text-stone-900">{rpDisplay}</td>
      <td className="px-3 py-2">
        <ChipTarjeta tarjeta={fila.tarjeta} />
      </td>
      <td className="px-3 py-2 text-right font-mono font-bold text-emerald-800">
        {puntosDisplay}
      </td>
    </tr>
  )
}
