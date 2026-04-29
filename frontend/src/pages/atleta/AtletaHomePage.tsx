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
  const logout = useAuthStore((state) => state.logout)
  const query = useQuery({
    queryKey: ['atleta-portal-home', atletaId],
    queryFn: () => loadAtletaPortalSnapshot(),
    enabled: Boolean(atletaId),
  })

  const nextOt = query.data?.entries
    .filter((entry) => entry.ot)
    .sort((left, right) => new Date(left.ot ?? 0).getTime() - new Date(right.ot ?? 0).getTime())[0]
  const torneosActivos = Array.from(
    new Map(
      (query.data?.entries ?? []).map((entry) => [
        entry.torneo.torneo_id,
        {
          torneo: entry.torneo,
          disciplinas: (query.data?.entries ?? []).filter(
            (candidate) => candidate.torneo.torneo_id === entry.torneo.torneo_id,
          ),
        },
      ]),
    ).values(),
  )

  return (
    <AtletaShell
      title="Portal del atleta"
      subtitle="Tus próximos torneos, anuncios y estado de participación."
      actions={
        <button
          type="button"
          onClick={logout}
          className="rounded-full border border-slate-700 px-3 py-2 text-xs font-semibold text-slate-200"
        >
          Salir
        </button>
      }
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

      {query.data ? (
        <div className="space-y-4">
          <section className="rounded-[1.75rem] border border-slate-800 bg-slate-900 p-5 shadow-[0_30px_60px_-40px_rgba(56,189,248,0.5)]">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-sky-400">
              Hola
            </p>
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
                <dd className="mt-1 font-semibold text-white">{query.data.atleta.club}</dd>
              </div>
            </dl>
          </section>

          <section className="rounded-[1.75rem] border border-slate-800 bg-slate-900 p-5">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-sky-400">
                  Tu próximo OT
                </p>
                <h3 className="mt-1 text-lg font-semibold text-white">Próxima salida</h3>
              </div>
              {nextOt?.torneo ? (
                <Link
                  to="/atleta/mis-inscripciones"
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

          <section className="rounded-[1.75rem] border border-slate-800 bg-slate-900 p-5">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-sky-400">
                  Mis inscripciones activas
                </p>
                <h3 className="mt-1 text-lg font-semibold text-white">Torneos vinculados</h3>
              </div>
              <Link to="/atleta/torneos" className="text-sm font-semibold text-sky-300">
                Explorar
              </Link>
            </div>

            <div className="mt-4 space-y-3">
              {torneosActivos.length === 0 ? (
                <div className="rounded-3xl border border-slate-800 bg-slate-950/70 p-4 text-sm text-slate-400">
                  Todavía no tenés inscripciones activas.
                </div>
              ) : null}

              {torneosActivos.map(({ torneo, disciplinas }) => (
                <Link
                  key={torneo.torneo_id}
                  to="/atleta/mis-inscripciones"
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
                        {entry.apEstado === 'declarado' ? ' ✓ AP' : entry.apEstado === 'cerrado' ? ' AP cerrado' : ' Sin AP'}
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
