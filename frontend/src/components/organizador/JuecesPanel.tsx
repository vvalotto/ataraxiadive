import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import {
  fetchCompetenciasPorTorneo,
  fetchEstadoCompetencia,
  type CompetenciaResumenDto,
  type EstadoCompetenciaDto,
} from '../../api/competencia'
import { listarUsuariosPorRol } from '../../api/identidad'
import {
  asignarJuez,
  listarDisciplinasTorneo,
  type DisciplinaTorneoDto,
} from '../../api/torneo'
import { EmptyStateCard } from './EmptyStateCard'
import { TablaJueces } from './TablaJueces'

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

function tieneGrillaGenerada(estado: EstadoCompetenciaDto): boolean {
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
  const [savingDisciplina, setSavingDisciplina] = useState<string | null>(null)

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

  const disciplinas = disciplinasQuery.data ?? []
  const jueces = useMemo(
    () => (juecesQuery.data ?? []).filter((usuario) => usuario.rol === 'JUEZ' && usuario.activo),
    [juecesQuery.data],
  )
  const asignablePorDisciplina = useMemo(() => {
    const asignable = new Map<string, boolean>()

    for (const item of competenciasQuery.data ?? []) {
      asignable.set(item.competencia.disciplina, tieneGrillaGenerada(item.estado))
    }

    return asignable
  }, [competenciasQuery.data])
  const todasAsignadas =
    disciplinas.length > 0 && disciplinas.every((disciplina) => Boolean(disciplina.juez_id))
  const sinJuecesAsignados =
    disciplinas.length > 0 && disciplinas.every((disciplina) => !disciplina.juez_id)
  const hayCompetenciasOperativas = (competenciasQuery.data?.length ?? 0) > 0

  const asignarMutation = useMutation({
    mutationFn: async (payload: { disciplina: DisciplinaTorneoDto; juezId: string }) => {
      setSavingDisciplina(payload.disciplina.disciplina)
      await asignarJuez({
        torneoId,
        disciplina: payload.disciplina.disciplina,
        juezId: payload.juezId,
      })
    },
    onSuccess: async () => {
      setError('')
      await queryClient.invalidateQueries({ queryKey: ['torneo-disciplinas', torneoId] })
    },
    onError: (mutationError) => {
      setError((mutationError as Error).message)
    },
    onSettled: () => setSavingDisciplina(null),
  })

  if (disciplinasQuery.isLoading || juecesQuery.isLoading || competenciasQuery.isLoading) {
    return (
      <section className="rounded-[2rem] border border-slate-700 bg-slate-900/70 p-5 text-sm text-slate-300">
        Cargando jueces...
      </section>
    )
  }

  if (disciplinasQuery.isError || juecesQuery.isError || competenciasQuery.isError) {
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
              Asignación por disciplina
            </p>
            <h2 className="mt-2 text-2xl font-semibold text-white">Jueces del torneo</h2>
            <p className="mt-2 text-sm text-slate-300">
              Vincula cada disciplina operativa con un juez habilitado antes de iniciar la ejecución.
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
              {disciplinas.length}
            </p>
            <p className="mt-2 text-sm text-slate-300">
              disciplinas · {jueces.length} jueces disponibles
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
              La tabla inferior se habilita por disciplina cuando la competencia ya tiene grilla disponible.
            </p>
          </div>
        </div>

        <div className="mt-6 rounded-[1.5rem] border border-slate-700 bg-slate-950/70 p-4">
          <TablaJueces
            disciplinas={disciplinas}
            jueces={jueces}
            savingDisciplina={savingDisciplina}
            asignablePorDisciplina={asignablePorDisciplina}
            onAsignar={(disciplina, juezId) => asignarMutation.mutate({ disciplina, juezId })}
          />
        </div>
      </article>
    </div>
  )
}
