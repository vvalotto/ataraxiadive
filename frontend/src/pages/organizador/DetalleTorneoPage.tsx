import { useQueries, useQuery } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import { Link, useParams, useSearchParams } from 'react-router-dom'
import {
  fetchCompetenciasPorTorneo,
  fetchEstadoCompetencia,
} from '../../api/competencia'
import {
  fetchTorneo,
  abrirInscripcion,
  cerrarInscripcion,
  cerrarTorneo,
  iniciarEjecucion,
  iniciarPremiacion,
  listarDisciplinasTorneo,
  type EstadoTorneo,
  type TorneoDto,
} from '../../api/torneo'
import { AccionesPanel } from '../../components/organizador/AccionesPanel'
import { FaseBadge } from '../../components/organizador/FaseBadge'
import { OrganizadorLayout } from '../../components/organizador/OrganizadorLayout'
import { TorneoRouteSelector } from '../../components/organizador/TorneoRouteSelector'

export function DetalleTorneoPage() {
  const { torneoId: torneoIdParam } = useParams<{ torneoId: string }>()
  const [searchParams] = useSearchParams()
  const torneoId = torneoIdParam ?? searchParams.get('torneo_id') ?? undefined

  if (!torneoId) {
    return (
      <OrganizadorLayout
        title="Panel"
        subtitle="Seleccionar torneo para operar el panel principal"
      >
        <TorneoRouteSelector
          description="El panel operativo ahora vive en una ruta primaria propia. Seleccioná un torneo para mantener la navegación del shell mientras revisás estado, inscriptos y ejecución."
          ctaLabel="Abrir panel"
          buildHref={(nextTorneoId) => `/organizador/panel?torneo_id=${nextTorneoId}`}
        />
      </OrganizadorLayout>
    )
  }

  return <DetalleTorneoContent torneoId={torneoId} />
}

interface DetalleTorneoContentProps {
  torneoId: string
}

interface EstadoOption {
  value: EstadoTorneo
  label: string
}

const ESTADO_LABELS: Record<EstadoTorneo, string> = {
  CREADO: 'Creado',
  INSCRIPCION_ABIERTA: 'Inscripciones abiertas',
  PREPARACION: 'Preparación',
  EJECUCION: 'En ejecución',
  PREMIACION: 'Premiación',
  CERRADO: 'Cerrado',
  CANCELADO: 'Cancelado',
}

const TRANSICIONES_ESTADO: Partial<Record<EstadoTorneo, Array<{
  target: EstadoTorneo
  run: (torneoId: string) => Promise<void>
}>>> = {
  CREADO: [{ target: 'INSCRIPCION_ABIERTA', run: abrirInscripcion }],
  INSCRIPCION_ABIERTA: [{ target: 'PREPARACION', run: cerrarInscripcion }],
  PREPARACION: [{ target: 'EJECUCION', run: iniciarEjecucion }],
  EJECUCION: [{ target: 'PREMIACION', run: iniciarPremiacion }],
  PREMIACION: [{ target: 'CERRADO', run: cerrarTorneo }],
}

function DetalleTorneoContent({ torneoId }: DetalleTorneoContentProps) {
  const [transitionError, setTransitionError] = useState('')
  const torneoQuery = useQuery({
    queryKey: ['torneo', torneoId],
    queryFn: () => fetchTorneo(torneoId ?? ''),
    enabled: Boolean(torneoId),
  })
  const disciplinasQuery = useQuery({
    queryKey: ['torneo-disciplinas', torneoId],
    queryFn: () => listarDisciplinasTorneo(torneoId ?? ''),
    enabled: Boolean(torneoId),
  })
  const competenciasQuery = useQuery({
    queryKey: ['competencias-torneo', torneoId],
    queryFn: () => fetchCompetenciasPorTorneo(torneoId ?? ''),
    enabled: Boolean(torneoId),
  })
  const estadoCompetenciasQueries = useQueries({
    queries:
      competenciasQuery.data?.map((competencia) => ({
        queryKey: ['competencia-estado', competencia.competencia_id, competencia.disciplina],
        queryFn: () =>
          fetchEstadoCompetencia(competencia.competencia_id, competencia.disciplina),
        enabled: torneoQuery.data?.estado === 'EJECUCION',
      })) ?? [],
  })
  const isPremiacionStatusLoading =
    torneoQuery.data?.estado === 'EJECUCION' &&
    (disciplinasQuery.isLoading ||
      competenciasQuery.isLoading ||
      estadoCompetenciasQueries.some((query) => query.isLoading))
  const premiacionPendientes = useMemo(() => {
    if (torneoQuery.data?.estado !== 'EJECUCION') return null
    const disciplinas = disciplinasQuery.data ?? []
    const competencias = competenciasQuery.data ?? []
    const estadosPorCompetencia = new Map(
      estadoCompetenciasQueries.map((query, index) => [
        competencias[index]?.competencia_id,
        query.data?.estado,
      ]),
    )

    return disciplinas
      .filter((disciplinaTorneo) => {
        const competencia = competencias.find(
          (item) => item.disciplina === disciplinaTorneo.disciplina,
        )
        if (!competencia) return true
        return estadosPorCompetencia.get(competencia.competencia_id) !== 'Finalizada'
      })
      .map((disciplinaTorneo) => disciplinaTorneo.disciplina)
  }, [
    competenciasQuery.data,
    disciplinasQuery.data,
    estadoCompetenciasQueries,
    torneoQuery.data?.estado,
  ])
  const hayDisciplinasEnCurso = useMemo(() => {
    if (torneoQuery.data?.estado !== 'EJECUCION') return false
    return estadoCompetenciasQueries.some((query) => query.data?.estado === 'EnEjecucion')
  }, [estadoCompetenciasQueries, torneoQuery.data?.estado])
  const isCancelado = torneoQuery.data?.estado === 'CANCELADO'

  return (
    <OrganizadorLayout
      title={torneoQuery.data?.nombre ?? 'Torneo'}
      activeTournamentId={torneoId}
      subtitle="Gestión del torneo activo"
      actions={
        <>
          {torneoQuery.data?.estado === 'CREADO' ? (
            <Link
              to={`/organizador/torneos/${torneoId}/disciplinas`}
              className="rounded-full border border-amber-400 bg-amber-400/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-amber-300"
            >
              Editar disciplinas
            </Link>
          ) : null}
        </>
      }
    >
      {torneoQuery.isLoading ? (
        <section className="rounded-[2rem] border border-slate-700 bg-slate-900/70 p-5 text-sm text-slate-300">
          Cargando torneo...
        </section>
      ) : null}

      {torneoQuery.isError ? (
        <section className="rounded-[2rem] border border-red-500/40 bg-red-950/40 p-5 text-sm text-red-100">
          No se pudo cargar el torneo.
        </section>
      ) : null}

      {torneoQuery.data ? (
        <>
          {isCancelado ? (
            <section className="rounded-[2rem] border border-red-500/40 bg-red-950/40 p-5 shadow-[0_20px_60px_rgba(2,6,23,0.24)]">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <FaseBadge estado={torneoQuery.data.estado} />
                  <h2 className="mt-3 text-2xl font-semibold text-white">
                    {torneoQuery.data.nombre}
                  </h2>
                  <p className="mt-2 text-sm font-semibold text-red-100">
                    Torneo cancelado
                  </p>
                  <p className="mt-2 text-sm text-red-100/80">
                    El torneo quedo en estado terminal. La informacion operativa no se
                    muestra desde el flujo normal de gestion.
                  </p>
                </div>
              </div>

              <dl className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                <div className="rounded-[1.5rem] border border-red-500/40 bg-slate-950/40 p-4">
                  <dt className="text-xs font-semibold text-red-200">Fechas</dt>
                  <dd className="mt-1 text-sm text-white">
                    {torneoQuery.data.fecha_inicio} a {torneoQuery.data.fecha_fin}
                  </dd>
                </div>
                <div className="rounded-[1.5rem] border border-red-500/40 bg-slate-950/40 p-4">
                  <dt className="text-xs font-semibold text-red-200">Sede</dt>
                  <dd className="mt-1 text-sm text-white">
                    {torneoQuery.data.sede.nombre}, {torneoQuery.data.sede.ciudad},{' '}
                    {torneoQuery.data.sede.pais}
                  </dd>
                </div>
                <div className="rounded-[1.5rem] border border-red-500/40 bg-slate-950/40 p-4">
                  <dt className="text-xs font-semibold text-red-200">Entidad</dt>
                  <dd className="mt-1 text-sm text-white">
                    {torneoQuery.data.entidad_organizadora.nombre} ·{' '}
                    {torneoQuery.data.entidad_organizadora.tipo}
                  </dd>
                </div>
              </dl>
            </section>
          ) : (
            <TorneoOperativoPanel
              key={torneoQuery.data.estado}
              torneo={torneoQuery.data}
              disciplinas={disciplinasQuery.data ?? []}
              competencias={competenciasQuery.data ?? []}
              estadosCompetencia={estadoCompetenciasQueries.map((query) => query.data?.estado ?? null)}
              isLoadingDisciplinas={disciplinasQuery.isLoading || competenciasQuery.isLoading}
              premiacionPendientes={premiacionPendientes}
              isPremiacionStatusLoading={isPremiacionStatusLoading}
              hayDisciplinasEnCurso={hayDisciplinasEnCurso}
              onTransitionSuccess={async () => {
                setTransitionError('')
                await torneoQuery.refetch()
                await disciplinasQuery.refetch()
                await competenciasQuery.refetch()
              }}
              onTransitionError={setTransitionError}
            />
          )}

          {!isCancelado && transitionError ? (
            <section className="rounded-[1.5rem] border border-red-500/40 bg-red-950/40 p-4 text-sm text-red-100">
              {transitionError}
            </section>
          ) : null}

          {!isCancelado ? (
            <AccionesPanel
              torneoId={torneoQuery.data.torneo_id}
              torneoNombre={torneoQuery.data.nombre}
              estado={torneoQuery.data.estado}
              premiacionPendientes={premiacionPendientes}
              isPremiacionStatusLoading={isPremiacionStatusLoading}
              onSuccess={async () => {
                setTransitionError('')
                await torneoQuery.refetch()
                await disciplinasQuery.refetch()
                await competenciasQuery.refetch()
              }}
              onError={setTransitionError}
              showPhaseActions={false}
            />
          ) : null}
        </>
      ) : null}
    </OrganizadorLayout>
  )
}

interface TorneoOperativoPanelProps {
  torneo: TorneoDto
  disciplinas: Array<{
    disciplina: string
    juez_id: string | null
  }>
  competencias: Array<{
    competencia_id: string
    disciplina: string
    torneo_id: string
  }>
  estadosCompetencia: Array<string | null>
  isLoadingDisciplinas: boolean
  premiacionPendientes: string[] | null
  isPremiacionStatusLoading: boolean
  hayDisciplinasEnCurso: boolean
  onTransitionSuccess: () => Promise<void>
  onTransitionError: (message: string) => void
}

function TorneoOperativoPanel({
  torneo,
  disciplinas,
  competencias,
  estadosCompetencia,
  isLoadingDisciplinas,
  premiacionPendientes,
  isPremiacionStatusLoading,
  hayDisciplinasEnCurso,
  onTransitionSuccess,
  onTransitionError,
}: TorneoOperativoPanelProps) {
  const [selectedEstado, setSelectedEstado] = useState<EstadoTorneo>(torneo.estado)
  const [isSavingState, setIsSavingState] = useState(false)
  const estadosPorDisciplina = new Map(
    competencias.map((competencia, index) => [competencia.disciplina, estadosCompetencia[index] ?? null]),
  )
  const transitionOptions = buildEstadoOptions(
    torneo.estado,
    premiacionPendientes,
    isPremiacionStatusLoading,
    hayDisciplinasEnCurso,
  )
  const selectedTransition = transitionOptions.find((option) => option.value === selectedEstado) ?? null

  async function handleSaveEstado() {
    if (!selectedTransition || selectedTransition.value === torneo.estado) return
    const transition = (TRANSICIONES_ESTADO[torneo.estado] ?? []).find(
      (item) => item.target === selectedTransition.value,
    )
    if (!transition) return

    setIsSavingState(true)
    onTransitionError('')
    try {
      await transition.run(torneo.torneo_id)
      await onTransitionSuccess()
    } catch (error) {
      onTransitionError(error instanceof Error ? error.message : 'No se pudo cambiar el estado del torneo')
    } finally {
      setIsSavingState(false)
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
      <section>
        <p className="mb-3 text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
          Datos generales
        </p>
        <div className="rounded-[1.75rem] border border-slate-700 bg-slate-900/85 p-5 shadow-[0_20px_60px_rgba(2,6,23,0.24)]">
          <div className="space-y-4">
            <FieldShell label="Nombre del torneo" value={torneo.nombre} />
            <FieldShell label="Fecha" value={torneo.fecha_inicio} />
            <FieldShell label="Sede" value={torneo.sede.nombre} />
            <FieldShell label="Estado">
              <select
                value={selectedEstado}
                onChange={(event) => setSelectedEstado(event.target.value as EstadoTorneo)}
                disabled={transitionOptions.length <= 1 || isSavingState}
                className="min-h-11 w-full rounded-xl border border-slate-700 bg-slate-950/70 px-4 text-sm text-white outline-none"
              >
                {transitionOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </FieldShell>
          </div>

          <div className="mt-4 rounded-[1.25rem] border border-slate-700 bg-slate-950/40 p-4 text-sm text-slate-300">
            {torneo.sede.ciudad}, {torneo.sede.pais} · {torneo.entidad_organizadora.nombre} ·{' '}
            {torneo.entidad_organizadora.tipo}
          </div>

          {torneo.estado === 'EJECUCION' && isPremiacionStatusLoading ? (
            <p className="mt-4 text-sm font-semibold text-slate-300">
              Verificando cierre de disciplinas antes de pasar a premiación...
            </p>
          ) : null}

          {torneo.estado === 'EJECUCION' && premiacionPendientes && premiacionPendientes.length > 0 ? (
            <p className="mt-4 text-sm font-semibold text-amber-300">
              Falta cerrar {premiacionPendientes.length}{' '}
              {premiacionPendientes.length === 1 ? 'disciplina' : 'disciplinas'}:{' '}
              {premiacionPendientes.join(', ')}.
            </p>
          ) : null}

          <button
            type="button"
            onClick={() => void handleSaveEstado()}
            disabled={
              isSavingState ||
              !selectedTransition ||
              selectedTransition.value === torneo.estado
            }
            className="mt-4 rounded-xl bg-sky-500 px-4 py-3 text-sm font-semibold text-slate-950 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isSavingState ? 'Guardando...' : 'Guardar cambios'}
          </button>
        </div>
      </section>

      <section>
        <p className="mb-3 text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
          Disciplinas
        </p>
        <div className="space-y-3">
          {isLoadingDisciplinas ? (
            <section className="rounded-[1.75rem] border border-slate-700 bg-slate-900/70 p-5 text-sm text-slate-300">
              Cargando disciplinas...
            </section>
          ) : disciplinas.length === 0 ? (
            <section className="rounded-[1.75rem] border border-slate-700 bg-slate-900/70 p-5 text-sm text-slate-300">
              Este torneo no tiene disciplinas configuradas.
            </section>
          ) : (
            disciplinas.map((disciplina) => (
              <DisciplinaCard
                key={disciplina.disciplina}
                disciplina={disciplina.disciplina}
                estado={estadosPorDisciplina.get(disciplina.disciplina)}
                hasCompetencia={competencias.some((item) => item.disciplina === disciplina.disciplina)}
                hasJuez={Boolean(disciplina.juez_id)}
              />
            ))
          )}
        </div>
      </section>
    </div>
  )
}

function buildEstadoOptions(
  estadoActual: EstadoTorneo,
  premiacionPendientes: string[] | null,
  isPremiacionStatusLoading: boolean,
  _hayDisciplinasEnCurso: boolean,
): EstadoOption[] {
  const options: EstadoOption[] = [
    { value: estadoActual, label: ESTADO_LABELS[estadoActual] },
  ]

  for (const transition of TRANSICIONES_ESTADO[estadoActual] ?? []) {
    if (
      transition.target === 'PREMIACION' &&
      (isPremiacionStatusLoading || (premiacionPendientes?.length ?? 0) > 0)
    ) {
      continue
    }
    options.push({
      value: transition.target,
      label: ESTADO_LABELS[transition.target],
    })
  }

  return options
}

function FieldShell({
  label,
  value,
  children,
}: {
  label: string
  value?: string
  children?: React.ReactNode
}) {
  return (
    <div>
      <label className="mb-2 block text-sm font-medium text-slate-200">{label}</label>
      {children ?? (
        <div className="flex min-h-11 items-center rounded-xl border border-slate-700 bg-slate-950/70 px-4 text-sm text-white">
          {value}
        </div>
      )}
    </div>
  )
}

function DisciplinaCard({
  disciplina,
  estado,
  hasCompetencia,
  hasJuez,
}: {
  disciplina: string
  estado: string | null | undefined
  hasCompetencia: boolean
  hasJuez: boolean
}) {
  const { label, className } = disciplinaStatus(estado, hasCompetencia)

  return (
    <article className="rounded-[1.5rem] border border-slate-700 bg-slate-900/85 p-5 shadow-[0_20px_60px_rgba(2,6,23,0.2)]">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-white">{disciplina}</h3>
          <p className="mt-1 text-sm text-slate-300">
            {hasCompetencia ? 'Competencia generada' : 'Competencia pendiente'} ·{' '}
            {hasJuez ? 'Juez asignado' : 'Sin juez asignado'}
          </p>
        </div>
        <span className={`rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em] ${className}`}>
          {label}
        </span>
      </div>
    </article>
  )
}

function disciplinaStatus(
  estado: string | null | undefined,
  hasCompetencia: boolean,
): { label: string; className: string } {
  if (!hasCompetencia) {
    return {
      label: 'Pendiente',
      className: 'bg-slate-700 text-slate-300',
    }
  }

  if (estado === 'EnEjecucion') {
    return {
      label: 'Activa',
      className: 'bg-emerald-500/15 text-emerald-300',
    }
  }

  if (estado === 'Finalizada') {
    return {
      label: 'Cerrada',
      className: 'bg-sky-500/15 text-sky-300',
    }
  }

  return {
    label: 'Pendiente',
    className: 'bg-slate-700 text-slate-300',
  }
}
