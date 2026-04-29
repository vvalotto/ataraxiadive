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
      <span className="inline-flex min-h-8 items-center rounded-xl border border-amber-500/40 bg-amber-500/10 px-3 py-1 text-xs font-semibold text-amber-200">
        AP pendiente
      </span>
    )
  }

  if (estado === 'cerrado') {
    return (
      <span className="inline-flex min-h-8 items-center rounded-xl border border-slate-700 bg-slate-950 px-3 py-1 text-xs font-semibold text-slate-300">
        {apLabel ? `AP cerrado · ${apLabel}` : 'AP cerrado'}
      </span>
    )
  }

  return (
    <span className="inline-flex min-h-8 items-center rounded-xl border border-emerald-500/40 bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-200">
      {apLabel ? `AP declarado · ${apLabel}` : 'AP declarado'}
    </span>
  )
}
