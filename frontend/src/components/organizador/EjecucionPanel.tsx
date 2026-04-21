import { useQuery } from '@tanstack/react-query'
import {
  fetchCompetenciasPorTorneo,
  fetchEstadoCompetencia,
  fetchGrillaCompetencia,
  fetchPerformanceActual,
  fetchProgresoCompetencia,
  fetchProximasPerformances,
  type CompetenciaResumenDto,
  type EstadoCompetenciaDto,
  type GrillaAtletaDto,
  type PerformanceActualDto,
  type ProgresoCompetenciaDto,
  type ProximoAtletaDto,
} from '../../api/competencia'
import { MonitorDisciplina } from './MonitorDisciplina'

interface EjecucionPanelProps {
  torneoId: string
}

interface CompetenciaConEstado {
  competencia: CompetenciaResumenDto
  estado: EstadoCompetenciaDto
}

interface MonitorDisciplinaData {
  competencia: CompetenciaResumenDto
  progreso: ProgresoCompetenciaDto
  performanceActual: PerformanceActualDto | null
  proximas: ProximoAtletaDto[]
  grilla: GrillaAtletaDto[]
}

interface MonitorData {
  totalCompetencias: number
  todasFinalizadas: boolean
  disciplinasActivas: MonitorDisciplinaData[]
}

const FINAL_STATES = new Set(['Finalizada', 'CompetenciaFinalizada'])

function isEnEjecucion(item: CompetenciaConEstado) {
  return item.estado.estado === 'EnEjecucion'
}

function isFinalizada(item: CompetenciaConEstado) {
  return FINAL_STATES.has(item.estado.estado)
}

async function loadMonitorData(torneoId: string): Promise<MonitorData> {
  const competencias = await fetchCompetenciasPorTorneo(torneoId)
  const conEstado = await Promise.all(
    competencias.map(async (competencia) => ({
      competencia,
      estado: await fetchEstadoCompetencia(competencia.competencia_id, competencia.disciplina),
    })),
  )

  const activas = conEstado.filter(isEnEjecucion)
  const disciplinasActivas = await Promise.all(
    activas.map(async ({ competencia }) => {
      const [progreso, performanceActual, proximas, grilla] = await Promise.all([
        fetchProgresoCompetencia(competencia.competencia_id),
        fetchPerformanceActual(competencia.competencia_id),
        fetchProximasPerformances(competencia.competencia_id, competencia.disciplina),
        fetchGrillaCompetencia(competencia.competencia_id, competencia.disciplina),
      ])

      return {
        competencia,
        progreso,
        performanceActual,
        proximas,
        grilla,
      }
    }),
  )

  return {
    totalCompetencias: competencias.length,
    todasFinalizadas: conEstado.length > 0 && conEstado.every(isFinalizada),
    disciplinasActivas,
  }
}

export function EjecucionPanel({ torneoId }: EjecucionPanelProps) {
  const monitorQuery = useQuery({
    queryKey: ['monitor-ejecucion', torneoId],
    queryFn: () => loadMonitorData(torneoId),
    refetchInterval: 30000,
  })

  if (monitorQuery.isLoading) {
    return (
      <div className="rounded-lg border border-stone-200 bg-stone-50 p-4 text-sm text-stone-600">
        Cargando monitor de ejecucion...
      </div>
    )
  }

  if (monitorQuery.isError) {
    return (
      <div className="rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-900">
        No se pudo cargar el monitor de ejecucion.
      </div>
    )
  }

  const data = monitorQuery.data
  const lastUpdated = dataUpdatedLabel(monitorQuery.dataUpdatedAt)

  if (!data || data.totalCompetencias === 0) {
    return (
      <div className="rounded-lg border border-stone-200 bg-stone-50 p-4 text-sm text-stone-600">
        Ninguna disciplina en ejecucion
      </div>
    )
  }

  if (data.todasFinalizadas) {
    return (
      <div className="rounded-lg border border-emerald-700 bg-emerald-50 p-5 text-sm text-emerald-950">
        <p className="text-lg font-semibold">Todas las disciplinas completadas</p>
        <p className="mt-2">
          La transicion a premiacion queda disponible desde el panel de acciones del torneo.
        </p>
      </div>
    )
  }

  if (data.disciplinasActivas.length === 0) {
    return (
      <div className="space-y-3">
        <div className="rounded-lg border border-stone-200 bg-stone-50 p-4 text-sm text-stone-600">
          Ninguna disciplina en ejecucion
        </div>
        {lastUpdated ? (
          <p className="text-xs font-semibold uppercase text-stone-500">
            Ultima actualizacion {lastUpdated}
          </p>
        ) : null}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-stone-600">
          {data.disciplinasActivas.length} disciplinas en ejecucion
        </p>
        {lastUpdated ? (
          <p className="text-xs font-semibold uppercase text-stone-500">
            Ultima actualizacion {lastUpdated}
          </p>
        ) : null}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        {data.disciplinasActivas.map((disciplina) => (
          <MonitorDisciplina
            key={disciplina.competencia.competencia_id}
            competencia={disciplina.competencia}
            progreso={disciplina.progreso}
            performanceActual={disciplina.performanceActual}
            proximas={disciplina.proximas}
            grilla={disciplina.grilla}
          />
        ))}
      </div>
    </div>
  )
}

function dataUpdatedLabel(timestamp: number) {
  if (!timestamp) return null
  return new Date(timestamp).toLocaleTimeString('es-AR', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
}
