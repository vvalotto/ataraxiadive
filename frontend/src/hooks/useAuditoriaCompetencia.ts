import { useQueries } from '@tanstack/react-query'
import {
  fetchEstadoCompetencia,
  fetchGrillaCompetencia,
  type EstadoCompetenciaDto,
  type GrillaAtletaDto,
} from '../api/competencia'
import {
  fetchRankingCompetencia,
  type RankingCompetenciaDto,
} from '../api/resultados'

interface UseAuditoriaCompetenciaArgs {
  competenciaId: string | undefined
  disciplina: string | undefined
}

interface UseAuditoriaCompetenciaResult {
  estado: EstadoCompetenciaDto | undefined
  grilla: GrillaAtletaDto[] | undefined
  ranking: RankingCompetenciaDto | undefined
  isLoading: boolean
  hasError: boolean
}

export function useAuditoriaCompetencia({
  competenciaId,
  disciplina,
}: UseAuditoriaCompetenciaArgs): UseAuditoriaCompetenciaResult {
  const enabled = Boolean(competenciaId && disciplina)
  const [estadoQuery, grillaQuery, rankingQuery] = useQueries({
    queries: [
      {
        queryKey: ['estado-competencia', competenciaId, disciplina],
        queryFn: () => fetchEstadoCompetencia(competenciaId!, disciplina!),
        enabled,
      },
      {
        queryKey: ['grilla-competencia', competenciaId, disciplina],
        queryFn: () => fetchGrillaCompetencia(competenciaId!, disciplina!),
        enabled,
      },
      {
        queryKey: ['ranking-competencia', competenciaId, disciplina],
        queryFn: () => fetchRankingCompetencia(competenciaId!, disciplina!),
        enabled,
      },
    ],
  })

  return {
    estado: estadoQuery.data,
    grilla: grillaQuery.data,
    ranking: rankingQuery.data,
    isLoading: estadoQuery.isLoading || grillaQuery.isLoading || rankingQuery.isLoading,
    hasError: estadoQuery.isError || grillaQuery.isError,
  }
}
