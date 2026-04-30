import { useQueries, useQuery } from '@tanstack/react-query'
import { AtletaShell } from '../../components/atleta/AtletaShell'
import { DisciplinaPendienteCard } from '../../components/atleta/DisciplinaPendienteCard'
import { OverallCard } from '../../components/atleta/OverallCard'
import { RankingCard } from '../../components/atleta/RankingCard'
import { ResultHero, type ResultHeroEstado } from '../../components/atleta/ResultHero'
import {
  fetchOverall,
  fetchRankingCompetencia,
  type RankingCompetenciaDto,
  type RankingEntradaDto,
} from '../../api/resultados'
import { fetchGrillaCompetencia } from '../../api/competencia'
import { formatMarca } from '../../utils/marca'
import {
  formatAp,
  formatCategoria,
  formatDisciplina,
  formatHora,
  loadAtletaPortalSnapshot,
  type AtletaPortalEntry,
} from './portalData'

interface ResultadoEntry {
  entry: AtletaPortalEntry
  ranking: RankingCompetenciaDto | null
  miResultado: RankingEntradaDto | null
}

function findMiResultado(
  ranking: RankingCompetenciaDto | null,
  atletaId: string,
): RankingEntradaDto | null {
  if (!ranking?.calculado) return null
  return (
    ranking.rankings
      .flatMap((categoria) => categoria.entradas)
      .find((entrada) => entrada.atleta_id === atletaId) ?? null
  )
}

function findMiCategoriaEntradas(
  ranking: RankingCompetenciaDto | null,
  atletaId: string,
): { entradas: RankingEntradaDto[]; categoria: string } | null {
  if (!ranking?.calculado) return null
  const cat = ranking.rankings.find((c) =>
    c.entradas.some((e) => e.atleta_id === atletaId),
  )
  if (!cat) return null
  return { entradas: cat.entradas, categoria: cat.categoria }
}

function getEstadoResultado(resultado: RankingEntradaDto): ResultHeroEstado {
  if (resultado.es_dns) return 'DNS'
  if (resultado.tarjeta?.toLowerCase().includes('roja')) return 'ROJA'
  if (resultado.tarjeta?.toLowerCase().includes('blanca')) return 'BLANCA'
  return 'PENDIENTE'
}

function formatResultado(resultado: RankingEntradaDto): string {
  if (resultado.es_dns || !resultado.rp) return '-'
  return formatMarca(resultado.rp, resultado.unidad ?? 'Metros')
}

function calcularDiferencia(params: {
  ap: string | null
  rp: string | null
  unidad: string | null
  esDns: boolean
}): string {
  if (params.esDns || !params.ap || !params.rp) return '-'
  const ap = Number(params.ap)
  const rp = Number(params.rp)
  if (!Number.isFinite(ap) || !Number.isFinite(rp)) return '-'
  const diff = rp - ap
  const sign = diff > 0 ? '+' : ''
  const suffix = params.unidad?.toLowerCase() === 'segundos' ? 's' : 'm'
  return `${sign}${Number(diff.toFixed(2))}${suffix}`
}

function groupByTorneo(resultados: ResultadoEntry[]): Array<{
  torneoId: string
  torneoNombre: string
  resultados: ResultadoEntry[]
}> {
  const groups = new Map<
    string,
    { torneoId: string; torneoNombre: string; resultados: ResultadoEntry[] }
  >()
  resultados.forEach((resultado) => {
    const torneoId = resultado.entry.torneo.torneo_id
    const current = groups.get(torneoId) ?? {
      torneoId,
      torneoNombre: resultado.entry.torneo.nombre,
      resultados: [],
    }
    current.resultados.push(resultado)
    groups.set(torneoId, current)
  })
  return Array.from(groups.values())
}

export function AtletaResultadosPage() {
  const snapshotQuery = useQuery({
    queryKey: ['atleta-resultados-snapshot'],
    queryFn: loadAtletaPortalSnapshot,
  })

  const entries = snapshotQuery.data?.entries ?? []
  const atletaId = snapshotQuery.data?.atleta.atleta_id ?? ''

  const rankingQueries = useQueries({
    queries: entries.map((entry) => ({
      queryKey: ['atleta-ranking', entry.competenciaId, entry.disciplina],
      queryFn: () => fetchRankingCompetencia(entry.competenciaId!, entry.disciplina),
      enabled: Boolean(entry.competenciaId),
      retry: false,
    })),
  })

  const grillaQueries = useQueries({
    queries: entries.map((entry) => ({
      queryKey: ['atleta-grilla-nombres', entry.competenciaId, entry.disciplina],
      queryFn: () => fetchGrillaCompetencia(entry.competenciaId!, entry.disciplina),
      enabled: Boolean(entry.competenciaId),
      retry: false,
    })),
  })

  const torneoIds = [...new Set(entries.map((e) => e.torneo.torneo_id))]
  const overallQueries = useQueries({
    queries: torneoIds.map((torneoId) => ({
      queryKey: ['atleta-overall', torneoId],
      queryFn: () => fetchOverall(torneoId),
      retry: false,
    })),
  })

  const nombresPorCompetencia = new Map<string, Map<string, string>>()
  entries.forEach((entry, index) => {
    if (!entry.competenciaId) return
    const grilla = grillaQueries[index]?.data ?? []
    const mapa = new Map<string, string>()
    grilla.forEach((fila) => mapa.set(fila.atleta_id, fila.nombre_atleta))
    nombresPorCompetencia.set(entry.competenciaId, mapa)
  })

  const overallPorTorneo = new Map(
    torneoIds.map((torneoId, index) => [torneoId, overallQueries[index]?.data ?? null]),
  )

  const resultados: ResultadoEntry[] = entries.map((entry, index) => {
    const ranking = rankingQueries[index]?.data ?? null
    return {
      entry,
      ranking,
      miResultado: findMiResultado(ranking, atletaId),
    }
  })
  const grupos = groupByTorneo(resultados)

  return (
    <AtletaShell title="Mis resultados" subtitle="Resultados publicados y ranking por disciplina.">
      {snapshotQuery.isLoading ? (
        <div className="rounded-3xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-300">
          Cargando resultados...
        </div>
      ) : null}

      {snapshotQuery.isError ? (
        <div className="rounded-3xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-100">
          No se pudieron cargar tus resultados.
        </div>
      ) : null}

      {snapshotQuery.data && resultados.length === 0 ? (
        <div className="rounded-[1.75rem] border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm font-semibold text-white">Aún no tenés resultados publicados.</p>
          <p className="mt-2 text-sm text-slate-400">
            Tus resultados aparecerán cuando tengas inscripciones con disciplinas publicadas.
          </p>
        </div>
      ) : null}

      {snapshotQuery.data && grupos.length > 0 ? (
        <div className="space-y-8">
          {grupos.map((grupo) => {
            const overall = overallPorTorneo.get(grupo.torneoId) ?? null
            const categoriaAtleta = grupo.resultados
              .map(({ ranking }) => findMiCategoriaEntradas(ranking, atletaId)?.categoria)
              .find(Boolean) ?? ''
            const categoriaLabel = formatCategoria(categoriaAtleta)
            const nombresParaOverall = (() => {
              const mapa = new Map<string, string>()
              grupo.resultados.forEach(({ entry }) => {
                if (!entry.competenciaId) return
                const m = nombresPorCompetencia.get(entry.competenciaId)
                m?.forEach((nombre, id) => mapa.set(id, nombre))
              })
              return mapa
            })()

            return (
              <section key={grupo.torneoId} className="space-y-3">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.22em] text-sky-400">
                    Torneo
                  </p>
                  <h2 className="mt-1 text-lg font-semibold text-white">{grupo.torneoNombre}</h2>
                </div>

                {grupo.resultados.map(({ entry, miResultado, ranking }) => {
                  const nombresPorId = entry.competenciaId
                    ? (nombresPorCompetencia.get(entry.competenciaId) ?? new Map())
                    : new Map<string, string>()

                  const miCategoria = findMiCategoriaEntradas(ranking, atletaId)

                  if (!miResultado) {
                    return (
                      <DisciplinaPendienteCard
                        key={`${entry.torneo.torneo_id}-${entry.disciplina}`}
                        disciplina={formatDisciplina(entry.disciplina)}
                        ot={entry.ot ? formatHora(entry.ot) : '-'}
                        ap={formatAp(entry.ap, entry.unidad)}
                        andarivel={entry.andarivel}
                      />
                    )
                  }

                  const estado = getEstadoResultado(miResultado)
                  return (
                    <div key={`${entry.torneo.torneo_id}-${entry.disciplina}`} className="space-y-2">
                      <ResultHero
                        disciplina={formatDisciplina(entry.disciplina)}
                        estado={estado}
                        rp={formatResultado(miResultado)}
                        ap={formatAp(entry.ap, entry.unidad)}
                        diferencia={calcularDiferencia({
                          ap: entry.ap,
                          rp: miResultado.rp,
                          unidad: miResultado.unidad ?? entry.unidad,
                          esDns: miResultado.es_dns,
                        })}
                        puntos={miResultado.es_dns ? '-' : (miResultado.puntos ?? '-')}
                        enPodio={miResultado.en_podio}
                      />
                      {miCategoria ? (
                        <RankingCard
                          categoriaLabel={formatCategoria(miCategoria.categoria)}
                          entradas={miCategoria.entradas}
                          unidad={entry.unidad}
                          nombresPorId={nombresPorId}
                          atletaId={atletaId}
                          calculado={ranking?.calculado ?? false}
                        />
                      ) : null}
                    </div>
                  )
                })}

                <OverallCard
                  overall={overall}
                  atletaId={atletaId}
                  nombresPorId={nombresParaOverall}
                  categoriaAtleta={categoriaAtleta}
                  categoriaLabel={categoriaLabel}
                />
              </section>
            )
          })}
        </div>
      ) : null}
    </AtletaShell>
  )
}
