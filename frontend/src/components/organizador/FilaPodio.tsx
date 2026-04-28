export interface FilaPodioData {
  atleta_id: string
  posicion: number
  nombre: string
  club: string
  rp: string | null
  unidad: string | null
  puntos: string
}

interface FilaPodioProps {
  fila: FilaPodioData
}

function badgeClass(posicion: number): string {
  if (posicion === 1) {
    return 'bg-amber-500/15 text-amber-500 ring-1 ring-amber-500/30'
  }
  if (posicion === 2) {
    return 'bg-slate-400/15 text-slate-500 ring-1 ring-slate-400/30'
  }
  if (posicion === 3) {
    return 'bg-amber-700/15 text-amber-700 ring-1 ring-amber-700/30'
  }
  return 'bg-stone-200 text-stone-500 ring-1 ring-stone-300'
}

function posicionLabel(posicion: number): string {
  return `${posicion}º`
}

export function FilaPodio({ fila }: FilaPodioProps) {
  const rpDisplay = fila.rp ? `${fila.rp} ${fila.unidad ?? ''}`.trim() : '—'

  return (
    <li className="grid grid-cols-[auto_minmax(0,1fr)_auto] items-start gap-3 rounded-2xl border border-stone-200/80 bg-white/75 px-3 py-3">
      <div
        className={[
          'inline-flex min-w-11 items-center justify-center rounded-full px-2 py-1 text-xs font-bold',
          badgeClass(fila.posicion),
        ].join(' ')}
      >
        {posicionLabel(fila.posicion)}
      </div>

      <div className="min-w-0">
        <p className="truncate text-sm font-semibold text-stone-900">{fila.nombre}</p>
        <p className="truncate text-xs text-stone-500">{fila.club || '—'}</p>
      </div>

      <div className="text-right">
        <p className="font-mono text-xs text-stone-500">{rpDisplay}</p>
        <p className="font-mono text-sm font-bold text-emerald-800">{fila.puntos}</p>
      </div>
    </li>
  )
}
