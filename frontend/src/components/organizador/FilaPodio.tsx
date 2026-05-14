import { formatMarca } from '../../utils/marca'

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
  centered?: boolean
}

function badgeClass(posicion: number): string {
  if (posicion === 1) {
    return 'bg-amber-500/15 text-amber-300 ring-1 ring-amber-500/30'
  }
  if (posicion === 2) {
    return 'bg-slate-400/15 text-slate-200 ring-1 ring-slate-400/30'
  }
  if (posicion === 3) {
    return 'bg-amber-700/15 text-amber-500 ring-1 ring-amber-700/30'
  }
  return 'bg-slate-800 text-slate-300 ring-1 ring-slate-700'
}

function posicionLabel(posicion: number): string {
  if (posicion === 1) return '🥇'
  if (posicion === 2) return '🥈'
  if (posicion === 3) return '🥉'
  return `${posicion}º`
}

export function FilaPodio({ fila, centered = false }: FilaPodioProps) {
  const rpDisplay = fila.rp ? formatMarca(fila.rp, fila.unidad ?? 'Metros') : ''

  if (centered) {
    return (
      <li className="flex items-center justify-center gap-3 rounded-2xl border border-slate-700 bg-slate-900/80 px-3 py-3">
        <div
          className={[
            'inline-flex min-w-11 items-center justify-center rounded-full px-2 py-1 text-xs font-bold',
            badgeClass(fila.posicion),
          ].join(' ')}
        >
          {posicionLabel(fila.posicion)}
        </div>
        <div className="text-center">
          <p className="text-sm font-semibold text-white">{fila.nombre}</p>
          {fila.club ? <p className="text-xs text-slate-400">{fila.club}</p> : null}
        </div>
      </li>
    )
  }

  return (
    <li className="grid grid-cols-[auto_minmax(0,1fr)_auto] items-start gap-3 rounded-2xl border border-slate-700 bg-slate-900/80 px-3 py-3">
      <div
        className={[
          'inline-flex min-w-11 items-center justify-center rounded-full px-2 py-1 text-xs font-bold',
          badgeClass(fila.posicion),
        ].join(' ')}
      >
        {posicionLabel(fila.posicion)}
      </div>

      <div className="min-w-0">
        <p className="truncate text-sm font-semibold text-white">{fila.nombre}</p>
        <p className="truncate text-xs text-slate-400">{fila.club || '—'}</p>
      </div>

      <div className="text-right">
        <p className="font-mono text-sm font-semibold text-slate-200">{rpDisplay}</p>
      </div>
    </li>
  )
}
