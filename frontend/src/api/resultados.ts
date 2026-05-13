export interface RankingEntradaDto {
  posicion: number
  atleta_id: string
  rp: string | null
  unidad: string | null
  tarjeta: string | null
  es_dns: boolean
  en_podio: boolean
  puntos: string | null
  motivo_dq: string | null
}

export interface RankingCategoriaDto {
  categoria: string
  entradas: RankingEntradaDto[]
}

export interface RankingCompetenciaDto {
  calculado: boolean
  rankings: RankingCategoriaDto[]
}

export interface OverallEntradaDto {
  posicion: number
  atleta_id: string
  puntos_overall: string
  detalle: Record<string, string>
  en_podio: boolean
}

export interface OverallCategoriaDto {
  categoria: string
  entradas: OverallEntradaDto[]
}

export interface OverallDto {
  calculado: boolean
  rankings: OverallCategoriaDto[]
}

export async function fetchRankingCompetencia(
  competenciaId: string,
  disciplina: string,
): Promise<RankingCompetenciaDto> {
  const response = await fetch(
    `/resultados/${competenciaId}/ranking?disciplina=${encodeURIComponent(disciplina)}`,
  )

  if (!response.ok) {
    throw new Error(`Error al obtener ranking: ${response.status}`)
  }

  return response.json() as Promise<RankingCompetenciaDto>
}

export async function fetchOverall(torneoId: string): Promise<OverallDto> {
  const response = await fetch(`/resultados/${torneoId}/overall`)

  if (!response.ok) {
    throw new Error(`Error al obtener overall: ${response.status}`)
  }

  return response.json() as Promise<OverallDto>
}
