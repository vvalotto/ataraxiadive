import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import useAuthStore from '../../stores/useAuthStore'
import { AtletaShell } from '../../components/atleta/AtletaShell'
import {
  buildNombreCorto,
  formatAp,
  formatCategoria,
  formatDisciplina,
  formatFecha,
  formatHora,
  getEstadoTorneoLabel,
  loadAtletaPortalSnapshot,
} from './portalData'


export function AtletaHomePage() {
  const atletaId = useAuthStore((state) => state.userId)
  const query = useQuery({
    queryKey: ['atleta-portal-home', atletaId],
    queryFn: () => loadAtletaPortalSnapshot(),
    enabled: Boolean(atletaId),
  })

  const allEntries = query.data?.entries ?? []

  const ESTADOS_ACTIVOS = ['INSCRIPCION_ABIERTA', 'PREPARACION', 'EJECUCION', 'PREMIACION']

  const hayTorneoEnEjecucion = allEntries.some((e) => e.torneo.estado === 'EJECUCION')
  const nextOt = allEntries
    .filter((e) => e.ot && e.torneo.estado === 'EJECUCION')
    .sort((left, right) => new Date(left.ot ?? 0).getTime() - new Date(right.ot ?? 0).getTime())[0]

  const torneosActivos = Array.from(
    new Map(
      allEntries
        .filter((e) => ESTADOS_ACTIVOS.includes(e.torneo.estado))
        .map((e) => [
          e.torneo.torneo_id,
          {
            torneo: e.torneo,
            disciplinas: allEntries.filter(
              (c) => c.torneo.torneo_id === e.torneo.torneo_id && ESTADOS_ACTIVOS.includes(c.torneo.estado),
            ),
          },
        ]),
    ).values(),
  ).sort(
    (left, right) =>
      new Date(left.torneo.fecha_inicio).getTime() - new Date(right.torneo.fecha_inicio).getTime(),
  )

  return (
    <AtletaShell
      title="Portal del atleta"
      subtitle="Tus próximos torneos, anuncios y estado de participación."
    >
      {query.isLoading ? (
        <div className="rounded-3xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-300">
          Cargando portal del atleta...
        </div>
      ) : null}

      {query.isError ? (
        <div className="rounded-3xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-100">
          No se pudo cargar el portal del atleta.
        </div>
      ) : null}

      {query.data?.atleta === null ? (
        <div className="rounded-3xl border border-slate-700 bg-slate-900 p-6 text-center text-sm text-slate-400">
          <p className="text-base font-semibold text-slate-200">No hay torneos activos.</p>
          <p className="mt-2">Cuando te inscribas en un torneo, tu información y disciplinas aparecerán aquí.</p>
        </div>
      ) : null}

      {query.data?.atleta ? (
        <div className="space-y-4">
          <section className="rounded-[1.75rem] border border-slate-800 bg-slate-900 p-5 shadow-[0_30px_60px_-40px_rgba(56,189,248,0.5)]">
            <h2 className="mt-2 text-2xl font-semibold text-white">
              {buildNombreCorto(query.data.atleta)}
            </h2>
            <dl className="mt-4 grid grid-cols-2 gap-3 text-sm text-slate-300">
              <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-3">
                <dt className="text-xs uppercase tracking-[0.18em] text-slate-500">Categoría</dt>
                <dd className="mt-1 font-semibold text-white">{formatCategoria(query.data.atleta.categoria)}</dd>
              </div>
              <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-3">
                <dt className="text-xs uppercase tracking-[0.18em] text-slate-500">Club</dt>
                <dd className="mt-1 font-semibold text-white">{query.data.atleta.club || '—'}</dd>
              </div>
            </dl>
          </section>

          {hayTorneoEnEjecucion ? (
            <section className="rounded-[1.75rem] border border-sky-500/20 bg-slate-900 p-5">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.22em] text-sky-400">
                    En competencia
                  </p>
                  <h3 className="mt-1 text-lg font-semibold text-white">Torneo en ejecución</h3>
                </div>
                {nextOt?.competenciaId ? (
                  <Link
                    to={`/atleta/grilla/${nextOt.competenciaId}?disciplina=${encodeURIComponent(nextOt.disciplina)}`}
                    className="text-sm font-semibold text-sky-300"
                  >
                    Ver grilla
                  </Link>
                ) : null}
              </div>

              {nextOt ? (
                <div className="mt-4 rounded-3xl border border-sky-500/30 bg-sky-500/10 p-4">
                  <p className="text-sm font-semibold text-white">{nextOt.torneo.nombre}</p>
                  <p className="mt-1 text-xs uppercase tracking-[0.18em] text-sky-300">
                    {formatDisciplina(nextOt.disciplina)}
                  </p>
                  <p className="mt-3 text-3xl font-semibold text-white">{formatHora(nextOt.ot ?? '')}</p>
                  <p className="mt-2 text-sm text-slate-300">
                    Andarivel {nextOt.andarivel ?? '—'} · Posición {nextOt.posicion ?? '—'}
                  </p>
                  <p className="mt-1 text-sm text-slate-300">
                    AP {formatAp(nextOt.ap, nextOt.unidad)}
                  </p>
                </div>
              ) : (
                <div className="mt-4 rounded-3xl border border-slate-800 bg-slate-950/70 p-4 text-sm text-slate-400">
                  Todavía no tenés OT asignado. Tus horarios aparecerán acá cuando la grilla esté publicada.
                </div>
              )}
            </section>
          ) : null}

          <section className="rounded-[1.75rem] border border-slate-800 bg-slate-900 p-5">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-sky-400">
                  Mis inscripciones
                </p>
              </div>
              {torneosActivos.length > 0 ? (
                <Link to="/atleta/mis-inscripciones" className="text-sm font-semibold text-sky-300">
                  Ver detalle
                </Link>
              ) : null}
            </div>

            <div className="mt-4 space-y-3">
              {torneosActivos.length === 0 ? (
                <div className="rounded-3xl border border-slate-800 bg-slate-950/70 p-4 text-sm text-slate-400">
                  No tenés inscripciones activas.
                </div>
              ) : null}

              {torneosActivos.map(({ torneo, disciplinas }) => (
                <Link
                  key={torneo.torneo_id}
                  to={`/atleta/torneos/${torneo.torneo_id}`}
                  className="block rounded-3xl border border-slate-800 bg-slate-950/70 p-4"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h4 className="text-base font-semibold text-white">{torneo.nombre}</h4>
                      <p className="mt-1 text-sm text-slate-400">
                        {formatFecha(torneo.fecha_inicio)} · {torneo.sede.ciudad}
                      </p>
                    </div>
                    <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-semibold text-slate-200">
                      {getEstadoTorneoLabel(torneo.estado)}
                    </span>
                  </div>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {disciplinas.map((entry) => (
                      <span
                        key={`${torneo.torneo_id}-${entry.disciplina}`}
                        className="rounded-full border border-slate-700 bg-slate-900 px-3 py-1 text-xs font-semibold text-slate-200"
                      >
                        {formatDisciplina(entry.disciplina)}
                        {entry.apEstado === 'declarado' || entry.apEstado === 'cerrado' ? ' ✓' : ' · Sin AP'}
                      </span>
                    ))}
                  </div>
                </Link>
              ))}
            </div>
          </section>
        </div>
      ) : null}
    </AtletaShell>
  )
}
