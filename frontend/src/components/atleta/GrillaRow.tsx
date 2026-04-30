interface GrillaRowProps {
  posicion: number
  nombre: string
  ot: string
  andarivel: number
  isSelf: boolean
}

export function GrillaRow({
  posicion,
  nombre,
  ot,
  andarivel,
  isSelf,
}: GrillaRowProps) {
  return (
    <div
      className={[
        'rounded-3xl border p-4',
        isSelf
          ? 'border-sky-400/40 border-l-4 bg-sky-500/10'
          : 'border-slate-800 bg-slate-950/70',
      ].join(' ')}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-full border border-slate-700 bg-slate-900 text-sm font-semibold text-slate-200">
              {posicion}
            </span>
            <p className="truncate text-sm font-semibold text-white">{nombre}</p>
            {isSelf ? (
              <span className="rounded-full border border-sky-400/40 bg-sky-400/10 px-2 py-0.5 text-[11px] font-semibold text-sky-100">
                TU
              </span>
            ) : null}
          </div>
        </div>
        <div className="shrink-0 text-right">
          <p className="text-sm font-semibold text-white">{ot}</p>
          <p className="mt-1 text-xs text-slate-400">Andarivel {andarivel}</p>
        </div>
      </div>
    </div>
  )
}
