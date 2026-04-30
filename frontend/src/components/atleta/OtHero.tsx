interface OtHeroProps {
  ot: string
  andarivel: number | null
  posicion: number | null
  ap: string
  torneo: string
  disciplina: string
}

export function OtHero({
  ot,
  andarivel,
  posicion,
  ap,
  torneo,
  disciplina,
}: OtHeroProps) {
  return (
    <section className="rounded-[1.75rem] border border-sky-500/30 bg-sky-500/10 p-5 shadow-[0_30px_60px_-40px_rgba(56,189,248,0.65)]">
      <p className="text-xs font-semibold uppercase tracking-[0.22em] text-sky-300">
        Tu Tiempo Oficial
      </p>
      <p className="mt-3 text-[52px] font-semibold leading-none text-white">{ot}</p>
      <p className="mt-3 text-sm font-semibold text-slate-100">
        Andarivel {andarivel ?? '-'} · Posicion {posicion ?? '-'}
      </p>
      <p className="mt-1 text-sm text-slate-300">
        {torneo} · {disciplina}
      </p>
      <div className="mt-4 flex flex-wrap gap-2">
        <span className="rounded-full border border-sky-300/30 bg-slate-950/40 px-3 py-1 text-xs font-semibold text-sky-100">
          AP: {ap}
        </span>
        <span className="rounded-full border border-emerald-400/30 bg-emerald-400/10 px-3 py-1 text-xs font-semibold text-emerald-100">
          Grilla publicada
        </span>
      </div>
    </section>
  )
}
