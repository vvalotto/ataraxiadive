import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
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

  const disciplinas = disciplinasQuery.data ?? []
  const jueces = useMemo(
    () => (juecesQuery.data ?? []).filter((usuario) => usuario.rol === 'JUEZ' && usuario.activo),
    [juecesQuery.data],
  )
  const todasAsignadas =
    disciplinas.length > 0 && disciplinas.every((disciplina) => Boolean(disciplina.juez_id))

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

  if (disciplinasQuery.isLoading || juecesQuery.isLoading) {
    return (
      <div className="rounded-lg border border-stone-200 bg-stone-50 p-4 text-sm text-stone-600">
        Cargando jueces...
      </div>
    )
  }

  if (disciplinasQuery.isError || juecesQuery.isError) {
    return (
      <div className="rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-900">
        No se pudieron cargar disciplinas o jueces.
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

      <TablaJueces
        disciplinas={disciplinas}
        jueces={jueces}
        savingDisciplina={savingDisciplina}
        onAsignar={(disciplina, juezId) => asignarMutation.mutate({ disciplina, juezId })}
      />
    </div>
  )
}
