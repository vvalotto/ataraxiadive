interface DisciplinaPendienteCardProps {
  disciplina: string
  ot: string
  ap: string
  andarivel: number | null
}

export function DisciplinaPendienteCard({
  disciplina,
  ot,
  ap,
  andarivel,
}: DisciplinaPendienteCardProps) {
  return (
    <article className="rounded-[1.75rem] border border-slate-800 bg-slate-900 p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-sky-400">
            {disciplina}
          </p>
          <p className="mt-2 text-base font-semibold text-white">Resultado pendiente</p>
        </div>
        <span className="rounded-full border border-slate-700 bg-slate-950/70 px-3 py-1 text-xs font-semibold text-slate-200">
          PENDIENTE
        </span>
      </div>
      <dl className="mt-4 grid grid-cols-3 gap-3 text-sm text-slate-300">
        <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-3">
          <dt className="text-xs uppercase tracking-[0.16em] text-slate-500">OT</dt>
          <dd className="mt-1 font-semibold text-white">{ot}</dd>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-3">
          <dt className="text-xs uppercase tracking-[0.16em] text-slate-500">AP</dt>
          <dd className="mt-1 font-semibold text-white">{ap}</dd>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-3">
          <dt className="text-xs uppercase tracking-[0.16em] text-slate-500">And.</dt>
          <dd className="mt-1 font-semibold text-white">{andarivel ?? '-'}</dd>
        </div>
      </dl>
      <p className="mt-4 text-sm text-slate-400">
        Resultado disponible al cierre de la disciplina
      </p>
    </article>
  )
}
