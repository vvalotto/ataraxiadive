import { useMutation, useQueries, useQuery, useQueryClient } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import {
  asignarJuezPerformance,
  fetchCompetenciasPorTorneo,
  fetchEstadoCompetencia,
  fetchGrillaCompetencia,
  type CompetenciaResumenDto,
  type EstadoCompetenciaDto,
} from '../../api/competencia'
import { listarUsuariosPorRol } from '../../api/identidad'
import {
  listarDisciplinasTorneo,
} from '../../api/torneo'
import { EmptyStateCard } from './EmptyStateCard'
import { TablaJueces, type FilaJuezPerformance } from './TablaJueces'

interface JuecesPanelProps {
  torneoId: string
}

interface CompetenciaConEstado {
  competencia: CompetenciaResumenDto
  estado: EstadoCompetenciaDto
}

const ESTADOS_CON_GRILLA_GENERADA = new Set([
  'GrillaGenerada',
  'GrillaConfirmada',
  'EnEjecucion',
  'Finalizada',
  'CompetenciaFinalizada',
])

function tieneGrillaGenerada(estado: EstadoCompetenciaDto | null | undefined): boolean {
  if (!estado) return false
  return estado.grilla_confirmada || ESTADOS_CON_GRILLA_GENERADA.has(estado.estado)
}

async function fetchCompetenciasConEstado(torneoId: string): Promise<CompetenciaConEstado[]> {
  const competencias = await fetchCompetenciasPorTorneo(torneoId)
  return Promise.all(
    competencias.map(async (competencia) => ({
      competencia,
      estado: await fetchEstadoCompetencia(competencia.competencia_id, competencia.disciplina),
    })),
  )
}

export function JuecesPanel({ torneoId }: JuecesPanelProps) {
  const queryClient = useQueryClient()
  const [error, setError] = useState('')
  const [savingKey, setSavingKey] = useState<string | null>(null)
  const [selectedDisciplina, setSelectedDisciplina] = useState<string | null>(null)

  const disciplinasQuery = useQuery({
    queryKey: ['torneo-disciplinas', torneoId],
    queryFn: () => listarDisciplinasTorneo(torneoId),
  })

  const juecesQuery = useQuery({
    queryKey: ['usuarios-rol', 'JUEZ'],
    queryFn: () => listarUsuariosPorRol('JUEZ'),
  })
  const competenciasQuery = useQuery({
    queryKey: ['competencias-estado-jueces', torneoId],
    queryFn: () => fetchCompetenciasConEstado(torneoId),
  })
  const grillaQueries = useQueries({
    queries:
      (competenciasQuery.data ?? []).map((item) => ({
        queryKey: ['grilla-jueces', item.competencia.competencia_id, item.competencia.disciplina],
        queryFn: () =>
          fetchGrillaCompetencia(item.competencia.competencia_id, item.competencia.disciplina),
        enabled: tieneGrillaGenerada(item.estado),
      })) ?? [],
  })

  const disciplinas = disciplinasQuery.data ?? []
  const jueces = useMemo(
    () => (juecesQuery.data ?? []).filter((usuario) => usuario.rol === 'JUEZ' && usuario.activo),
    [juecesQuery.data],
  )
  const rows = useMemo<FilaJuezPerformance[]>(() => {
    return (competenciasQuery.data ?? []).flatMap((item, index) => {
      const grilla = grillaQueries[index]?.data ?? []
      return grilla.map((row) => ({
        competenciaId: item.competencia.competencia_id,
        disciplina: item.competencia.disciplina,
        performanceId: row.performance_id,
        atletaId: row.atleta_id,
        nombreAtleta: row.nombre_atleta,
        posicion: row.posicion,
        andarivel: row.andarivel,
        otProgramado: row.ot_programado,
        apDeclarado: row.ap_declarado,
        unidad: row.unidad,
        juezId: row.juez_id,
      }))
    })
  }, [competenciasQuery.data, grillaQueries])
  const disciplinasDisponibles = useMemo(
    () => Array.from(new Set(rows.map((row) => row.disciplina))),
    [rows],
  )
  const disciplinaActiva =
    selectedDisciplina && disciplinasDisponibles.includes(selectedDisciplina)
      ? selectedDisciplina
      : disciplinasDisponibles[0] ?? null
  const rowsDisciplinaActiva = useMemo(
    () => rows.filter((row) => row.disciplina === disciplinaActiva),
    [disciplinaActiva, rows],
  )
  const disciplinasConGrilla = useMemo(
    () =>
      (competenciasQuery.data ?? []).filter((item) => tieneGrillaGenerada(item.estado)).length,
    [competenciasQuery.data],
  )
  const totalPerformances = rows.length
  const performancesAsignadas = rows.filter((row) => row.juezId).length
  const todasAsignadas =
    disciplinas.length > 0 &&
    disciplinasConGrilla === disciplinas.length &&
    totalPerformances > 0 &&
    performancesAsignadas === totalPerformances
  const sinJuecesAsignados = totalPerformances > 0 && performancesAsignadas === 0
  const hayCompetenciasOperativas = (competenciasQuery.data?.length ?? 0) > 0
  const disciplinasPendientesDeGrilla = useMemo(() => {
    const competenciasPorDisciplina = new Map(
      (competenciasQuery.data ?? []).map((item) => [item.competencia.disciplina, item.estado]),
    )
    return disciplinas
      .filter((disciplina) =>
        !tieneGrillaGenerada(competenciasPorDisciplina.get(disciplina.disciplina)),
      )
      .map((disciplina) => disciplina.disciplina)
  }, [competenciasQuery.data, disciplinas])

  const asignarMutation = useMutation({
    mutationFn: async (payload: { row: FilaJuezPerformance; juezId: string }) => {
      setSavingKey(`${payload.row.competenciaId}:${payload.row.performanceId}`)
      await asignarJuezPerformance({
        competenciaId: payload.row.competenciaId,
        performanceId: payload.row.performanceId,
        disciplina: payload.row.disciplina,
        juezId: payload.juezId,
      })
    },
    onSuccess: async () => {
      setError('')
      await queryClient.invalidateQueries({ queryKey: ['grilla-jueces'] })
      await queryClient.invalidateQueries({ queryKey: ['ejecucion-disciplinas', torneoId] })
    },
    onError: (mutationError) => {
      setError((mutationError as Error).message)
    },
    onSettled: () => setSavingKey(null),
  })

  if (
    disciplinasQuery.isLoading ||
    juecesQuery.isLoading ||
    competenciasQuery.isLoading ||
    grillaQueries.some((query) => query.isLoading)
  ) {
    return (
      <section className="rounded-[2rem] border border-slate-700 bg-slate-900/70 p-5 text-sm text-slate-300">
        Cargando jueces...
      </section>
    )
  }

  if (
    disciplinasQuery.isError ||
    juecesQuery.isError ||
    competenciasQuery.isError ||
    grillaQueries.some((query) => query.isError)
  ) {
    return (
      <section className="rounded-[2rem] border border-red-500/40 bg-red-950/40 p-5 text-sm text-red-100">
        No se pudieron cargar los jueces.
      </section>
    )
  }

  if (disciplinas.length > 0 && !hayCompetenciasOperativas) {
    return <EmptyStateCard message="Este torneo todavía no tiene competencias operativas." />
  }

  return (
    <div className="space-y-4">
      {error ? (
        <section className="rounded-[2rem] border border-red-500/40 bg-red-950/40 p-5 text-sm text-red-100">
          {error}
        </section>
      ) : null}

      <article className="rounded-[2rem] border border-slate-700 bg-slate-900/85 p-6 shadow-[0_20px_60px_rgba(2,6,23,0.24)]">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
              Asignación por performance
            </p>
            <h2 className="mt-2 text-2xl font-semibold text-white">Jueces del torneo</h2>
            <p className="mt-2 text-sm text-slate-300">
              Asigna un juez a cada atleta de la grilla antes de iniciar la ejecución del torneo.
            </p>
          </div>
          <span
            className={[
              'rounded-full border px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.16em]',
              todasAsignadas
                ? 'border-emerald-500/40 bg-emerald-950/40 text-emerald-200'
                : 'border-slate-700 bg-slate-950 text-slate-300',
            ].join(' ')}
          >
            {todasAsignadas ? 'Asignación completa' : 'Asignación pendiente'}
          </span>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <div className="rounded-[1.5rem] border border-slate-700 bg-slate-950/70 p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
              Cobertura operativa
            </p>
            <p className="mt-3 text-3xl font-semibold tracking-tight text-white">
              {performancesAsignadas}/{totalPerformances || 0}
            </p>
            <p className="mt-2 text-sm text-slate-300">
              performances con juez · {jueces.length} jueces disponibles
            </p>
          </div>

          <div className="rounded-[1.5rem] border border-slate-700 bg-slate-950/70 p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
              Estado de asignación
            </p>
            <p className="mt-3 text-lg font-semibold text-white">
              {sinJuecesAsignados ? 'Todavía no hay jueces asignados' : 'Asignaciones en curso'}
            </p>
            <p className="mt-2 text-sm text-slate-300">
              La asignación se hace por performance una vez que la disciplina ya tiene grilla confirmada.
            </p>
          </div>
        </div>

        {disciplinasPendientesDeGrilla.length > 0 ? (
          <div className="mt-6 rounded-[1.5rem] border border-amber-500/30 bg-amber-500/5 p-4 text-sm text-amber-100">
            Falta confirmar la grilla en: {disciplinasPendientesDeGrilla.join(', ')}.
          </div>
        ) : null}

        {disciplinasDisponibles.length > 1 ? (
          <div className="mt-6 flex flex-wrap gap-2">
            {disciplinasDisponibles.map((disciplina) => (
              <button
                key={disciplina}
                type="button"
                onClick={() => setSelectedDisciplina(disciplina)}
                className={[
                  'rounded-full border px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] transition',
                  disciplina === disciplinaActiva
                    ? 'border-sky-400 bg-sky-400/10 text-sky-300'
                    : 'border-slate-700 bg-slate-950 text-slate-300 hover:border-slate-500',
                ].join(' ')}
              >
                {disciplina}
              </button>
            ))}
          </div>
        ) : null}

        <div className="mt-6 rounded-[1.5rem] border border-slate-700 bg-slate-950/70 p-4">
          <TablaJueces
            rows={rowsDisciplinaActiva}
            jueces={jueces}
            savingKey={savingKey}
            disciplina={disciplinaActiva}
            onAsignar={(row, juezId) => asignarMutation.mutate({ row, juezId })}
          />
        </div>
      </article>
    </div>
  )
}
