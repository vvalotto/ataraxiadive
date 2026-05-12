import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import {
  ajustarGrilla,
  crearCompetencia,
  confirmarGrilla,
  fetchCompetenciasPorTorneo,
  fetchEstadoCompetencia,
  fetchGrillaCompetencia,
  generarGrilla,
  type CambioGrillaPayload,
  type GrillaAtletaDto,
} from '../../api/competencia'
import {
  listarDisciplinasTorneo,
  type EstadoTorneo,
  type DisciplinaCodigo,
} from '../../api/torneo'
import { ConfigurarGrillaForm } from './ConfigurarGrillaForm'
import { EmptyStateCard } from './EmptyStateCard'
import { TablaGrilla } from './TablaGrilla'
import useAuthStore from '../../stores/useAuthStore'

interface GrillaPanelProps {
  torneoId: string
  torneoEstado?: EstadoTorneo
  fechaInicioTorneo?: string
  fechaFinTorneo?: string
}

const ESTADO_COMPETENCIA_LABELS: Record<string, string> = {
  Preparacion: 'Preparación',
  GrillaGenerada: 'Grilla generada',
  GrillaConfirmada: 'Grilla confirmada',
  Confirmada: 'Grilla confirmada',
  EnEjecucion: 'En ejecución',
  Finalizada: 'Finalizada',
  CompetenciaFinalizada: 'Competencia finalizada',
}

function buildOtInicio(fechaOt: string, primerOt: string): string {
  return `${fechaOt}T${primerOt}:00`
}

function formatEstadoCompetencia(estado: string, grillaConfirmada: boolean): string {
  if (grillaConfirmada) {
    return 'Grilla confirmada'
  }
  return ESTADO_COMPETENCIA_LABELS[estado] ?? estado
}

export function GrillaPanel({
  torneoId,
  torneoEstado,
  fechaInicioTorneo,
  fechaFinTorneo,
}: GrillaPanelProps) {
  const queryClient = useQueryClient()
  const organizadorId = useAuthStore((state) => state.userId)
  const [disciplinaSeleccionada, setDisciplinaSeleccionada] = useState<DisciplinaCodigo | ''>('')
  const [localRows, setLocalRows] = useState<GrillaAtletaDto[] | null>(null)
  const [error, setError] = useState('')

  const disciplinasQuery = useQuery({
    queryKey: ['torneo-disciplinas', torneoId],
    queryFn: () => listarDisciplinasTorneo(torneoId),
  })

  const disciplinas = useMemo(
    () => disciplinasQuery.data?.map((item) => item.disciplina) ?? [],
    [disciplinasQuery.data],
  )
  const disciplina =
    disciplinaSeleccionada && disciplinas.includes(disciplinaSeleccionada)
      ? disciplinaSeleccionada
      : disciplinas[0] ?? ''

  const competenciasQuery = useQuery({
    queryKey: ['competencias-torneo', torneoId],
    queryFn: () => fetchCompetenciasPorTorneo(torneoId),
  })

  const competencia = useMemo(
    () =>
      disciplina
        ? competenciasQuery.data?.find((item) => item.disciplina === disciplina) ?? null
        : null,
    [competenciasQuery.data, disciplina],
  )

  const estadoQuery = useQuery({
    queryKey: ['competencia-estado', competencia?.competencia_id, disciplina],
    queryFn: () => fetchEstadoCompetencia(competencia?.competencia_id ?? '', disciplina),
    enabled: Boolean(competencia && disciplina),
  })

  const grillaQuery = useQuery({
    queryKey: ['competencia-grilla', competencia?.competencia_id, disciplina],
    queryFn: () => fetchGrillaCompetencia(competencia?.competencia_id ?? '', disciplina),
    enabled: Boolean(competencia && disciplina),
  })

  const rows = localRows ?? grillaQuery.data ?? []
  const readOnly = estadoQuery.data?.grilla_confirmada || estadoQuery.data?.estado === 'GrillaConfirmada'
  const puedeOperarGrilla = torneoEstado === 'PREPARACION'
  const necesitaCrearCompetencia = Boolean(!competencia && disciplina && puedeOperarGrilla)
  const puedeGenerar = Boolean(competencia && disciplina && puedeOperarGrilla && rows.length === 0)
  const puedeRegenerar = Boolean(competencia && disciplina && puedeOperarGrilla && rows.length > 0 && !readOnly)
  const canConfirm = Boolean(competencia && rows.length > 0 && !readOnly)

  async function refresh() {
    setLocalRows(null)
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['competencias-torneo', torneoId] }),
      queryClient.invalidateQueries({ queryKey: ['competencia-estado'] }),
      queryClient.invalidateQueries({ queryKey: ['competencia-grilla'] }),
    ])
  }

  const ajustarMutation = useMutation({
    mutationFn: async (payload: { rows: GrillaAtletaDto[]; cambios: CambioGrillaPayload[] }) => {
      if (!competencia || !disciplina) return
      setLocalRows(payload.rows)
      await ajustarGrilla({
        competenciaId: competencia.competencia_id,
        disciplina,
        cambios: payload.cambios,
      })
    },
    onSuccess: refresh,
    onError: (mutationError) => setError((mutationError as Error).message),
  })

  const generarMutation = useMutation({
    mutationFn: async (payload: { otInicio: string; andariveles: number }) => {
      if (!competencia || !disciplina) return
      setError('')
      await generarGrilla({
        competenciaId: competencia.competencia_id,
        disciplina,
        otInicio: payload.otInicio,
        andariveles: payload.andariveles,
      })
    },
    onSuccess: refresh,
    onError: (mutationError) => setError((mutationError as Error).message),
  })

  const crearYGenerarMutation = useMutation({
    mutationFn: async (payload: {
      otInicio: string
      intervaloMinutos: number
      andariveles: number
    }) => {
      if (!disciplina || !organizadorId) {
        throw new Error('No se pudo identificar al organizador para crear la competencia.')
      }
      setError('')
      const competenciaId = crypto.randomUUID()
      await crearCompetencia({
        competenciaId,
        disciplina,
        intervaloMinutos: payload.intervaloMinutos,
        configuradoPor: organizadorId,
        torneoId,
      })
      await generarGrilla({
        competenciaId,
        disciplina,
        otInicio: payload.otInicio,
        andariveles: payload.andariveles,
      })
    },
    onSuccess: refresh,
    onError: (mutationError) => setError((mutationError as Error).message),
  })

  const regenerarConIntervaloMutation = useMutation({
    mutationFn: async (payload: {
      otInicio: string
      intervaloMinutos: number
      andariveles: number
    }) => {
      if (!competencia || !disciplina || !organizadorId) return
      setError('')
      await crearCompetencia({
        competenciaId: competencia.competencia_id,
        disciplina,
        intervaloMinutos: payload.intervaloMinutos,
        configuradoPor: organizadorId,
        torneoId,
      })
      await generarGrilla({
        competenciaId: competencia.competencia_id,
        disciplina,
        otInicio: payload.otInicio,
        andariveles: payload.andariveles,
      })
    },
    onSuccess: refresh,
    onError: (mutationError) => setError((mutationError as Error).message),
  })

  const confirmarMutation = useMutation({
    mutationFn: async () => {
      if (!competencia || !disciplina) return
      await confirmarGrilla({ competenciaId: competencia.competencia_id, disciplina })
    },
    onSuccess: refresh,
    onError: (mutationError) => setError((mutationError as Error).message),
  })

  return (
    <div className="space-y-4">
      {error ? (
        <section className="rounded-[2rem] border border-red-500/40 bg-red-950/40 p-5 text-sm text-red-100">
          {error}
        </section>
      ) : null}

      {disciplinasQuery.isLoading ? (
        <section className="rounded-[2rem] border border-slate-700 bg-slate-900/70 p-5 text-sm text-slate-300">
          Cargando disciplinas del torneo...
        </section>
      ) : null}

      {disciplinasQuery.isError ? (
        <section className="rounded-[2rem] border border-red-500/40 bg-red-950/40 p-5 text-sm text-red-100">
          No se pudieron cargar las disciplinas del torneo.
        </section>
      ) : null}

      {!disciplinasQuery.isLoading && !disciplinasQuery.isError && disciplinas.length === 0 ? (
        <section className="rounded-[2rem] border border-slate-700 bg-slate-900/70 p-5 text-sm text-slate-300">
          Este torneo no tiene disciplinas configuradas para generar grilla.
        </section>
      ) : null}

      {competenciasQuery.isLoading ? (
        <section className="rounded-[2rem] border border-slate-700 bg-slate-900/70 p-5 text-sm text-slate-300">
          Cargando competencias...
        </section>
      ) : null}

      {!disciplinasQuery.isLoading &&
      !disciplinasQuery.isError &&
      disciplinas.length > 0 &&
      !competenciasQuery.isLoading &&
      !puedeOperarGrilla &&
      (competenciasQuery.data?.length ?? 0) === 0 ? (
        <EmptyStateCard message="La grilla se habilita al pasar el torneo a Preparación." />
      ) : null}

      {disciplina ? (
        <article className="rounded-[2rem] border border-slate-700 bg-slate-900/85 p-6 shadow-[0_20px_60px_rgba(2,6,23,0.24)]">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                Grilla operativa
              </p>
              <h2 className="mt-2 text-2xl font-semibold text-white">{disciplina}</h2>
              <p className="mt-2 text-sm text-slate-300">
                Reordena performances, revisa OT y confirma la grilla de la disciplina activa.
              </p>
              <p className="mt-2 text-xs uppercase tracking-[0.16em] text-sky-300">
                La grilla usa los AP declarados durante la inscripción.
              </p>
              {torneoEstado !== 'PREPARACION' ? (
                <p className="mt-2 text-sm text-amber-300">
                  La generación de grilla se habilita cuando el torneo pasa a Preparación.
                </p>
              ) : null}
            </div>
            <div className="flex flex-col gap-2 sm:items-end">
              <label className="text-sm font-semibold text-slate-200">
                Disciplina
                <select
                  value={disciplina}
                  onChange={(event) => {
                    setDisciplinaSeleccionada(event.target.value as DisciplinaCodigo)
                    setLocalRows(null)
                    setError('')
                  }}
                  disabled={disciplinasQuery.isLoading || disciplinas.length === 0}
                  className="mt-2 min-h-10 min-w-40 rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100"
                >
                  {disciplinas.map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
              </label>
              {estadoQuery.data ? (
                <span className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.16em] text-slate-200">
                  {formatEstadoCompetencia(
                    estadoQuery.data.estado,
                    estadoQuery.data.grilla_confirmada,
                  )}
                </span>
              ) : null}
            </div>
          </div>

          {puedeGenerar ? (
            <div className="mt-6 rounded-[1.5rem] border border-slate-700 bg-slate-950/70 p-4">
              <p className="mb-3 text-sm text-slate-300">
                El torneo está en Preparación. Define el primer OT para generar la grilla de salida.
              </p>
              <ConfigurarGrillaForm
                disciplina={disciplina}
                isSubmitting={generarMutation.isPending}
                fechaInicioTorneo={fechaInicioTorneo}
                fechaFinTorneo={fechaFinTorneo}
                onSubmit={({ fechaOt, primerOt, andariveles }) =>
                  generarMutation.mutate({
                    otInicio: buildOtInicio(fechaOt, primerOt),
                    andariveles,
                  })
                }
              />
            </div>
          ) : null}

          {puedeRegenerar ? (
            <div className="mt-6 rounded-[1.5rem] border border-amber-500/30 bg-amber-500/5 p-4">
              <p className="mb-3 text-sm text-slate-300">
                Puedes volver a generar la grilla antes de confirmarla para cambiar intervalo OT, fecha, primer OT y cantidad de andariveles.
              </p>
              <ConfigurarGrillaForm
                disciplina={disciplina}
                requiresIntervalo
                isSubmitting={regenerarConIntervaloMutation.isPending}
                fechaInicioTorneo={fechaInicioTorneo}
                fechaFinTorneo={fechaFinTorneo}
                submitLabel="Regenerar grilla"
                submittingLabel="Regenerando..."
                onSubmit={({ fechaOt, primerOt, intervaloMinutos, andariveles }) =>
                  regenerarConIntervaloMutation.mutate({
                    otInicio: buildOtInicio(fechaOt, primerOt),
                    intervaloMinutos: intervaloMinutos ?? 1,
                    andariveles,
                  })
                }
              />
            </div>
          ) : null}

          {necesitaCrearCompetencia ? (
            <div className="mt-6 rounded-[1.5rem] border border-slate-700 bg-slate-950/70 p-4">
              <p className="mb-3 text-sm text-slate-300">
                Esta disciplina todavía no tiene competencia creada. Configura el intervalo OT y genera la grilla de salida.
              </p>
              <ConfigurarGrillaForm
                disciplina={disciplina}
                requiresIntervalo
                isSubmitting={crearYGenerarMutation.isPending}
                fechaInicioTorneo={fechaInicioTorneo}
                fechaFinTorneo={fechaFinTorneo}
                onSubmit={({ fechaOt, primerOt, intervaloMinutos, andariveles }) =>
                  crearYGenerarMutation.mutate({
                    otInicio: buildOtInicio(fechaOt, primerOt),
                    intervaloMinutos: intervaloMinutos ?? 1,
                    andariveles,
                  })
                }
              />
            </div>
          ) : null}

          {competencia ? (
            <div className="mt-6 rounded-[1.5rem] border border-slate-700 bg-slate-950/70 p-4">
              <TablaGrilla
                rows={rows}
                readOnly={Boolean(readOnly) || !puedeOperarGrilla}
                isSaving={ajustarMutation.isPending}
                onReorder={(nextRows, cambios) => ajustarMutation.mutate({ rows: nextRows, cambios })}
              />
            </div>
          ) : null}

          {!readOnly && puedeOperarGrilla && competencia ? (
            <div className="mt-6 flex justify-end">
              <button
                type="button"
                disabled={!canConfirm || confirmarMutation.isPending}
                onClick={() => confirmarMutation.mutate()}
                className="min-h-10 rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
              >
                {confirmarMutation.isPending ? 'Confirmando...' : 'Confirmar grilla'}
              </button>
            </div>
          ) : null}
        </article>
      ) : null}
    </div>
  )
}
