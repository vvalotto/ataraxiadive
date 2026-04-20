interface EstadoAPBadgeProps {
  ap?: string | null
  unidad?: string | null
}

export function EstadoAPBadge({ ap, unidad }: EstadoAPBadgeProps) {
  const hasAp = Boolean(ap && ap.trim())
  if (!hasAp) {
    return (
      <span className="inline-flex min-h-8 items-center rounded-lg border border-amber-300 bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-900">
        Sin AP
      </span>
    )
  }

  return (
    <span className="inline-flex min-h-8 items-center rounded-lg border border-emerald-300 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-900">
      AP registrado · {ap}
      {unidad ? unidad : ''}
    </span>
  )
}
