import { useQueries, useQuery } from '@tanstack/react-query'
import { AtletaShell } from '../../components/atleta/AtletaShell'
import {
  GrupoResultados,
  groupByTorneo,
  findMiResultado,
  type ResultadoEntry,
} from '../../components/atleta/GrupoResultados'
import { fetchOverall, fetchRankingCompetencia } from '../../api/resultados'
import { fetchGrillaCompetencia } from '../../api/competencia'
import { loadAtletaPortalSnapshot } from './portalData'

export function AtletaResultadosPage() {
  const snapshotQuery = useQuery({
    queryKey: ['atleta-resultados-snapshot'],
    queryFn: loadAtletaPortalSnapshot,
  })

  const entries = snapshotQuery.data?.entries ?? []
  const atletaId = snapshotQuery.data?.atleta?.atleta_id ?? ''

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

  const resultados: ResultadoEntry[] = entries
    .filter((entry) => ['EJECUCION', 'PREMIACION', 'CERRADO'].includes(entry.torneo.estado))
    .map((entry) => {
      const index = entries.indexOf(entry)
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
          <p className="text-sm font-semibold text-white">No hay resultados para mostrar.</p>
          <p className="mt-2 text-sm text-slate-400">
            Tus resultados aparecerán una vez que el torneo esté en ejecución y el juez registre tus performances.
          </p>
        </div>
      ) : null}

      {snapshotQuery.data && grupos.length > 0 ? (
        <div className="space-y-8">
          {grupos.map((grupo) => (
            <GrupoResultados
              key={grupo.torneoId}
              grupo={grupo}
              atletaId={atletaId}
              nombresPorCompetencia={nombresPorCompetencia}
              overallPorTorneo={overallPorTorneo}
            />
          ))}
        </div>
      ) : null}
    </AtletaShell>
  )
}
