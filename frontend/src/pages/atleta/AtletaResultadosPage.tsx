import { useQueries, useQuery } from '@tanstack/react-query'
import { AtletaShell } from '../../components/atleta/AtletaShell'
import { DisciplinaPendienteCard } from '../../components/atleta/DisciplinaPendienteCard'
import { ResultHero, type ResultHeroEstado } from '../../components/atleta/ResultHero'
import {
  fetchRankingCompetencia,
  type RankingCompetenciaDto,
  type RankingEntradaDto,
} from '../../api/resultados'
import { formatMarca } from '../../utils/marca'
import {
  formatAp,
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

  const rankingQueries = useQueries({
    queries: (snapshotQuery.data?.entries ?? []).map((entry) => ({
      queryKey: ['atleta-ranking', entry.competenciaId, entry.disciplina],
      queryFn: () => fetchRankingCompetencia(entry.competenciaId!, entry.disciplina),
      enabled: Boolean(entry.competenciaId),
      retry: false,
    })),
  })

  const resultados: ResultadoEntry[] = (snapshotQuery.data?.entries ?? []).map((entry, index) => {
    const ranking = rankingQueries[index]?.data ?? null
    return {
      entry,
      ranking,
      miResultado: findMiResultado(ranking, snapshotQuery.data?.atleta.atleta_id ?? ''),
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
        <div className="space-y-5">
          {grupos.map((grupo) => (
            <section key={grupo.torneoId} className="space-y-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-sky-400">
                  Torneo
                </p>
                <h2 className="mt-1 text-lg font-semibold text-white">{grupo.torneoNombre}</h2>
              </div>

              {grupo.resultados.map(({ entry, miResultado }) => {
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
                  <ResultHero
                    key={`${entry.torneo.torneo_id}-${entry.disciplina}`}
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
                )
              })}
            </section>
          ))}
        </div>
      ) : null}
    </AtletaShell>
  )
}
