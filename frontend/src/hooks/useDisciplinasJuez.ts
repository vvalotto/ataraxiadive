import { useQuery } from '@tanstack/react-query'
import { useMemo } from 'react'
import { fetchCompetenciasPorTorneo, fetchEstadoCompetencia } from '../api/competencia'
import { fetchDisciplinasDeJuez, fetchTorneos } from '../api/torneo'
import useAuthStore from '../stores/useAuthStore'

export interface DisciplinaViewModel {
  disciplina: string
  estado: 'ACTIVA' | 'PENDIENTE'
  competenciaId: string
}

function esEnEjecucion(estado: string): boolean {
  return estado === 'EJECUCION' || estado === 'EnEjecucion'
}

export function useDisciplinasJuez() {
  const email = useAuthStore((s) => s.email)
  const userId = useAuthStore((s) => s.userId)

  const torneoActivoQuery = useQuery({
    queryKey: ['torneos'],
    queryFn: fetchTorneos,
    select: (torneos) => torneos.find((torneo) => esEnEjecucion(torneo.estado)) ?? null,
  })

  const disciplinasQuery = useQuery({
    queryKey: ['disciplinas-juez', torneoActivoQuery.data?.torneo_id, userId],
    queryFn: () => fetchDisciplinasDeJuez(torneoActivoQuery.data!.torneo_id, userId!),
    enabled: Boolean(torneoActivoQuery.data?.torneo_id && userId),
  })

  const disciplinasViewQuery = useQuery({
    queryKey: ['mis-disciplinas', torneoActivoQuery.data?.torneo_id, userId],
    enabled: Boolean(torneoActivoQuery.data?.torneo_id && userId && disciplinasQuery.data),
    queryFn: async (): Promise<DisciplinaViewModel[]> => {
      const torneoId = torneoActivoQuery.data!.torneo_id
      const disciplinas = disciplinasQuery.data ?? []
      const competencias = await fetchCompetenciasPorTorneo(torneoId)

      const resultados = await Promise.all(
        disciplinas.map(async (disciplina) => {
          const competencia = competencias.find((item) => item.disciplina === disciplina)
          if (!competencia) return null
          const estado = await fetchEstadoCompetencia(competencia.competencia_id, disciplina)
          return {
            disciplina,
            competenciaId: competencia.competencia_id,
            estado: esEnEjecucion(estado.estado) ? 'ACTIVA' : 'PENDIENTE',
          } satisfies DisciplinaViewModel
        }),
      )

      return resultados.filter((item): item is DisciplinaViewModel => item !== null)
    },
  })

  const subtitle = useMemo(() => {
    if (!torneoActivoQuery.data) return email ?? 'Juez'
    return `${email ?? 'Juez'} · ${torneoActivoQuery.data.nombre}`
  }, [email, torneoActivoQuery.data])

  return {
    torneoActivo: torneoActivoQuery.data ?? null,
    disciplinas: disciplinasViewQuery.data ?? [],
    subtitle,
    isLoading:
      torneoActivoQuery.isLoading ||
      disciplinasQuery.isLoading ||
      disciplinasViewQuery.isLoading,
    hasError:
      torneoActivoQuery.isError || disciplinasQuery.isError || disciplinasViewQuery.isError,
  }
}
