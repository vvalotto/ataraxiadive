import { useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { useQueries, useQuery } from '@tanstack/react-query'
import {
  fetchCompetenciasPorTorneo,
  type CompetenciaResumenDto,
} from '../../api/competencia'
import { listarInscriptosDetalle } from '../../api/registro'
import { fetchOverall, fetchRankingCompetencia } from '../../api/resultados'
import { fetchTorneos } from '../../api/torneo'
import { EmptyStateCard } from '../../components/organizador/EmptyStateCard'
import { FilaPodio, type FilaPodioData } from '../../components/organizador/FilaPodio'
import { OrganizadorLayout } from '../../components/organizador/OrganizadorLayout'

const PODIO_CATEGORIAS = [
  { categoria: 'JUNIOR_FEMENINO', titulo: 'JUNIOR F' },
  { categoria: 'JUNIOR_MASCULINO', titulo: 'JUNIOR M' },
  { categoria: 'SENIOR_FEMENINO', titulo: 'SENIOR F' },
  { categoria: 'SENIOR_MASCULINO', titulo: 'SENIOR M' },
  { categoria: 'MASTER_FEMENINO', titulo: 'MASTER F' },
  { categoria: 'MASTER_MASCULINO', titulo: 'MASTER M' },
] as const


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
      subtitle="Clasificación final y podios por categoría"
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

interface EntradaPodio {
  atleta_id: string
  posicion: number
  rp?: string | null
  unidad?: string | null
  puntos?: string | null
  puntos_overall?: string
  en_podio: boolean
}

interface CategoriaPodio {
  categoria: string
  entradas: EntradaPodio[]
}

function filasParaCategoria(
  categorias: CategoriaPodio[],
  categoria: string,
  inscriptosPorAtleta: Map<string, { nombre: string; club: string }>,
  kind: 'ranking' | 'overall',
): FilaPodioData[] {
  const grupo = categorias.find((g) => g.categoria === categoria)
  if (!grupo) return []
  return grupo.entradas
    .filter((e) => e.en_podio)
    .map((entrada) => {
      const inscripto = inscriptosPorAtleta.get(entrada.atleta_id)
      return {
        atleta_id: entrada.atleta_id,
        posicion: entrada.posicion,
        nombre: inscripto?.nombre ?? entrada.atleta_id,
        club: inscripto?.club ?? '-',
        rp: kind === 'ranking' && 'rp' in entrada ? (entrada.rp ?? null) : null,
        unidad: kind === 'ranking' && 'unidad' in entrada ? (entrada.unidad ?? null) : null,
        puntos:
          kind === 'ranking' && 'puntos' in entrada
            ? (entrada.puntos ?? '')
            : 'puntos_overall' in entrada
              ? (entrada.puntos_overall ?? '')
              : '',
      }
    })
}

function PodiosTorneo({ torneoId }: PodiosTorneoProps) {
  const [categoriaSeleccionada, setCategoriaSeleccionada] = useState<string>(
    PODIO_CATEGORIAS[0].categoria,
  )

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

  const rankingQueries = useQueries({
    queries: disciplinas.map((comp) => ({
      queryKey: ['ranking', comp.competencia_id, comp.disciplina],
      queryFn: () => fetchRankingCompetencia(comp.competencia_id, comp.disciplina),
      enabled: Boolean(comp.competencia_id && comp.disciplina),
      refetchInterval: 30_000,
    })),
  })

  const overallQuery = useQuery({
    queryKey: ['overall', torneoId],
    queryFn: () => fetchOverall(torneoId),
    enabled: disciplinas.length > 0,
    refetchInterval: 30_000,
    retry: false,
  })

  const inscriptosPorAtleta = useMemo(
    () =>
      new Map(
        (inscriptosQuery.data ?? []).map((i) => [
          i.atleta_id,
          { nombre: [i.apellido, i.nombre].filter(Boolean).join(', '), club: i.club },
        ]),
      ),
    [inscriptosQuery.data],
  )

  const categoriaActiva =
    PODIO_CATEGORIAS.find((c) => c.categoria === categoriaSeleccionada) ?? PODIO_CATEGORIAS[0]

  const filasOverall = useMemo(
    () =>
      filasParaCategoria(
        (overallQuery.data?.rankings ?? []) as CategoriaPodio[],
        categoriaActiva.categoria,
        inscriptosPorAtleta,
        'overall',
      ),
    [overallQuery.data, categoriaActiva, inscriptosPorAtleta],
  )

  const filasPorDisciplina = useMemo(
    () =>
      disciplinas.map((comp, idx) => ({
        disciplina: comp.disciplina,
        filas: filasParaCategoria(
          (rankingQueries[idx]?.data?.rankings ?? []) as CategoriaPodio[],
          categoriaActiva.categoria,
          inscriptosPorAtleta,
          'ranking',
        ),
        calculado: rankingQueries[idx]?.data?.calculado ?? false,
      })),
    [disciplinas, rankingQueries, categoriaActiva, inscriptosPorAtleta],
  )

  const subtitulo = torneo ? `${torneo.nombre} · ${torneo.sede.ciudad}` : 'Podios del torneo'

  return (
    <OrganizadorLayout
      title="Podios"
      activeTournamentId={torneoId}
      activeTournamentState={torneo?.estado}
      subtitle="Clasificación final y podios por categoría"
    >
      {competenciasQuery.isLoading ? (
        <section className="rounded-[2rem] border border-slate-700 bg-slate-900/75 p-5 text-sm text-slate-300">
          Cargando disciplinas...
        </section>
      ) : null}

      {!competenciasQuery.isLoading && !competenciasQuery.isError && disciplinas.length === 0 ? (
        <EmptyStateCard message="Este torneo todavia no tiene competencias operativas." />
      ) : null}

      {disciplinas.length > 0 ? (
        <>
          <section className="rounded-[2rem] border border-slate-700 bg-slate-900/85 p-5 shadow-[0_20px_60px_rgba(2,6,23,0.24)]">
            <div className="flex flex-col gap-4 border-b border-slate-800 pb-4">
              <div className="flex gap-1 border-b border-slate-800">
                {PODIO_CATEGORIAS.map(({ categoria, titulo }) => (
                  <button
                    key={categoria}
                    type="button"
                    onClick={() => setCategoriaSeleccionada(categoria)}
                    className={`flex-1 rounded-t-xl py-2 text-xs font-semibold uppercase tracking-[0.18em] transition-colors ${
                      categoriaSeleccionada === categoria
                        ? 'bg-slate-800 text-sky-400'
                        : 'text-slate-500 hover:text-slate-300'
                    }`}
                  >
                    {titulo}
                  </button>
                ))}
              </div>
              <div className="text-center">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                  Premiacion
                </p>
                <h2 className="mt-2 text-2xl font-semibold text-white">{categoriaActiva.titulo}</h2>
              </div>
            </div>
          </section>

          <section className="flex flex-col gap-6">
            <div className="rounded-[2rem] border border-amber-500/30 bg-amber-500/5 p-5 shadow-[0_20px_60px_rgba(245,158,11,0.12)]">
              <div className="mb-4 border-b border-amber-500/20 pb-3 text-center">
                <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-amber-300">
                  Overall — {categoriaActiva.titulo}
                </h3>
              </div>
              {filasOverall.length === 0 ? (
                <p className="text-sm text-slate-400">Sin datos de overall para esta categoría.</p>
              ) : (
                <ol className="space-y-2">
                  {filasOverall.map((fila) => (
                    <FilaPodio key={fila.atleta_id} fila={fila} centered />
                  ))}
                </ol>
              )}
            </div>

            <div className="flex flex-col gap-4">
              {filasPorDisciplina
                .filter(({ filas }) => filas.length > 0)
                .map(({ disciplina, filas }) => (
                <div
                  key={disciplina}
                  className="rounded-[1.75rem] border border-slate-700 bg-slate-950/60 p-4"
                >
                  <div className="mb-3 border-b border-slate-800 pb-2 text-center">
                    <h4 className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                      {disciplina}
                    </h4>
                  </div>
                  <ol className="space-y-2">
                    {filas.map((fila) => (
                      <FilaPodio key={fila.atleta_id} fila={fila} />
                    ))}
                  </ol>
                </div>
              ))}
            </div>
          </section>
        </>
      ) : null}
    </OrganizadorLayout>
  )
}
