import { useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { useQueries, useQuery } from '@tanstack/react-query'
import {
  fetchCompetenciasPorTorneo,
  fetchEstadoCompetencia,
  type CompetenciaResumenDto,
} from '../../api/competencia'
import { listarInscriptosDetalle } from '../../api/registro'
import { fetchOverall, fetchRankingCompetencia } from '../../api/resultados'
import { fetchTorneos } from '../../api/torneo'
import { EmptyStateCard } from '../../components/organizador/EmptyStateCard'
import { OrganizadorLayout } from '../../components/organizador/OrganizadorLayout'
import { PodiosSection, type PodioCategoriaGroup } from '../../components/organizador/PodiosSection'

const PODIO_CATEGORIAS = [
  { categoria: 'SENIOR_MASCULINO', titulo: 'SENIOR M' },
  { categoria: 'SENIOR_FEMENINO', titulo: 'SENIOR F' },
  { categoria: 'MASTER_MASCULINO', titulo: 'MASTER M' },
  { categoria: 'MASTER_FEMENINO', titulo: 'MASTER F' },
  { categoria: 'JUNIOR_MASCULINO', titulo: 'JUNIOR M' },
  { categoria: 'JUNIOR_FEMENINO', titulo: 'JUNIOR F' },
] as const

const FINAL_STATES = new Set(['Finalizada', 'CompetenciaFinalizada'])

export function PodiosPage() {
  const [searchParams] = useSearchParams()
  const torneoId = searchParams.get('torneo_id')

  if (!torneoId) {
    return <SelectorTorneoPodios />
  }

  return <PodiosTorneo torneoId={torneoId} />
}

function SelectorTorneoPodios() {
  const torneosQuery = useQuery({
    queryKey: ['torneos-organizador'],
    queryFn: fetchTorneos,
  })

  return (
    <OrganizadorLayout
      title="Podios"
      subtitle="Seleccionar torneo para ver los podios"
      showTournamentNavigation={false}
      simpleHeader
      actions={
        <Link
          to="/organizador/torneo"
          className="rounded-full border border-slate-600 bg-slate-800 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-slate-100"
        >
          Volver
        </Link>
      }
    >
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
                  to={`/organizador/podios?torneo_id=${torneo.torneo_id}`}
                  className="rounded-full border border-sky-400 bg-sky-400/10 px-4 py-2 text-center text-xs font-semibold uppercase tracking-[0.16em] text-sky-300"
                >
                  Ver podios
                </Link>
              </div>
            </article>
          ))
        : null}
    </OrganizadorLayout>
  )
}

interface PodiosTorneoProps {
  torneoId: string
}

function nombreVisible(nombre: string, apellido: string): string {
  const partes = [apellido, nombre].filter(Boolean)
  return partes.join(', ')
}

function buildPodioGroups(params: {
  categorias: Array<
    | {
        categoria: string
        entradas: Array<{
          atleta_id: string
          posicion: number
          rp: string | null
          unidad: string | null
          puntos: string | null
        }>
      }
    | {
        categoria: string
        entradas: Array<{
          atleta_id: string
          posicion: number
          puntos_overall: string
        }>
      }
  >
  inscriptos: Array<{
    atleta_id: string
    nombre: string
    apellido: string
    club: string
  }>
  kind: 'ranking' | 'overall'
}): PodioCategoriaGroup[] {
  const inscriptosPorAtleta = new Map(
    params.inscriptos.map((inscripto) => [
      inscripto.atleta_id,
      {
        nombre: nombreVisible(inscripto.nombre, inscripto.apellido),
        club: inscripto.club,
      },
    ]),
  )

  const categoriasPorCodigo = new Map(params.categorias.map((grupo) => [grupo.categoria, grupo]))

  return PODIO_CATEGORIAS.map(({ categoria, titulo }) => {
    const grupo = categoriasPorCodigo.get(categoria)
    const filas =
      grupo?.entradas.map((entrada) => {
        const inscripto = inscriptosPorAtleta.get(entrada.atleta_id)
        return {
          atleta_id: entrada.atleta_id,
          posicion: entrada.posicion,
          nombre: inscripto?.nombre ?? entrada.atleta_id,
          club: inscripto?.club ?? '-',
          rp: params.kind === 'ranking' && 'rp' in entrada ? entrada.rp : null,
          unidad: params.kind === 'ranking' && 'unidad' in entrada ? entrada.unidad : null,
          puntos:
            params.kind === 'ranking' && 'puntos' in entrada
              ? (entrada.puntos ?? '-')
              : 'puntos_overall' in entrada
                ? entrada.puntos_overall
                : '-',
        }
      }) ?? []

    return { categoria, titulo, filas }
  })
}

function PodiosTorneo({ torneoId }: PodiosTorneoProps) {
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

  const rankingQuery = useQuery({
    queryKey: ['ranking', competenciaActiva?.competencia_id, disciplinaActiva],
    queryFn: () =>
      fetchRankingCompetencia(competenciaActiva!.competencia_id, disciplinaActiva!),
    enabled: Boolean(competenciaActiva && disciplinaActiva),
    refetchInterval: 30_000,
  })

  const overallQuery = useQuery({
    queryKey: ['overall', torneoId],
    queryFn: () => fetchOverall(torneoId),
    enabled: disciplinas.length > 0,
    refetchInterval: 30_000,
    retry: false,
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
  const estadosLoading = estadosCompetenciaQueries.some((query) => query.isLoading)
  const disciplinaActivaFinalizada = competenciaActiva
    ? FINAL_STATES.has(
        estadoCompetencias.find(
          (item) => item.competencia.competencia_id === competenciaActiva.competencia_id,
        )?.estado ?? '',
      )
    : false

  const podioDisciplina = useMemo(
    () =>
      buildPodioGroups({
        categorias: rankingQuery.data?.rankings ?? [],
        inscriptos: inscriptosQuery.data ?? [],
        kind: 'ranking',
      }),
    [rankingQuery.data, inscriptosQuery.data],
  )

  const podioOverall = useMemo(
    () =>
      buildPodioGroups({
        categorias: overallQuery.data?.rankings ?? [],
        inscriptos: inscriptosQuery.data ?? [],
        kind: 'overall',
      }),
    [overallQuery.data, inscriptosQuery.data],
  )

  const subtitulo = torneo ? `${torneo.nombre} · ${torneo.sede.ciudad}` : 'Podios del torneo'
  const progresoLabel =
    totalDisciplinas > 0 ? `${disciplinasCerradas} de ${totalDisciplinas} disciplinas cerradas` : null

  return (
    <OrganizadorLayout
      title="Podios"
      activeTournamentId={torneoId}
      activeTournamentState={torneo?.estado}
      subtitle={progresoLabel ? `${subtitulo} · ${progresoLabel}` : subtitulo}
    >
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
        <EmptyStateCard message="Este torneo todavia no tiene competencias operativas." />
      ) : null}

      {disciplinas.length > 0 ? (
        <>
          <section className="rounded-[2rem] border border-slate-700 bg-slate-900/85 p-5 shadow-[0_20px_60px_rgba(2,6,23,0.24)]">
            <div className="flex flex-col gap-4 border-b border-slate-800 pb-4">
              <div className="flex flex-wrap items-center gap-2">
                {disciplinas.map((comp) => (
                  <button
                    key={comp.disciplina}
                    type="button"
                    onClick={() => setDisciplinaSeleccionada(comp.disciplina)}
                    className={
                      disciplinaActiva === comp.disciplina
                        ? 'rounded-full border border-sky-400 bg-sky-400/10 px-4 py-1.5 text-xs font-semibold uppercase tracking-[0.18em] text-sky-300'
                        : 'rounded-full border border-slate-700 bg-slate-950 px-4 py-1.5 text-xs font-semibold uppercase tracking-[0.18em] text-slate-300 hover:border-slate-500 hover:text-white'
                    }
                  >
                    {comp.disciplina}
                  </button>
                ))}
              </div>

              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                  Premiacion por categoria
                </p>
                <h2 className="mt-2 text-2xl font-semibold text-white">
                  {disciplinaActiva ?? 'Sin disciplina'}
                </h2>
                <p className="mt-2 text-sm text-slate-300">
                  Podios por disciplina y acumulado overall separados de la vista tecnica de resultados.
                </p>
              </div>
            </div>
          </section>

          <section className="grid gap-4 xl:grid-cols-[1.15fr_0.85fr]">
            <div className="flex flex-col gap-4">
              {disciplinaActiva ? (
                <PodiosSection
                  title={`Podios — ${disciplinaActiva}`}
                  subtitle="Resultados agrupados por categoria y genero con puntaje FAAS."
                  groups={podioDisciplina}
                  emptyState={
                    !disciplinaActivaFinalizada
                      ? {
                          title: 'Podios disponibles al cerrar la disciplina',
                          detail: 'La disciplina seleccionada todavia no esta finalizada.',
                        }
                      : rankingQuery.isError
                        ? {
                            title: 'No se pudo cargar el ranking de la disciplina',
                            detail: 'Volve a intentar cuando el calculo de resultados este disponible.',
                          }
                        : rankingQuery.data && !rankingQuery.data.calculado
                          ? {
                              title: 'Ranking aun no calculado',
                              detail: 'Los podios se publican cuando la disciplina finaliza con ranking calculado.',
                            }
                          : null
                  }
                />
              ) : null}
            </div>

            <div className="flex flex-col gap-4">
              <PodiosSection
                title="Overall"
                subtitle="Acumulado del torneo por categoria y genero."
                groups={podioOverall}
                emptyState={
                  estadosLoading
                    ? {
                        title: 'Verificando cierre de disciplinas',
                        detail: 'Estamos comprobando el estado operativo del torneo.',
                      }
                    : !overallDisponible
                      ? {
                          title: 'Disponible al cerrar todas las disciplinas',
                          detail: `(${disciplinasCerradas} de ${totalDisciplinas} disciplinas cerradas)`,
                        }
                      : overallQuery.isError
                        ? {
                            title: 'No se pudo cargar el overall del torneo',
                            detail: 'El calculo acumulado todavia no esta disponible.',
                          }
                        : overallQuery.data && !overallQuery.data.calculado
                          ? {
                              title: 'Overall aun no calculado',
                              detail: 'El acumulado se habilita cuando el backend publica el ranking overall.',
                            }
                          : null
                }
              />
            </div>
          </section>
        </>
      ) : null}
    </OrganizadorLayout>
  )
}
