interface PenalizacionesSelectorProps {
  disciplina: string
  count: number
  onChange: (next: number) => void
}

function admitePenalizaciones(disciplina: string) {
  return disciplina === 'DNF' || disciplina === 'DYN' || disciplina === 'DBF'
}

export function PenalizacionesSelector({
  disciplina,
  count,
  onChange,
}: PenalizacionesSelectorProps) {
  const enabled = admitePenalizaciones(disciplina)

  return (
    <div className="space-y-3 rounded-2xl bg-slate-950/70 p-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
            Penalizaciones
          </p>
          <p className="mt-1 text-sm text-slate-300">
            {enabled ? 'Cada penalizacion descuenta 3m del RP medido.' : `${disciplina} no admite penalizaciones`}
          </p>
        </div>
        <span className="rounded-full bg-slate-900 px-3 py-2 text-sm font-semibold text-white">
          {count}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <button
          type="button"
          disabled={!enabled || count === 0}
          onClick={() => onChange(Math.max(0, count - 1))}
          className="rounded-2xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm font-semibold text-white disabled:opacity-40"
        >
          −
        </button>
        <button
          type="button"
          disabled={!enabled}
          onClick={() => onChange(count + 1)}
          className="rounded-2xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm font-semibold text-white disabled:opacity-40"
        >
          +
        </button>
      </div>
    </div>
  )
}
