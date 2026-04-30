export type ResultHeroEstado = 'BLANCA' | 'ROJA' | 'DNS' | 'PENDIENTE'

interface ResultHeroProps {
  disciplina: string
  estado: ResultHeroEstado
  rp: string
  ap: string
  diferencia: string
  puntos: string
  enPodio: boolean
}

const ESTADO_STYLES: Record<ResultHeroEstado, string> = {
  BLANCA: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-100',
  ROJA: 'border-red-500/40 bg-red-500/10 text-red-100',
  DNS: 'border-slate-600 bg-slate-900 text-slate-200',
  PENDIENTE: 'border-slate-800 bg-slate-900 text-slate-200',
}

export function ResultHero({
  disciplina,
  estado,
  rp,
  ap,
  diferencia,
  puntos,
  enPodio,
}: ResultHeroProps) {
  return (
    <article className={`rounded-[1.75rem] border p-5 ${ESTADO_STYLES[estado]}`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.22em] opacity-80">
            {disciplina}
          </p>
          <p className="mt-3 text-4xl font-semibold leading-none text-white">{rp}</p>
        </div>
        <div className="flex flex-col items-end gap-2">
          <span className="rounded-full border border-current/30 bg-slate-950/30 px-3 py-1 text-xs font-semibold">
            {estado}
          </span>
          {enPodio ? (
            <span className="rounded-full border border-amber-300/40 bg-amber-300/10 px-3 py-1 text-xs font-semibold text-amber-100">
              EN PODIO
            </span>
          ) : null}
        </div>
      </div>

      <dl className="mt-5 grid grid-cols-3 gap-3 text-sm">
        <div className="rounded-2xl border border-white/10 bg-slate-950/30 p-3">
          <dt className="text-xs uppercase tracking-[0.16em] opacity-70">AP</dt>
          <dd className="mt-1 font-semibold text-white">{ap}</dd>
        </div>
        <div className="rounded-2xl border border-white/10 bg-slate-950/30 p-3">
          <dt className="text-xs uppercase tracking-[0.16em] opacity-70">Dif.</dt>
          <dd className="mt-1 font-semibold text-white">{diferencia}</dd>
        </div>
        <div className="rounded-2xl border border-white/10 bg-slate-950/30 p-3">
          <dt className="text-xs uppercase tracking-[0.16em] opacity-70">Puntos</dt>
          <dd className="mt-1 font-semibold text-white">{puntos}</dd>
        </div>
      </dl>
    </article>
  )
}
