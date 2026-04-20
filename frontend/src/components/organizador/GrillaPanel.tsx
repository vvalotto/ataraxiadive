import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import {
  ajustarGrilla,
  confirmarGrilla,
  crearCompetencia,
  fetchCompetenciasPorTorneo,
  fetchEstadoCompetencia,
  fetchGrillaCompetencia,
  generarGrilla,
  type CambioGrillaPayload,
  type GrillaAtletaDto,
} from '../../api/competencia'
import { ConfigurarGrillaForm } from './ConfigurarGrillaForm'
import { TablaGrilla } from './TablaGrilla'

interface GrillaPanelProps {
  torneoId: string
}

const DISCIPLINAS = ['STA', 'DNF', 'DYN', 'DBF', 'SPE_2X50', 'SPE_4X50', 'SPE_8X50', 'SPE_16X50']

function buildOtIso(time: string) {
  const [hours, minutes] = time.split(':').map(Number)
  const date = new Date()
  date.setHours(hours, minutes, 0, 0)
  return date.toISOString()
}

export function GrillaPanel({ torneoId }: GrillaPanelProps) {
  const queryClient = useQueryClient()
  const [disciplina, setDisciplina] = useState('DNF')
  const [localRows, setLocalRows] = useState<GrillaAtletaDto[] | null>(null)
  const [error, setError] = useState('')

  const competenciasQuery = useQuery({
    queryKey: ['competencias-torneo', torneoId],
    queryFn: () => fetchCompetenciasPorTorneo(torneoId),
  })

  const competencia = useMemo(
    () => competenciasQuery.data?.find((item) => item.disciplina === disciplina) ?? null,
    [competenciasQuery.data, disciplina],
  )

  const estadoQuery = useQuery({
    queryKey: ['competencia-estado', competencia?.competencia_id, disciplina],
    queryFn: () => fetchEstadoCompetencia(competencia?.competencia_id ?? '', disciplina),
    enabled: Boolean(competencia),
  })

  const grillaQuery = useQuery({
    queryKey: ['competencia-grilla', competencia?.competencia_id, disciplina],
    queryFn: () => fetchGrillaCompetencia(competencia?.competencia_id ?? '', disciplina),
    enabled: Boolean(competencia),
  })

  const rows = localRows ?? grillaQuery.data ?? []
  const readOnly = estadoQuery.data?.grilla_confirmada || estadoQuery.data?.estado === 'GrillaConfirmada'
  const canConfirm = Boolean(competencia && rows.length > 0 && !readOnly)

  async function refresh() {
    setLocalRows(null)
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['competencias-torneo', torneoId] }),
      queryClient.invalidateQueries({ queryKey: ['competencia-estado'] }),
      queryClient.invalidateQueries({ queryKey: ['competencia-grilla'] }),
    ])
  }

  const generarMutation = useMutation({
    mutationFn: async (payload: { intervaloMinutos: number; primerOt: string }) => {
      const competenciaId = crypto.randomUUID()
      await crearCompetencia({
        competenciaId,
        disciplina,
        intervaloMinutos: payload.intervaloMinutos,
        configuradoPor: 'organizador-ui',
        torneoId,
      })
      await generarGrilla({
        competenciaId,
        disciplina,
        otInicio: buildOtIso(payload.primerOt),
        andariveles: 1,
      })
    },
    onSuccess: refresh,
    onError: (mutationError) => setError((mutationError as Error).message),
  })

  const ajustarMutation = useMutation({
    mutationFn: async (payload: { rows: GrillaAtletaDto[]; cambios: CambioGrillaPayload[] }) => {
      if (!competencia) return
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

  const confirmarMutation = useMutation({
    mutationFn: async () => {
      if (!competencia) return
      await confirmarGrilla({ competenciaId: competencia.competencia_id, disciplina })
    },
    onSuccess: refresh,
    onError: (mutationError) => setError((mutationError as Error).message),
  })

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <label className="text-sm font-semibold text-stone-900">
          Disciplina
          <select
            value={disciplina}
            onChange={(event) => {
              setDisciplina(event.target.value)
              setLocalRows(null)
              setError('')
            }}
            className="ml-0 mt-2 min-h-10 rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm sm:ml-3 sm:mt-0"
          >
            {DISCIPLINAS.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </label>
        {estadoQuery.data ? (
          <span className="rounded-lg border border-stone-300 px-3 py-2 text-sm font-semibold text-stone-800">
            {estadoQuery.data.grilla_confirmada ? 'Grilla confirmada' : estadoQuery.data.estado}
          </span>
        ) : null}
      </div>

      {error ? (
        <div className="rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-900">
          {error}
        </div>
      ) : null}

      {competenciasQuery.isLoading ? (
        <div className="rounded-lg border border-stone-200 bg-stone-50 p-4 text-sm text-stone-600">
          Cargando competencias...
        </div>
      ) : null}

      {!competenciasQuery.isLoading && !competencia ? (
        <ConfigurarGrillaForm
          disciplina={disciplina}
          isSubmitting={generarMutation.isPending}
          onSubmit={(payload) => generarMutation.mutate(payload)}
        />
      ) : null}

      {competencia ? (
        <>
          <TablaGrilla
            rows={rows}
            readOnly={Boolean(readOnly)}
            isSaving={ajustarMutation.isPending}
            onReorder={(nextRows, cambios) => ajustarMutation.mutate({ rows: nextRows, cambios })}
          />
          <div className="flex justify-end">
            {!readOnly ? (
              <button
                type="button"
                disabled={!canConfirm || confirmarMutation.isPending}
                onClick={() => confirmarMutation.mutate()}
                className="min-h-10 rounded-lg bg-emerald-800 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-stone-300"
              >
                {confirmarMutation.isPending ? 'Confirmando...' : 'Confirmar grilla'}
              </button>
            ) : null}
          </div>
        </>
      ) : null}
    </div>
  )
}
