import {
  fetchCompetenciasPorTorneo,
  fetchGrillaCompetencia,
  type CompetenciaResumenDto,
  type GrillaAtletaDto,
} from '../../api/competencia'
import {
  ApiError,
  fetchApInscripcion,
  fetchAtletaMe,
  listarInscripcionesDeAtleta,
  type AtletaDto,
  type InscriptoDto,
} from '../../api/registro'
import { fetchTorneos, type EstadoTorneo, type TorneoDto } from '../../api/torneo'
import { formatMarca } from '../../utils/marca'

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
  atleta: AtletaDto | null
  inscripciones: InscriptoDto[]
  torneos: TorneoDto[]
  entries: AtletaPortalEntry[]
}

export const CATEGORIA_LABELS: Record<string, string> = {
  SENIOR_MASCULINO: 'Senior Masculino',
  SENIOR_FEMENINO: 'Senior Femenino',
  MASTER_MASCULINO: 'Master Masculino',
  MASTER_FEMENINO: 'Master Femenino',
  JUNIOR_MASCULINO: 'Junior Masculino',
  JUNIOR_FEMENINO: 'Junior Femenino',
}

export function formatCategoria(categoria: string): string {
  return CATEGORIA_LABELS[categoria] ?? categoria
}

export const DISCIPLINA_LABELS: Record<string, string> = {
  STA: 'STA',
  DNF: 'DNF',
  DYN: 'DYN',
  DBF: 'DBF',
  DYNB: 'DBF',
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

export function esDisciplinaTiempo(disciplina: string): boolean {
  return ['STA', 'SPE_2X50', 'SPE_4X50', 'SPE_8X50', 'SPE_16X50'].includes(disciplina)
}

export function getUnidadEsperada(disciplina: string): 'Metros' | 'Segundos' {
  return esDisciplinaTiempo(disciplina) ? 'Segundos' : 'Metros'
}

export function getUnidadLabel(unidad: string | null): string {
  if (unidad?.toLowerCase() === 'segundos') return 'mm:ss'
  return 'm'
}

export function formatAp(value: string | null, unidad: string | null): string {
  if (!value?.trim()) return 'Sin dato'
  return formatMarca(value, unidad ?? 'Metros')
}

export function secondsToApInput(value: string): string {
  const total = Number(value)
  if (!Number.isFinite(total) || total <= 0) return value
  const minutos = Math.floor(total / 60)
  const segundos = total % 60
  return `${minutos}:${String(segundos).padStart(2, '0')}`
}

export function normalizeApInput(value: string, disciplina: string): string {
  const trimmed = value.trim()
  if (!esDisciplinaTiempo(disciplina)) {
    return trimmed.replace(',', '.')
  }
  if (!trimmed.includes(':')) {
    return trimmed
  }
  if (!/^\d+:\d{1,2}$/.test(trimmed)) {
    return trimmed
  }
  const [minutosRaw, segundosRaw] = trimmed.split(':', 2)
  const minutos = Number(minutosRaw)
  const segundos = Number(segundosRaw)
  if (!Number.isFinite(minutos) || !Number.isFinite(segundos)) {
    return trimmed
  }
  if (!Number.isInteger(minutos) || !Number.isInteger(segundos) || segundos < 0 || segundos >= 60) {
    return trimmed
  }
  return String(minutos * 60 + segundos)
}

export function isApInputValido(value: string, disciplina: string): boolean {
  const trimmed = value.trim()
  if (!trimmed) {
    return false
  }
  if (!esDisciplinaTiempo(disciplina)) {
    return Number(trimmed.replace(',', '.')) > 0
  }
  if (!/^\d+:\d{2}$/.test(trimmed)) {
    return false
  }
  const normalizado = normalizeApInput(trimmed, disciplina)
  return Number(normalizado) > 0 && !normalizado.includes(':')
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

export async function loadAtletaPortalSnapshot(): Promise<AtletaPortalSnapshot> {
  const [atletaResult, torneos] = await Promise.all([
    fetchAtletaMe().catch((err) => (err instanceof ApiError && err.status === 404 ? null : Promise.reject(err))),
    fetchTorneos(),
  ])
  if (atletaResult === null) {
    return { atleta: null, inscripciones: [], torneos: [], entries: [] }
  }
  const atleta = atletaResult
  const atletaId = atleta.atleta_id
  const inscripciones = await listarInscripcionesDeAtleta(atletaId)

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

  const entries: AtletaPortalEntry[] = (
    await Promise.all(
      inscripciones.flatMap((inscripcion) => {
        const torneo = torneosById.get(inscripcion.torneo_id)
        if (!torneo) return []

        return inscripcion.disciplinas.map(async (disciplina) => {
          const competencia = (competenciasPorTorneo.get(inscripcion.torneo_id) ?? []).find(
            (item) => item.disciplina === disciplina,
          )
          const grillaEntry = competencia
            ? (grillasPorCompetencia.get(competencia.competencia_id) ?? []).find(
                (entry) => entry.atleta_id === atletaId,
              ) ?? null
            : null

          let ap: string | null = grillaEntry?.ap_declarado ?? null
          let unidad: string | null = grillaEntry?.unidad ?? null

          if (!grillaEntry && torneo.estado === 'INSCRIPCION_ABIERTA') {
            try {
              const apDto = await fetchApInscripcion(inscripcion.inscripcion_id, disciplina)
              ap = apDto.ap
              unidad = apDto.unidad
            } catch {
              // sin AP declarado
            }
          }

          const syntheticGrilla = ap ? ({ ap_declarado: ap } as GrillaAtletaDto) : null

          return {
            torneo,
            inscripcion,
            disciplina,
            competenciaId: competencia?.competencia_id ?? null,
            ap,
            unidad,
            apEstado: buildApEstado(torneo.estado, syntheticGrilla),
            ot: grillaEntry?.ot_programado ?? null,
            andarivel: grillaEntry?.andarivel ?? null,
            posicion: grillaEntry?.posicion ?? null,
          }
        })
      }),
    )
  ).filter((e): e is AtletaPortalEntry => e !== undefined)

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
