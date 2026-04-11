interface DisciplinaCardProps {
  disciplina: string
  estado: 'ACTIVA' | 'PENDIENTE'
  onSelect?: () => void
}

export function DisciplinaCard({ disciplina, estado, onSelect }: DisciplinaCardProps) {
  const isActive = estado === 'ACTIVA'

  return (
    <button
      type="button"
      onClick={isActive ? onSelect : undefined}
      disabled={!isActive}
      className={[
        'w-full rounded-3xl border p-4 text-left transition',
        isActive
          ? 'border-sky-500/60 bg-slate-900 shadow-lg shadow-sky-950/20'
          : 'border-slate-800 bg-slate-900/60 opacity-75',
      ].join(' ')}
    >
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
            Disciplina
          </p>
          <h2 className="mt-2 text-xl font-semibold text-slate-50">{disciplina}</h2>
        </div>
        <span
          className={[
            'rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em]',
            isActive ? 'bg-emerald-500/15 text-emerald-300' : 'bg-slate-700 text-slate-300',
          ].join(' ')}
        >
          {estado}
        </span>
      </div>
      <p className="mt-3 text-sm text-slate-400">
        {isActive
          ? 'Lista para abrir la grilla de salida.'
          : 'Visible, pero bloqueada hasta que la competencia inicie.'}
      </p>
    </button>
  )
}
