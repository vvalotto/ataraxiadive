import {
  fetchCompetenciasPorTorneo,
  fetchGrillaCompetencia,
  type CompetenciaResumenDto,
  type GrillaAtletaDto,
} from '../../api/competencia'
import {
  fetchAtleta,
  listarInscripcionesDeAtleta,
  type AtletaDto,
  type InscriptoDto,
} from '../../api/registro'
import { fetchTorneos, type EstadoTorneo, type TorneoDto } from '../../api/torneo'

export interface AtletaPortalEntry {
  torneo: TorneoDto
  inscripcion: InscriptoDto
  disciplina: string
  competenciaId: string | null
  ap: string | null
  unidad: string | null
  apEstado: 'pendiente' | 'declarado' | 'cerrado'
  ot: string | null
  andarivel: number | null
  posicion: number | null
}

export interface AtletaPortalSnapshot {
  atleta: AtletaDto
  inscripciones: InscriptoDto[]
  torneos: TorneoDto[]
  entries: AtletaPortalEntry[]
}

export const DISCIPLINA_LABELS: Record<string, string> = {
  STA: 'STA',
  DNF: 'DNF',
  DYN: 'DYN',
  DBF: 'DBF',
  DYNB: 'DYNB',
  SPE_2X50: 'SPE 2x50',
  SPE_4X50: 'SPE 4x50',
  SPE_8X50: 'SPE 8x50',
  SPE_16X50: 'SPE 16x50',
}

export function formatDisciplina(disciplina: string): string {
  return DISCIPLINA_LABELS[disciplina] ?? disciplina
}

export function formatFecha(fechaIso: string): string {
  const fecha = new Date(fechaIso)
  return new Intl.DateTimeFormat('es-AR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(fecha)
}

export function formatHora(fechaIso: string): string {
  const fecha = new Date(fechaIso)
  return new Intl.DateTimeFormat('es-AR', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(fecha)
}

export function getEstadoTorneoLabel(estado: EstadoTorneo): string {
  switch (estado) {
    case 'INSCRIPCION_ABIERTA':
      return 'Inscripciones abiertas'
    case 'PREPARACION':
      return 'Preparación'
    case 'EJECUCION':
      return 'En ejecución'
    case 'PREMIACION':
      return 'Premiación'
    case 'CERRADO':
      return 'Cerrado'
    case 'CANCELADO':
      return 'Cancelado'
    default:
      return 'Creado'
  }
}

export function getUnidadEsperada(disciplina: string): 'METROS' | 'SEGUNDOS' {
  return disciplina === 'STA' ? 'SEGUNDOS' : 'METROS'
}

export function getUnidadLabel(unidad: string | null): string {
  if (unidad === 'SEGUNDOS') return 'seg'
  return 'm'
}

function buildApEstado(
  torneoEstado: EstadoTorneo,
  grilla: GrillaAtletaDto | null,
): 'pendiente' | 'declarado' | 'cerrado' {
  if (torneoEstado !== 'INSCRIPCION_ABIERTA') {
    return 'cerrado'
  }
  return grilla?.ap_declarado?.trim() ? 'declarado' : 'pendiente'
}

export async function loadAtletaPortalSnapshot(atletaId: string): Promise<AtletaPortalSnapshot> {
  const [atleta, inscripciones, torneos] = await Promise.all([
    fetchAtleta(atletaId),
    listarInscripcionesDeAtleta(atletaId),
    fetchTorneos(),
  ])

  const torneosById = new Map(torneos.map((torneo) => [torneo.torneo_id, torneo]))
  const torneosInscriptos = inscripciones
    .map((inscripcion) => inscripcion.torneo_id)
    .filter((torneoId, index, array) => array.indexOf(torneoId) === index)

  const competenciasPorTorneo = new Map<string, CompetenciaResumenDto[]>()
  await Promise.all(
    torneosInscriptos.map(async (torneoId) => {
      try {
        const competencias = await fetchCompetenciasPorTorneo(torneoId)
        competenciasPorTorneo.set(torneoId, competencias)
      } catch {
        competenciasPorTorneo.set(torneoId, [])
      }
    }),
  )

  const grillasPorCompetencia = new Map<string, GrillaAtletaDto[]>()
  await Promise.all(
    Array.from(competenciasPorTorneo.values())
      .flat()
      .map(async (competencia) => {
        try {
          const grilla = await fetchGrillaCompetencia(
            competencia.competencia_id,
            competencia.disciplina,
          )
          grillasPorCompetencia.set(competencia.competencia_id, grilla)
        } catch {
          grillasPorCompetencia.set(competencia.competencia_id, [])
        }
      }),
  )

  const entries: AtletaPortalEntry[] = inscripciones.flatMap((inscripcion) => {
    const torneo = torneosById.get(inscripcion.torneo_id)
    if (!torneo) return []

    return inscripcion.disciplinas.map((disciplina) => {
      const competencia = (competenciasPorTorneo.get(inscripcion.torneo_id) ?? []).find(
        (item) => item.disciplina === disciplina,
      )
      const grilla = competencia
        ? (grillasPorCompetencia.get(competencia.competencia_id) ?? []).find(
            (entry) => entry.atleta_id === atletaId,
          ) ?? null
        : null

      return {
        torneo,
        inscripcion,
        disciplina,
        competenciaId: competencia?.competencia_id ?? null,
        ap: grilla?.ap_declarado ?? null,
        unidad: grilla?.unidad ?? null,
        apEstado: buildApEstado(torneo.estado, grilla),
        ot: grilla?.ot_programado ?? null,
        andarivel: grilla?.andarivel ?? null,
        posicion: grilla?.posicion ?? null,
      }
    })
  })

  return { atleta, inscripciones, torneos, entries }
}

export function buildNombreCorto(atleta: AtletaDto): string {
  return `${atleta.nombre} ${atleta.apellido}`.trim()
}

export function isTorneoProximo(estado: EstadoTorneo): boolean {
  return estado === 'CREADO'
}

export function isTorneoAbierto(estado: EstadoTorneo): boolean {
  return estado === 'INSCRIPCION_ABIERTA'
}

export function sortByDateAsc<T extends { fecha_inicio: string }>(items: T[]): T[] {
  return [...items].sort(
    (left, right) => new Date(left.fecha_inicio).getTime() - new Date(right.fecha_inicio).getTime(),
  )
}
