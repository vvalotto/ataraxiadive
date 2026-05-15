import { useQueries, useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import useAuthStore from '../../stores/useAuthStore'
import { AtletaShell } from '../../components/atleta/AtletaShell'
import { findMiResultado } from '../../components/atleta/GrupoResultados'
import { fetchRankingCompetencia } from '../../api/resultados'
import { formatMarca } from '../../utils/marca'
import {
  buildNombreCorto,
  formatAp,
  formatCategoria,
  formatDisciplina,
  formatFecha,
  formatHora,
  getEstadoTorneoLabel,
  loadAtletaPortalSnapshot,
  type AtletaPortalEntry,
} from './portalData'

function getOtTimestamp(entry: AtletaPortalEntry): number | null {
  if (!entry.ot) return null
  const timestamp = new Date(entry.ot).getTime()
  return Number.isNaN(timestamp) ? null : timestamp
}

function sortDisciplinasPorOt(entries: AtletaPortalEntry[], now = new Date()): AtletaPortalEntry[] {
  const nowTimestamp = now.getTime()

  return [...entries].sort((left, right) => {
    const leftTimestamp = getOtTimestamp(left)
    const rightTimestamp = getOtTimestamp(right)
    const leftFuture = leftTimestamp !== null && leftTimestamp > nowTimestamp
    const rightFuture = rightTimestamp !== null && rightTimestamp > nowTimestamp
    const leftPast = leftTimestamp !== null && leftTimestamp <= nowTimestamp
    const rightPast = rightTimestamp !== null && rightTimestamp <= nowTimestamp

    if (leftFuture && rightFuture) return leftTimestamp - rightTimestamp
    if (leftFuture) return -1
    if (rightFuture) return 1
    if (!leftPast && !rightPast) return 0
    if (!leftPast) return -1
    if (!rightPast) return 1
    if (leftTimestamp !== null && rightTimestamp !== null) return leftTimestamp - rightTimestamp
    return 0
  })
}

export function AtletaHomePage() {
  const atletaId = useAuthStore((state) => state.userId)
  const query = useQuery({
    queryKey: ['atleta-portal-home', atletaId],
    queryFn: () => loadAtletaPortalSnapshot(),
    enabled: Boolean(atletaId),
  })

  const allEntries = query.data?.entries ?? []

  const entriesCerradas = allEntries.filter((e) => e.torneo.estado === 'CERRADO')

  const rankingCerradoQueries = useQueries({
    queries: entriesCerradas.map((entry) => ({
      queryKey: ['atleta-ranking-home', entry.competenciaId, entry.disciplina],
      queryFn: () => fetchRankingCompetencia(entry.competenciaId!, entry.disciplina),
      enabled: Boolean(entry.competenciaId),
      retry: false,
    })),
  })

  const hayTorneoEnEjecucion = allEntries.some((entry) =>
    ['PREPARACION', 'EJECUCION'].includes(entry.torneo.estado),
  )
  const nextOt = allEntries
    .filter((entry) => entry.ot && ['PREPARACION', 'EJECUCION'].includes(entry.torneo.estado))
    .sort((left, right) => new Date(left.ot ?? 0).getTime() - new Date(right.ot ?? 0).getTime())[0]

  const torneosActivos = Array.from(
    new Map(
      allEntries
        .filter((entry) => ['PREPARACION', 'EJECUCION'].includes(entry.torneo.estado))
        .map((entry) => [
          entry.torneo.torneo_id,
          {
            torneo: entry.torneo,
            disciplinas: sortDisciplinasPorOt(
              allEntries.filter(
                (candidate) =>
                  candidate.torneo.torneo_id === entry.torneo.torneo_id &&
                  ['PREPARACION', 'EJECUCION'].includes(candidate.torneo.estado),
              ),
            ),
          },
        ]),
    ).values(),
  )

  const torneosCerradosMap = new Map<
    string,
    {
      torneo: AtletaPortalEntry['torneo']
      disciplinas: Array<{ entry: AtletaPortalEntry; miResultado: ReturnType<typeof findMiResultado> }>
    }
  >()
  entriesCerradas.forEach((entry, idx) => {
    const torneoId = entry.torneo.torneo_id
    const rankingData = rankingCerradoQueries[idx]?.data ?? null
    const miResultado = findMiResultado(rankingData, atletaId ?? '')
    const current = torneosCerradosMap.get(torneoId) ?? { torneo: entry.torneo, disciplinas: [] }
    current.disciplinas.push({ entry, miResultado })
    torneosCerradosMap.set(torneoId, current)
  })
  const torneosCerrados = Array.from(torneosCerradosMap.values()).slice(0, 3)

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
                <dd className="mt-1 font-semibold text-white">{query.data.atleta.club}</dd>
              </div>
            </dl>
          </section>

          {hayTorneoEnEjecucion ? (
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
                  to={
                    nextOt.competenciaId
                      ? `/atleta/grilla/${nextOt.competenciaId}?disciplina=${encodeURIComponent(nextOt.disciplina)}`
                      : '/atleta/mis-inscripciones'
                  }
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
                  No hay torneos activos para mostrar.
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
                        {entry.apEstado === 'declarado' || entry.apEstado === 'cerrado' ? ' ✓' : ' · Sin AP'}
                      </span>
                    ))}
                  </div>
                </Link>
              ))}
            </div>
          </section>

          {torneosCerrados.length > 0 ? (
            <section className="rounded-[1.75rem] border border-slate-800 bg-slate-900 p-5">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">
                    Historial
                  </p>
                  <h3 className="mt-1 text-lg font-semibold text-white">Torneos finalizados</h3>
                </div>
                <Link to="/atleta/resultados" className="text-sm font-semibold text-sky-300">
                  Ver todos
                </Link>
              </div>

              <div className="mt-4 space-y-3">
                {torneosCerrados.map(({ torneo, disciplinas }) => (
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
                      <span className="rounded-full border border-slate-600 px-3 py-1 text-xs font-semibold text-slate-400">
                        Finalizado
                      </span>
                    </div>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {disciplinas.map(({ entry, miResultado }) => {
                        const esDns = miResultado?.es_dns ?? false
                        const tarjeta = miResultado?.tarjeta?.toLowerCase() ?? ''
                        const esBlanca = tarjeta.includes('blanca')
                        const esRoja = tarjeta.includes('roja')
                        const rp =
                          miResultado && !esDns && miResultado.rp
                            ? formatMarca(miResultado.rp, miResultado.unidad ?? 'Metros')
                            : esDns
                            ? 'DNS'
                            : null
                        return (
                          <span
                            key={`${torneo.torneo_id}-${entry.disciplina}`}
                            className="flex items-center gap-1.5 rounded-full border border-slate-700 bg-slate-900 px-3 py-1 text-xs font-semibold text-slate-200"
                          >
                            <span
                              className={`inline-block h-2 w-2 rounded-full ${
                                esBlanca
                                  ? 'bg-white'
                                  : esRoja
                                  ? 'bg-red-500'
                                  : 'bg-slate-500'
                              }`}
                            />
                            {formatDisciplina(entry.disciplina)}
                            {rp ? <span className="text-slate-400">{rp}</span> : null}
                            {miResultado?.en_podio ? <span className="text-amber-400">🏅</span> : null}
                          </span>
                        )
                      })}
                    </div>
                  </Link>
                ))}
              </div>
            </section>
          ) : null}
        </div>
      ) : null}
    </AtletaShell>
  )
}
