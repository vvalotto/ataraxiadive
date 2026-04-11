export interface TorneoDto {
  torneo_id: string
  nombre: string
  descripcion: string
  fecha_inicio: string
  fecha_fin: string
  sede: {
    nombre: string
    ciudad: string
    pais: string
  }
  entidad_organizadora: {
    nombre: string
    tipo: string
  }
  estado: string
}

export async function fetchTorneos(): Promise<TorneoDto[]> {
  const response = await fetch('/torneos')

  if (!response.ok) {
    throw new Error(`Error al obtener torneos: ${response.status}`)
  }

  return response.json() as Promise<TorneoDto[]>
}

export async function fetchDisciplinasDeJuez(
  torneoId: string,
  juezId: string,
): Promise<string[]> {
  const response = await fetch(`/torneos/${torneoId}/jueces/${juezId}/disciplinas`)

  if (!response.ok) {
    throw new Error(`Error al obtener disciplinas del juez: ${response.status}`)
  }

  return response.json() as Promise<string[]>
}
