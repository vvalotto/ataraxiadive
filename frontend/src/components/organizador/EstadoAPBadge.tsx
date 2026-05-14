import { formatMarca } from '../../utils/marca'

interface EstadoAPBadgeProps {
  estado: 'pendiente' | 'declarado' | 'cerrado'
  ap?: string | null
  unidad?: string | null
}

function formatAp(ap?: string | null, unidad?: string | null): string | null {
  if (!ap?.trim()) return null
  return formatMarca(ap, unidad ?? 'Metros')
}

export function EstadoAPBadge({ estado, ap, unidad }: EstadoAPBadgeProps) {
  const apLabel = formatAp(ap, unidad)

  if (estado === 'pendiente') {
    return (
      <span className="inline-flex min-h-8 items-center rounded-xl bg-amber-500/10 px-3 py-1 text-xs font-semibold text-amber-200">
        AP pendiente
      </span>
    )
  }

  if (estado === 'cerrado') {
    return (
      <span className="inline-flex min-h-8 items-center rounded-xl bg-slate-950 px-3 py-1 text-xs font-semibold text-slate-300">
        {apLabel ?? '—'}
      </span>
    )
  }

  return (
    <span className="inline-flex min-h-8 items-center rounded-xl bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-200">
      {apLabel ?? 'AP declarado'}
    </span>
  )
}
