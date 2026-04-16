export interface RankingEntradaDto {
  posicion: number
  atleta_id: string
  rp: string | null
  unidad: string | null
  tarjeta: string | null
  es_dns: boolean
  en_podio: boolean
}

export interface RankingCategoriaDto {
  categoria: string
  entradas: RankingEntradaDto[]
}

export interface RankingCompetenciaDto {
  calculado: boolean
  rankings: RankingCategoriaDto[]
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
