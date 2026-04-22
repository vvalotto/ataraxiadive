import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import {
  fetchCompetenciasPorTorneo,
  fetchEstadoCompetencia,
  finalizarCompetencia,
  fetchGrillaCompetencia,
  fetchPerformanceActual,
  fetchProgresoCompetencia,
  fetchProximasPerformances,
  iniciarCompetencia,
  type CompetenciaResumenDto,
  type EstadoCompetenciaDto,
  type GrillaAtletaDto,
  type PerformanceActualDto,
  type ProgresoCompetenciaDto,
  type ProximoAtletaDto,
} from '../../api/competencia'
import { listarDisciplinasTorneo, type DisciplinaTorneoDto } from '../../api/torneo'
import { MonitorDisciplina } from './MonitorDisciplina'
import { ProgressBar } from './ProgressBar'

interface EjecucionPanelProps {
  torneoId: string
}

type EstadoOperativo =
  | 'sin_competencia'
  | 'sin_grilla'
  | 'sin_juez'
  | 'lista_para_iniciar'
  | 'en_ejecucion'
  | 'finalizada'
  | 'no_disponible'

interface CompetenciaConEstado {
  competencia: CompetenciaResumenDto
  estado: EstadoCompetenciaDto
  progreso: ProgresoCompetenciaDto | null
}

interface DisciplinaEjecucionItem {
  disciplina: DisciplinaTorneoDto
  competencia: CompetenciaResumenDto | null
  estado: EstadoCompetenciaDto | null
  progreso: ProgresoCompetenciaDto | null
  estadoOperativo: EstadoOperativo
}

interface EjecucionData {
  disciplinas: DisciplinaEjecucionItem[]
  todasFinalizadas: boolean
}

interface DetalleDisciplinaData {
  grilla: GrillaAtletaDto[]
  performanceActual: PerformanceActualDto | null
  proximas: ProximoAtletaDto[]
  progreso: ProgresoCompetenciaDto
}

const FINAL_STATES = new Set(['Finalizada', 'CompetenciaFinalizada'])
const RUNNING_STATES = new Set(['EnEjecucion'])
const READY_STATES = new Set(['Confirmada', 'GrillaConfirmada'])

function tieneGrillaConfirmada(estado: EstadoCompetenciaDto | null): boolean {
  return Boolean(estado?.grilla_confirmada || (estado && READY_STATES.has(estado.estado)))
}

function estadoOperativoDe(
  disciplina: DisciplinaTorneoDto,
  competencia: CompetenciaResumenDto | null,
  estado: EstadoCompetenciaDto | null,
): EstadoOperativo {
  if (!competencia || !estado) return 'sin_competencia'
  if (FINAL_STATES.has(estado.estado)) return 'finalizada'
  if (RUNNING_STATES.has(estado.estado)) return 'en_ejecucion'
  if (!tieneGrillaConfirmada(estado)) return 'sin_grilla'
  if (!disciplina.juez_id) return 'sin_juez'
  if (READY_STATES.has(estado.estado)) return 'lista_para_iniciar'
  return 'no_disponible'
}

function estadoLabel(estado: EstadoOperativo): string {
  const labels: Record<EstadoOperativo, string> = {
    sin_competencia: 'Falta grilla',
    sin_grilla: 'Grilla pendiente',
    sin_juez: 'Juez pendiente',
    lista_para_iniciar: 'Lista para iniciar',
    en_ejecucion: 'En ejecucion',
    finalizada: 'Finalizada',
    no_disponible: 'No disponible',
  }
  return labels[estado]
}

function estadoClasses(estado: EstadoOperativo): string {
  if (estado === 'lista_para_iniciar') return 'border-sky-700 bg-sky-50 text-sky-900'
  if (estado === 'en_ejecucion') return 'border-emerald-700 bg-emerald-50 text-emerald-900'
  if (estado === 'finalizada') return 'border-stone-700 bg-stone-100 text-stone-900'
  return 'border-amber-300 bg-amber-50 text-amber-900'
}

async function fetchCompetenciasConEstado(torneoId: string): Promise<CompetenciaConEstado[]> {
  const competencias = await fetchCompetenciasPorTorneo(torneoId)

  return Promise.all(
    competencias.map(async (competencia) => {
      const estado = await fetchEstadoCompetencia(competencia.competencia_id, competencia.disciplina)
      const progreso = await fetchProgresoCompetencia(competencia.competencia_id)
      return { competencia, estado, progreso }
    }),
  )
}

async function loadEjecucionData(torneoId: string): Promise<EjecucionData> {
  const [disciplinas, competenciasConEstado] = await Promise.all([
    listarDisciplinasTorneo(torneoId),
    fetchCompetenciasConEstado(torneoId),
  ])
  const competenciasPorDisciplina = new Map(
    competenciasConEstado.map((item) => [item.competencia.disciplina, item]),
  )

  const items = disciplinas.map((disciplina) => {
    const competenciaConEstado = competenciasPorDisciplina.get(disciplina.disciplina)
    const competencia = competenciaConEstado?.competencia ?? null
    const estado = competenciaConEstado?.estado ?? null

    return {
      disciplina,
      competencia,
      estado,
      progreso: competenciaConEstado?.progreso ?? null,
      estadoOperativo: estadoOperativoDe(disciplina, competencia, estado),
    }
  })

  return {
    disciplinas: items,
    todasFinalizadas:
      items.length > 0 && items.every((item) => item.estadoOperativo === 'finalizada'),
  }
}

async function loadDetalleDisciplina(item: DisciplinaEjecucionItem): Promise<DetalleDisciplinaData> {
  if (!item.competencia) {
    throw new Error('La disciplina no tiene competencia configurada.')
  }

  const [grilla, performanceActual, proximas, progreso] = await Promise.all([
    fetchGrillaCompetencia(item.competencia.competencia_id, item.disciplina.disciplina),
    fetchPerformanceActual(item.competencia.competencia_id),
    fetchProximasPerformances(item.competencia.competencia_id, item.disciplina.disciplina),
    fetchProgresoCompetencia(item.competencia.competencia_id),
  ])

  return { grilla, performanceActual, proximas, progreso }
}

function dataUpdatedLabel(timestamp: number) {
  if (!timestamp) return null
  return new Date(timestamp).toLocaleTimeString('es-AR', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
}

export function EjecucionPanel({ torneoId }: EjecucionPanelProps) {
  const queryClient = useQueryClient()
  const [selectedDisciplina, setSelectedDisciplina] = useState<string | null>(null)
  const [error, setError] = useState('')

  const ejecucionQuery = useQuery({
    queryKey: ['ejecucion-disciplinas', torneoId],
    queryFn: () => loadEjecucionData(torneoId),
    refetchInterval: 30000,
  })

  const disciplinas = useMemo(
    () => ejecucionQuery.data?.disciplinas ?? [],
    [ejecucionQuery.data],
  )

  const selectedItem =
    disciplinas.find((item) => item.disciplina.disciplina === selectedDisciplina) ??
    disciplinas[0] ??
    null

  const detalleQuery = useQuery({
    queryKey: [
      'ejecucion-detalle',
      selectedItem?.competencia?.competencia_id,
      selectedItem?.disciplina.disciplina,
    ],
    queryFn: () => loadDetalleDisciplina(selectedItem as DisciplinaEjecucionItem),
    enabled: Boolean(selectedItem?.competencia),
    refetchInterval: selectedItem?.estadoOperativo === 'en_ejecucion' ? 30000 : false,
  })

  const iniciarMutation = useMutation({
    mutationFn: async (item: DisciplinaEjecucionItem) => {
      if (!item.competencia || !item.disciplina.juez_id) return
      await iniciarCompetencia({
        competenciaId: item.competencia.competencia_id,
        disciplina: item.disciplina.disciplina,
        juezId: item.disciplina.juez_id,
      })
    },
    onSuccess: async () => {
      setError('')
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['ejecucion-disciplinas', torneoId] }),
        queryClient.invalidateQueries({ queryKey: ['ejecucion-detalle'] }),
        queryClient.invalidateQueries({ queryKey: ['monitor-ejecucion', torneoId] }),
      ])
    },
    onError: (mutationError) => setError((mutationError as Error).message),
  })

  const finalizarMutation = useMutation({
    mutationFn: async (item: DisciplinaEjecucionItem) => {
      if (!item.competencia) return
      await finalizarCompetencia({
        competenciaId: item.competencia.competencia_id,
        disciplina: item.disciplina.disciplina,
      })
    },
    onSuccess: async () => {
      setError('')
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['ejecucion-disciplinas', torneoId] }),
        queryClient.invalidateQueries({ queryKey: ['ejecucion-detalle'] }),
        queryClient.invalidateQueries({ queryKey: ['monitor-ejecucion', torneoId] }),
      ])
    },
    onError: (mutationError) => setError((mutationError as Error).message),
  })

  if (ejecucionQuery.isLoading) {
    return (
      <div className="rounded-lg border border-stone-200 bg-stone-50 p-4 text-sm text-stone-600">
        Cargando ejecucion de disciplinas...
      </div>
    )
  }

  if (ejecucionQuery.isError) {
    return (
      <div className="rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-900">
        No se pudo cargar la ejecucion de disciplinas.
      </div>
    )
  }

  if (disciplinas.length === 0) {
    return (
      <div className="rounded-lg border border-stone-200 bg-stone-50 p-4 text-sm text-stone-600">
        No hay disciplinas configuradas para ejecutar.
      </div>
    )
  }

  const lastUpdated = dataUpdatedLabel(ejecucionQuery.dataUpdatedAt)

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-stone-600">
          {disciplinas.length} disciplinas configuradas para ejecucion
        </p>
        {lastUpdated ? (
          <p className="text-xs font-semibold uppercase text-stone-500">
            Ultima actualizacion {lastUpdated}
          </p>
        ) : null}
      </div>

      {ejecucionQuery.data?.todasFinalizadas ? (
        <div className="rounded-lg border border-emerald-700 bg-emerald-50 p-4 text-sm text-emerald-950">
          Todas las disciplinas completadas. La transicion a premiacion queda disponible
          desde el panel de acciones del torneo.
        </div>
      ) : null}

      {error ? (
        <div className="rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-900">
          {error}
        </div>
      ) : null}

      <div className="grid gap-4 xl:grid-cols-[minmax(18rem,24rem)_1fr]">
        <DisciplinaMaestro
          disciplinas={disciplinas}
          selectedDisciplina={selectedItem?.disciplina.disciplina ?? null}
          onSelect={(disciplina) => {
            setError('')
            setSelectedDisciplina(disciplina)
          }}
        />

        <DisciplinaDetalle
          item={selectedItem}
          detalle={detalleQuery.data ?? null}
          isLoading={detalleQuery.isLoading}
          isError={detalleQuery.isError}
          isStarting={iniciarMutation.isPending}
          isFinishing={finalizarMutation.isPending}
          onIniciar={(item) => iniciarMutation.mutate(item)}
          onFinalizar={(item) => finalizarMutation.mutate(item)}
        />
      </div>
    </div>
  )
}

interface DisciplinaMaestroProps {
  disciplinas: DisciplinaEjecucionItem[]
  selectedDisciplina: string | null
  onSelect: (disciplina: string) => void
}

function DisciplinaMaestro({
  disciplinas,
  selectedDisciplina,
  onSelect,
}: DisciplinaMaestroProps) {
  return (
    <div className="space-y-3">
      {disciplinas.map((item) => {
        const selected = item.disciplina.disciplina === selectedDisciplina
        const progreso = item.progreso
        return (
          <button
            key={item.disciplina.disciplina}
            type="button"
            onClick={() => onSelect(item.disciplina.disciplina)}
            className={[
              'w-full rounded-lg border bg-white p-4 text-left transition',
              selected
                ? 'border-sky-700 bg-sky-50 shadow-[0_20px_60px_rgba(120,93,54,0.10)]'
                : 'border-stone-200 hover:border-stone-400',
            ].join(' ')}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-xs font-semibold uppercase text-stone-500">Disciplina</p>
                <h3 className="mt-1 text-lg font-semibold text-stone-950">
                  {item.disciplina.disciplina}
                </h3>
              </div>
              <span
                className={[
                  'rounded-lg border px-3 py-2 text-xs font-semibold',
                  estadoClasses(item.estadoOperativo),
                ].join(' ')}
              >
                {estadoLabel(item.estadoOperativo)}
              </span>
            </div>

            <div className="mt-4 space-y-2 text-sm text-stone-600">
              <p>Juez: {item.disciplina.juez_id ?? 'Sin juez asignado'}</p>
              <p>
                Competencia:{' '}
                {item.competencia ? item.competencia.competencia_id.slice(0, 8) : 'Pendiente'}
              </p>
            </div>

            {progreso ? (
              <div className="mt-4">
                <ProgressBar completed={progreso.completadas} total={progreso.total} />
              </div>
            ) : null}
          </button>
        )
      })}
    </div>
  )
}

interface DisciplinaDetalleProps {
  item: DisciplinaEjecucionItem | null
  detalle: DetalleDisciplinaData | null
  isLoading: boolean
  isError: boolean
  isStarting: boolean
  isFinishing: boolean
  onIniciar: (item: DisciplinaEjecucionItem) => void
  onFinalizar: (item: DisciplinaEjecucionItem) => void
}

function DisciplinaDetalle({
  item,
  detalle,
  isLoading,
  isError,
  isStarting,
  isFinishing,
  onIniciar,
  onFinalizar,
}: DisciplinaDetalleProps) {
  if (!item) {
    return (
      <div className="rounded-lg border border-stone-200 bg-stone-50 p-5 text-sm text-stone-600">
        Selecciona una disciplina.
      </div>
    )
  }

  const canStart = item.estadoOperativo === 'lista_para_iniciar'
  const canFinish = puedeFinalizar(item, detalle)
  const hash = item.estado?.hash_sha256

  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-sky-700 bg-sky-50/40 p-5">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase text-stone-500">Detalle</p>
            <h3 className="mt-1 text-2xl font-semibold text-stone-950">
              {item.disciplina.disciplina}
            </h3>
            <p className="mt-2 text-sm text-stone-600">
              Juez asignado: {item.disciplina.juez_id ?? 'Sin juez asignado'}
            </p>
          </div>
          <span
            className={[
              'rounded-lg border px-3 py-2 text-sm font-semibold',
              estadoClasses(item.estadoOperativo),
            ].join(' ')}
          >
            {estadoLabel(item.estadoOperativo)}
          </span>
        </div>

        {hash ? (
          <p className="mt-4 break-all rounded-lg border border-stone-200 bg-stone-50 p-3 text-xs text-stone-700">
            Hash SHA-256: {hash}
          </p>
        ) : null}

        <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-stone-600">{detalleBloqueo(item)}</p>
          {canStart ? (
            <button
              type="button"
              disabled={isStarting}
              onClick={() => onIniciar(item)}
              className="min-h-10 rounded-lg bg-emerald-800 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-stone-300"
            >
              {isStarting ? 'Habilitando...' : 'Habilitar disciplina'}
            </button>
          ) : null}
          {item.estadoOperativo === 'en_ejecucion' ? (
            <button
              type="button"
              disabled={!canFinish || isFinishing}
              onClick={() => {
                if (canFinish) onFinalizar(item)
              }}
              className="min-h-10 rounded-lg bg-stone-900 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-stone-300"
            >
              {isFinishing ? 'Finalizando...' : 'Finalizar prueba'}
            </button>
          ) : null}
        </div>
      </div>

      {item.competencia ? (
        <DetalleConCompetencia
          item={item}
          detalle={detalle}
          isLoading={isLoading}
          isError={isError}
        />
      ) : null}
    </div>
  )
}

function detalleBloqueo(item: DisciplinaEjecucionItem): string {
  const progreso = item.progreso
  const disciplina = item.disciplina.disciplina
  if (item.estadoOperativo === 'sin_competencia') {
    return `Falta generar la grilla de ${disciplina} en el tab Grilla.`
  }
  if (item.estadoOperativo === 'sin_grilla') {
    return `Falta confirmar la grilla de ${disciplina} en el tab Grilla.`
  }
  if (item.estadoOperativo === 'sin_juez') {
    return `Falta asignar juez a ${disciplina} en el tab Jueces.`
  }
  if (item.estadoOperativo === 'lista_para_iniciar') return 'La disciplina esta lista para iniciar.'
  if (item.estadoOperativo === 'en_ejecucion' && progreso) {
    const pendientes = Math.max(progreso.total - progreso.completadas, 0)
    if (pendientes > 0) return `Quedan ${pendientes} performances pendientes.`
    if (progreso.total > 0) return 'La disciplina puede finalizarse manualmente.'
  }
  if (item.estadoOperativo === 'en_ejecucion') return 'La disciplina esta en ejecucion.'
  if (item.estadoOperativo === 'finalizada') return 'La disciplina finalizo y queda en modo lectura.'
  return 'La disciplina no esta disponible para habilitar.'
}

function puedeFinalizar(
  item: DisciplinaEjecucionItem,
  detalle: DetalleDisciplinaData | null,
): boolean {
  const progreso = detalle?.progreso ?? item.progreso
  return Boolean(
    item.estadoOperativo === 'en_ejecucion' &&
      progreso &&
      progreso.total > 0 &&
      progreso.completadas === progreso.total,
  )
}

interface DetalleConCompetenciaProps {
  item: DisciplinaEjecucionItem
  detalle: DetalleDisciplinaData | null
  isLoading: boolean
  isError: boolean
}

function DetalleConCompetencia({
  item,
  detalle,
  isLoading,
  isError,
}: DetalleConCompetenciaProps) {
  if (isLoading) {
    return (
      <div className="rounded-lg border border-stone-200 bg-stone-50 p-4 text-sm text-stone-600">
        Cargando detalle de disciplina...
      </div>
    )
  }

  if (isError || !detalle) {
    return (
      <div className="rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-900">
        No se pudo cargar el detalle de la disciplina.
      </div>
    )
  }

  if (item.competencia && item.estadoOperativo === 'en_ejecucion') {
    return (
      <MonitorDisciplina
        competencia={item.competencia}
        progreso={detalle.progreso}
        performanceActual={detalle.performanceActual}
        proximas={detalle.proximas}
        grilla={detalle.grilla}
      />
    )
  }

  return (
    <div className="rounded-lg border border-stone-300 bg-white p-5">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm font-semibold text-stone-950">Grilla OT</p>
        <p className="text-sm text-stone-600">
          {detalle.progreso.completadas} / {detalle.progreso.total} completadas
        </p>
      </div>

      <div className="mt-4 overflow-x-auto rounded-lg border border-stone-200">
        <table className="min-w-full divide-y divide-stone-200 text-left text-sm">
          <thead className="bg-stone-50 text-xs font-semibold uppercase text-stone-500">
            <tr>
              <th className="px-4 py-3">Posicion</th>
              <th className="px-4 py-3">Atleta</th>
              <th className="px-4 py-3">OT</th>
              <th className="px-4 py-3">Estado</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-stone-200 bg-white">
            {detalle.grilla.map((row) => (
              <tr key={row.performance_id}>
                <td className="px-4 py-3 font-semibold text-stone-950">{row.posicion}</td>
                <td className="px-4 py-3 text-stone-700">{row.nombre_atleta}</td>
                <td className="px-4 py-3 text-stone-700">{formatOt(row.ot_programado)}</td>
                <td className="px-4 py-3 text-stone-700">{row.estado}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function formatOt(value?: string) {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleTimeString('es-AR', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
}
