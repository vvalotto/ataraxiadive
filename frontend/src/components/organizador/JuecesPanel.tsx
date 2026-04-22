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
      <div className="rounded-lg border border-stone-200 bg-stone-50 p-4 text-sm text-stone-600">
        Cargando jueces...
      </div>
    )
  }

  if (disciplinasQuery.isError || juecesQuery.isError || competenciasQuery.isError) {
    return (
      <div className="rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-900">
        No se pudieron cargar los jueces.
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-stone-600">
          {disciplinas.length} disciplinas · {jueces.length} jueces disponibles
        </p>
        <span
          className={[
            'rounded-lg border px-3 py-2 text-sm font-semibold',
            todasAsignadas
              ? 'border-emerald-700 bg-emerald-50 text-emerald-900'
              : 'border-stone-300 bg-white text-stone-700',
          ].join(' ')}
        >
          {todasAsignadas ? 'Asignacion completa' : 'Asignacion pendiente'}
        </span>
      </div>

      {error ? (
        <div className="rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-900">
          {error}
        </div>
      ) : null}

      {sinJuecesAsignados ? (
        <div className="rounded-lg border border-stone-200 bg-stone-50 p-4 text-sm text-stone-600">
          Todavia no hay jueces asignados
        </div>
      ) : null}

      <TablaJueces
        disciplinas={disciplinas}
        jueces={jueces}
        savingDisciplina={savingDisciplina}
        asignablePorDisciplina={asignablePorDisciplina}
        onAsignar={(disciplina, juezId) => asignarMutation.mutate({ disciplina, juezId })}
      />
    </div>
  )
}
