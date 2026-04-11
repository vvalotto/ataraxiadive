export interface CompetenciaResumenDto {
  competencia_id: string
  disciplina: string
  torneo_id: string
}

export interface EstadoCompetenciaDto {
  estado: string
  intervalo_minutos: number | null
  grilla_confirmada: boolean
  torneo_id: string | null
}

export async function fetchCompetenciasPorTorneo(
  torneoId: string,
): Promise<CompetenciaResumenDto[]> {
  const response = await fetch(`/competencia?torneo_id=${torneoId}`)

  if (!response.ok) {
    throw new Error(`Error al obtener competencias: ${response.status}`)
  }

  return response.json() as Promise<CompetenciaResumenDto[]>
}

export async function fetchEstadoCompetencia(
  competenciaId: string,
  disciplina: string,
): Promise<EstadoCompetenciaDto> {
  const response = await fetch(
    `/competencia/${competenciaId}/estado?disciplina=${encodeURIComponent(disciplina)}`,
  )

  if (!response.ok) {
    throw new Error(`Error al obtener estado de competencia: ${response.status}`)
  }

  return response.json() as Promise<EstadoCompetenciaDto>
}
