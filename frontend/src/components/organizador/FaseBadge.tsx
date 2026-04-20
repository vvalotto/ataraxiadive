import type { EstadoTorneo } from '../../api/torneo'

const ESTADO_TORNEO_LABELS: Record<EstadoTorneo, string> = {
  CREADO: 'Creado',
  INSCRIPCION_ABIERTA: 'Inscripcion abierta',
  PREPARACION: 'Preparacion',
  EJECUCION: 'En ejecucion',
  PREMIACION: 'Premiacion',
  CERRADO: 'Cerrado',
  CANCELADO: 'Cancelado',
}

const ESTADO_TORNEO_STYLES: Record<EstadoTorneo, string> = {
  CREADO: 'border-stone-300 bg-stone-100 text-stone-800',
  INSCRIPCION_ABIERTA: 'border-emerald-300 bg-emerald-50 text-emerald-900',
  PREPARACION: 'border-amber-300 bg-amber-50 text-amber-900',
  EJECUCION: 'border-sky-300 bg-sky-50 text-sky-900',
  PREMIACION: 'border-violet-300 bg-violet-50 text-violet-900',
  CERRADO: 'border-stone-400 bg-stone-200 text-stone-900',
  CANCELADO: 'border-red-300 bg-red-50 text-red-900',
}

interface FaseBadgeProps {
  estado: EstadoTorneo
}

export function FaseBadge({ estado }: FaseBadgeProps) {
  return (
    <span
      className={[
        'inline-flex min-h-9 items-center rounded-lg border px-3 py-1 text-sm font-semibold',
        ESTADO_TORNEO_STYLES[estado],
      ].join(' ')}
    >
      {ESTADO_TORNEO_LABELS[estado]}
    </span>
  )
}
