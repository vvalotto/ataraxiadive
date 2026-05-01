import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import useAuthStore from '../../stores/useAuthStore'
import { AtletaShell } from '../../components/atleta/AtletaShell'
import {
  formatAp,
  formatDisciplina,
  formatFecha,
  formatHora,
  loadAtletaPortalSnapshot,
} from './portalData'

export function AtletaMisInscripcionesPage() {
  const atletaId = useAuthStore((state) => state.userId)
  const query = useQuery({
    queryKey: ['atleta-mis-inscripciones', atletaId],
    queryFn: () => loadAtletaPortalSnapshot(),
    enabled: Boolean(atletaId),
  })

  const enEjecucion = (query.data?.entries ?? []).filter(
    (entry) => entry.torneo.estado !== 'INSCRIPCION_ABIERTA',
  )
  const abiertas = (query.data?.entries ?? []).filter(
    (entry) => entry.torneo.estado === 'INSCRIPCION_ABIERTA',
  )

  return (
    <AtletaShell title="Mis inscripciones" subtitle="Estado visible por torneo y disciplina, con acceso al anuncio de AP.">
      {query.isLoading ? (
        <div className="rounded-3xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-300">
          Cargando inscripciones...
        </div>
      ) : null}

      {query.isError ? (
        <div className="rounded-3xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-100">
          No se pudieron cargar tus inscripciones.
        </div>
      ) : null}

      {query.data ? (
        <div className="space-y-5">
          <section>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-sky-400">
              En ejecución
            </p>
            <div className="mt-3 space-y-3">
              {enEjecucion.length === 0 ? (
                <div className="rounded-3xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-400">
                  No hay disciplinas en ejecución para tus inscripciones activas.
                </div>
              ) : null}

              {enEjecucion.map((entry) => (
                <div
                  key={`${entry.torneo.torneo_id}-${entry.disciplina}`}
                  className="rounded-3xl border border-slate-800 bg-slate-900 p-4"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-white">{entry.torneo.nombre}</p>
                      <p className="mt-1 text-xs uppercase tracking-[0.18em] text-sky-300">
                        {formatDisciplina(entry.disciplina)}
                      </p>
                    </div>
                    <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-semibold text-slate-200">
                      AP cerrado
                    </span>
                  </div>
                  <dl className="mt-4 grid grid-cols-2 gap-3 text-sm text-slate-300">
                    <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-3">
                      <dt className="text-xs uppercase tracking-[0.18em] text-slate-500">AP</dt>
                      <dd className="mt-1 font-semibold text-white">
                        {formatAp(entry.ap, entry.unidad)}
                      </dd>
                    </div>
                    <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-3">
                      <dt className="text-xs uppercase tracking-[0.18em] text-slate-500">OT</dt>
                      <dd className="mt-1 font-semibold text-white">
                        {entry.ot ? formatHora(entry.ot) : 'Pendiente'}
                      </dd>
                    </div>
                  </dl>
                  <p className="mt-3 text-sm text-slate-400">
                    Andarivel {entry.andarivel ?? '—'} · Posición {entry.posicion ?? '—'}
                  </p>
                  {entry.competenciaId ? (
                    <Link
                      to={`/atleta/grilla/${entry.competenciaId}?disciplina=${encodeURIComponent(entry.disciplina)}`}
                      className="mt-4 flex min-h-10 items-center justify-center rounded-2xl border border-sky-500/40 bg-sky-500/10 px-4 py-2 text-sm font-semibold text-sky-200"
                    >
                      Ver grilla
                    </Link>
                  ) : null}
                </div>
              ))}
            </div>
          </section>

          <section>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-sky-400">
              Inscripciones abiertas
            </p>
            <div className="mt-3 space-y-3">
              {abiertas.length === 0 ? (
                <div className="rounded-3xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-400">
                  No tenés inscripciones abiertas para declarar AP.
                </div>
              ) : null}

              {abiertas.map((entry) => (
                <div
                  key={`${entry.torneo.torneo_id}-${entry.disciplina}`}
                  className="rounded-3xl border border-slate-800 bg-slate-900 p-4"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-white">{entry.torneo.nombre}</p>
                      <p className="mt-1 text-xs uppercase tracking-[0.18em] text-sky-300">
                        {formatDisciplina(entry.disciplina)}
                      </p>
                    </div>
                    <span
                      className={[
                        'rounded-full px-3 py-1 text-xs font-semibold',
                        entry.apEstado === 'declarado'
                          ? 'border border-emerald-500/30 bg-emerald-500/10 text-emerald-200'
                          : 'border border-amber-500/30 bg-amber-500/10 text-amber-100',
                      ].join(' ')}
                    >
                      {entry.apEstado === 'declarado' ? 'AP declarado' : 'AP pendiente'}
                    </span>
                  </div>
                  <p className="mt-3 text-sm text-slate-400">
                    Deadline visible: el anuncio permanece abierto mientras el torneo siga en inscripción.
                  </p>
                  <p className="mt-2 text-sm text-slate-400">
                    Inicio del torneo: {formatFecha(entry.torneo.fecha_inicio)}
                  </p>
                  <div className="mt-4 flex items-center justify-between gap-3">
                    <p className="text-sm text-slate-300">
                      {entry.ap ? `AP actual ${formatAp(entry.ap, entry.unidad)}` : '⚠ Sin AP declarado'}
                    </p>
                    {!entry.ap ? (
                      <Link
                        to={`/atleta/ap/${entry.torneo.torneo_id}/${entry.disciplina}`}
                        className="rounded-2xl bg-sky-500 px-4 py-2 text-sm font-semibold text-slate-950"
                      >
                        Declarar AP
                      </Link>
                    ) : (
                      <span className="rounded-2xl border border-slate-700 px-4 py-2 text-sm font-semibold text-slate-300">
                        AP bloqueado
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>
      ) : null}
    </AtletaShell>
  )
}
