import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  fetchCompetenciasPorTorneo,
  fetchGrillaCompetencia,
  type CompetenciaResumenDto,
} from '../../api/competencia'
import { listarInscriptosDetalle } from '../../api/registro'
import { fetchRankingCompetencia } from '../../api/resultados'
import { fetchTorneos } from '../../api/torneo'
import { OrganizadorLayout } from '../../components/organizador/OrganizadorLayout'
import { TablaDisciplinaResultados } from '../../components/organizador/TablaDisciplinaResultados'

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
      subtitle="Seleccionar torneo para ver los resultados"
      actions={
        <Link
          to="/organizador/dashboard"
          className="rounded-full border border-stone-300 bg-white px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-stone-700"
        >
          Volver
        </Link>
      }
    >
      {torneosQuery.isLoading ? (
        <section className="rounded-[2rem] border border-stone-300/80 bg-white/80 p-5 text-sm text-stone-600">
          Cargando torneos...
        </section>
      ) : null}

      {torneosQuery.isError ? (
        <section className="rounded-[2rem] border border-red-300/60 bg-red-50 p-5 text-sm text-red-900">
          No se pudieron cargar los torneos.
        </section>
      ) : null}

      {!torneosQuery.isLoading && !torneosQuery.isError && torneosQuery.data?.length === 0 ? (
        <section className="rounded-[2rem] border border-stone-300/80 bg-white/80 p-5 text-sm text-stone-600">
          No hay torneos disponibles.
        </section>
      ) : null}

      {!torneosQuery.isLoading && !torneosQuery.isError
        ? (torneosQuery.data ?? []).map((torneo) => (
            <article
              key={torneo.torneo_id}
              className="rounded-[2rem] border border-stone-300/80 bg-white/85 p-5 shadow-[0_20px_60px_rgba(120,93,54,0.08)]"
            >
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
                    Torneo
                  </p>
                  <h2 className="mt-2 text-xl font-semibold text-stone-900">{torneo.nombre}</h2>
                  <p className="mt-2 text-sm text-stone-600">
                    {torneo.sede.nombre}, {torneo.sede.ciudad}
                  </p>
                </div>
                <Link
                  to={`/organizador/resultados?torneo_id=${torneo.torneo_id}`}
                  className="rounded-full bg-stone-900 px-4 py-2 text-center text-xs font-semibold uppercase tracking-[0.18em] text-stone-50"
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

  const disciplinas: CompetenciaResumenDto[] = competenciasQuery.data ?? []
  const disciplinaActiva = disciplinaSeleccionada ?? disciplinas[0]?.disciplina ?? null
  const competenciaActiva = disciplinas.find((d) => d.disciplina === disciplinaActiva) ?? null

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

  const isLoading =
    competenciasQuery.isLoading ||
    inscriptosQuery.isLoading ||
    grillaQuery.isLoading ||
    rankingQuery.isLoading

  const subtitulo = torneo
    ? `${torneo.nombre} · ${torneo.sede.ciudad}`
    : 'Resultados por disciplina'

  return (
    <OrganizadorLayout
      title="Resultados"
      subtitle={subtitulo}
      actions={
        <Link
          to="/organizador/dashboard"
          className="rounded-full border border-stone-300 bg-white px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-stone-700"
        >
          Volver
        </Link>
      }
    >
      {competenciasQuery.isLoading ? (
        <section className="rounded-[2rem] border border-stone-300/80 bg-white/80 p-5 text-sm text-stone-600">
          Cargando disciplinas...
        </section>
      ) : null}

      {competenciasQuery.isError ? (
        <section className="rounded-[2rem] border border-red-300/60 bg-red-50 p-5 text-sm text-red-900">
          No se pudieron cargar las disciplinas del torneo.
        </section>
      ) : null}

      {!competenciasQuery.isLoading && !competenciasQuery.isError && disciplinas.length === 0 ? (
        <section className="rounded-[2rem] border border-stone-300/80 bg-white/80 p-5 text-sm text-stone-600">
          Este torneo aún no tiene competencias generadas.
        </section>
      ) : null}

      {disciplinas.length > 0 ? (
        <section className="rounded-[2rem] border border-stone-300/80 bg-white/85 p-5 shadow-[0_20px_60px_rgba(120,93,54,0.08)]">
          <div className="flex flex-wrap gap-2 border-b border-stone-200 pb-4">
            {disciplinas.map((comp) => (
              <button
                key={comp.disciplina}
                type="button"
                onClick={() => setDisciplinaSeleccionada(comp.disciplina)}
                className={
                  disciplinaActiva === comp.disciplina
                    ? 'rounded-full bg-stone-900 px-4 py-1.5 text-xs font-semibold uppercase tracking-[0.18em] text-white'
                    : 'rounded-full border border-stone-300 bg-white px-4 py-1.5 text-xs font-semibold uppercase tracking-[0.18em] text-stone-700 hover:bg-stone-50'
                }
              >
                {comp.disciplina}
              </button>
            ))}
          </div>

          {disciplinaActiva ? (
            <div className="mt-4">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-stone-500">
                  Tabla de ejecución — {disciplinaActiva}
                </h2>
                {isLoading ? (
                  <span className="text-xs text-stone-400">Actualizando...</span>
                ) : null}
              </div>

              {grillaQuery.isError ? (
                <p className="text-sm text-red-700">Error al cargar la grilla.</p>
              ) : null}

              {!grillaQuery.isLoading && !grillaQuery.isError ? (
                <TablaDisciplinaResultados
                  grilla={grillaQuery.data ?? []}
                  ranking={rankingQuery.data ?? null}
                  inscriptos={inscriptosQuery.data ?? []}
                />
              ) : null}

              {grillaQuery.isLoading ? (
                <p className="py-6 text-center text-sm text-stone-400">Cargando tabla...</p>
              ) : null}
            </div>
          ) : null}
        </section>
      ) : null}
    </OrganizadorLayout>
  )
}
