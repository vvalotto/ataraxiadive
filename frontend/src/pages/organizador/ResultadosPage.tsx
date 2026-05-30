import { useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { useQueries, useQuery } from '@tanstack/react-query'
import {
  fetchCompetenciasPorTorneo,
  fetchEstadoCompetencia,
  fetchGrillaCompetencia,
  type CompetenciaResumenDto,
} from '../../api/competencia'
import { listarInscriptosDetalle } from '../../api/registro'
import { fetchRankingCompetencia } from '../../api/resultados'
import { fetchTorneos } from '../../api/torneo'
import { EmptyStateCard } from '../../components/organizador/EmptyStateCard'
import { OrganizadorLayout } from '../../components/organizador/OrganizadorLayout'
import { TablaDisciplinaResultados } from '../../components/organizador/TablaDisciplinaResultados'

const FINAL_STATES = new Set(['Finalizada', 'CompetenciaFinalizada'])

export function ResultadosPage() {
  const [searchParams] = useSearchParams()
  const torneoId = searchParams.get('torneo_id')

  if (!torneoId) {
    return <SelectorTorneo />
  }

  return <ResultadosTorneo torneoId={torneoId} />
}

function SelectorTorneo() {
  const torneosQuery = useQuery({
    queryKey: ['torneos-organizador'],
    queryFn: fetchTorneos,
  })

    return (
      <OrganizadorLayout
      title="Resultados"
      subtitle="Rankings provisionales y finales por disciplina"
      showTournamentNavigation={false}
      simpleHeader
    >
      <div className="flex justify-end">
        <Link
          to="/organizador/torneo"
          className="rounded-full border border-slate-600 bg-slate-800 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-slate-100"
        >
          Volver
        </Link>
      </div>
      {torneosQuery.isLoading ? (
        <section className="rounded-[2rem] border border-slate-700 bg-slate-900/70 p-5 text-sm text-slate-300">
          Cargando torneos...
        </section>
      ) : null}

      {torneosQuery.isError ? (
        <section className="rounded-[2rem] border border-red-500/40 bg-red-950/50 p-5 text-sm text-red-100">
          No se pudieron cargar los torneos.
        </section>
      ) : null}

      {!torneosQuery.isLoading && !torneosQuery.isError && torneosQuery.data?.length === 0 ? (
        <section className="rounded-[2rem] border border-slate-700 bg-slate-900/70 p-5 text-sm text-slate-300">
          No hay torneos disponibles.
        </section>
      ) : null}

      {!torneosQuery.isLoading && !torneosQuery.isError
        ? (torneosQuery.data ?? []).map((torneo) => (
            <article
              key={torneo.torneo_id}
              className="rounded-[2rem] border border-slate-700 bg-slate-900/80 p-5 shadow-[0_20px_60px_rgba(2,6,23,0.32)]"
            >
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                    Torneo
                  </p>
                  <h2 className="mt-2 text-xl font-semibold text-white">{torneo.nombre}</h2>
                  <p className="mt-2 text-sm text-slate-300">
                    {torneo.sede.nombre}, {torneo.sede.ciudad}
                  </p>
                </div>
                <Link
                  to={`/organizador/resultados?torneo_id=${torneo.torneo_id}`}
                  className="rounded-full border border-sky-400 bg-sky-400/10 px-4 py-2 text-center text-xs font-semibold uppercase tracking-[0.16em] text-sky-300"
                >
                  Ver resultados
                </Link>
              </div>
            </article>
          ))
        : null}
    </OrganizadorLayout>
  )
}

interface ResultadosTorneoProps {
  torneoId: string
}

function ResultadosTorneo({ torneoId }: ResultadosTorneoProps) {
  const [disciplinaSeleccionada, setDisciplinaSeleccionada] = useState<string | null>(null)

  const torneosQuery = useQuery({
    queryKey: ['torneos-organizador'],
    queryFn: fetchTorneos,
  })
  const torneo = torneosQuery.data?.find((t) => t.torneo_id === torneoId) ?? null

  const competenciasQuery = useQuery({
    queryKey: ['competencias-torneo', torneoId],
    queryFn: () => fetchCompetenciasPorTorneo(torneoId),
  })

  const inscriptosQuery = useQuery({
    queryKey: ['inscriptos-detalle', torneoId],
    queryFn: () => listarInscriptosDetalle(torneoId),
  })

  const disciplinas: CompetenciaResumenDto[] = useMemo(
    () => competenciasQuery.data ?? [],
    [competenciasQuery.data],
  )
  const disciplinaActiva = disciplinaSeleccionada ?? disciplinas[0]?.disciplina ?? null
  const competenciaActiva = disciplinas.find((d) => d.disciplina === disciplinaActiva) ?? null

  const estadosCompetenciaQueries = useQueries({
    queries: disciplinas.map((competencia) => ({
      queryKey: ['estado-competencia', competencia.competencia_id, competencia.disciplina],
      queryFn: () => fetchEstadoCompetencia(competencia.competencia_id, competencia.disciplina),
      enabled: Boolean(competencia.competencia_id && competencia.disciplina),
    })),
  })

  const grillaQuery = useQuery({
    queryKey: ['grilla', competenciaActiva?.competencia_id, disciplinaActiva],
    queryFn: () =>
      fetchGrillaCompetencia(competenciaActiva!.competencia_id, disciplinaActiva!),
    enabled: Boolean(competenciaActiva && disciplinaActiva),
  })

  const rankingQuery = useQuery({
    queryKey: ['ranking', competenciaActiva?.competencia_id, disciplinaActiva],
    queryFn: () =>
      fetchRankingCompetencia(competenciaActiva!.competencia_id, disciplinaActiva!),
    enabled: Boolean(competenciaActiva && disciplinaActiva),
    refetchInterval: 30_000,
  })

  const estadoCompetencias = useMemo(
    () =>
      disciplinas.map((competencia, index) => ({
        competencia,
        estado: estadosCompetenciaQueries[index]?.data?.estado ?? null,
      })),
    [disciplinas, estadosCompetenciaQueries],
  )

  const disciplinasCerradas = estadoCompetencias.filter((item) =>
    item.estado ? FINAL_STATES.has(item.estado) : false,
  ).length
  const totalDisciplinas = disciplinas.length
  const overallDisponible = totalDisciplinas > 0 && disciplinasCerradas === totalDisciplinas
  const disciplinaActivaFinalizada = competenciaActiva
    ? FINAL_STATES.has(
        estadoCompetencias.find((item) => item.competencia.competencia_id === competenciaActiva.competencia_id)?.estado ??
          '',
      )
    : false

  const isLoading =
    competenciasQuery.isLoading ||
    inscriptosQuery.isLoading ||
    grillaQuery.isLoading ||
    rankingQuery.isLoading

  return (
    <OrganizadorLayout
      title="Resultados"
      activeTournamentId={torneoId}
      activeTournamentState={torneo?.estado}
      subtitle="Rankings provisionales y finales por disciplina"
    >
      <div className="flex justify-end">
        <button
          type="button"
          disabled={!overallDisponible}
          className={
            overallDisponible
              ? 'rounded-full border border-sky-400 bg-sky-400/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-sky-300'
              : 'cursor-not-allowed rounded-full border border-slate-700 bg-slate-900 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-slate-500'
          }
        >
          Publicar resultados
        </button>
      </div>
      {competenciasQuery.isLoading ? (
        <section className="rounded-[2rem] border border-slate-700 bg-slate-900/75 p-5 text-sm text-slate-300">
          Cargando disciplinas...
        </section>
      ) : null}

      {competenciasQuery.isError ? (
        <section className="rounded-[2rem] border border-red-500/40 bg-red-950/40 p-5 text-sm text-red-100">
          No se pudieron cargar las disciplinas del torneo.
        </section>
      ) : null}

      {!competenciasQuery.isLoading && !competenciasQuery.isError && disciplinas.length === 0 ? (
        <EmptyStateCard message="Este torneo todavía no tiene competencias operativas." />
      ) : null}

      {disciplinas.length > 0 ? (
        <section className="rounded-[2rem] border border-slate-700 bg-slate-900/85 p-5 shadow-[0_20px_60px_rgba(2,6,23,0.24)]">
          <div className="flex flex-col gap-4 border-b border-slate-800 pb-4">
            <div className="flex gap-1 border-b border-slate-800 -mb-5 pb-0">
              {disciplinas.map((comp) => (
                <button
                  key={comp.disciplina}
                  type="button"
                  onClick={() => setDisciplinaSeleccionada(comp.disciplina)}
                  className={`flex-1 rounded-t-xl px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] transition-colors ${
                    disciplinaActiva === comp.disciplina
                      ? 'bg-slate-800 text-sky-400'
                      : 'text-slate-500 hover:text-slate-300'
                  }`}
                >
                  {comp.disciplina}
                </button>
              ))}
            </div>

            {disciplinaActiva ? (
              <div className="mt-6 flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                    Ranking por disciplina
                  </p>
                  <h2 className="mt-2 text-2xl font-semibold text-white">{disciplinaActiva}</h2>
                  <p className="mt-2 text-sm text-slate-300">
                    Tabla de ejecucion ordenada por OT con anuncio, RP, tarjeta y andarivel.
                  </p>
                </div>
                <div className="flex flex-wrap gap-3 text-xs uppercase tracking-[0.16em] text-slate-400">
                  <span className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1.5">
                    {disciplinaActivaFinalizada ? 'Disciplina finalizada' : 'Disciplina en seguimiento'}
                  </span>
                  {isLoading ? (
                    <span className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1.5">
                      Actualizando
                    </span>
                  ) : null}
                </div>
              </div>
            ) : null}
          </div>

          {disciplinaActiva ? (
            <div className="mt-4">
              {grillaQuery.isError ? (
                <p className="rounded-[1.5rem] border border-red-500/40 bg-red-950/30 p-4 text-sm text-red-100">
                  Error al cargar la grilla.
                </p>
              ) : null}

              {!grillaQuery.isLoading && !grillaQuery.isError ? (
                <TablaDisciplinaResultados
                  grilla={grillaQuery.data ?? []}
                  ranking={rankingQuery.data ?? null}
                  inscriptos={inscriptosQuery.data ?? []}
                />
              ) : null}

              {grillaQuery.isLoading ? (
                <p className="py-6 text-center text-sm text-slate-400">Cargando tabla...</p>
              ) : null}
            </div>
          ) : null}
        </section>
      ) : null}
    </OrganizadorLayout>
  )
}
