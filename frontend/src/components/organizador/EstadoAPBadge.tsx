interface EstadoAPBadgeProps {
  estado: 'pendiente' | 'declarado' | 'cerrado'
  ap?: string | null
  unidad?: string | null
}

function formatAp(ap?: string | null, unidad?: string | null): string | null {
  if (!ap?.trim()) return null
  return `${ap}${unidad ? ` ${unidad}` : ''}`
}

export function EstadoAPBadge({ estado, ap, unidad }: EstadoAPBadgeProps) {
  const apLabel = formatAp(ap, unidad)

  if (estado === 'pendiente') {
    return (
      <span className="inline-flex min-h-8 items-center rounded-lg border border-amber-300 bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-900">
        AP pendiente
      </span>
    )
  }

  if (estado === 'cerrado') {
    return (
      <span className="inline-flex min-h-8 items-center rounded-lg border border-slate-300 bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-800">
        {apLabel ? `AP cerrado · ${apLabel}` : 'AP cerrado'}
      </span>
    )
  }

  return (
    <span className="inline-flex min-h-8 items-center rounded-lg border border-emerald-300 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-900">
      {apLabel ? `AP declarado · ${apLabel}` : 'AP declarado'}
    </span>
  )
}
