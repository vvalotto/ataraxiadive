import { useMutation, useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { fetchApAtleta, fetchCompetenciasPorTorneo, fetchGrillaCompetencia, registrarAP } from '../../api/competencia'
import { fetchAtletaMe } from '../../api/registro'
import { fetchTorneo } from '../../api/torneo'
import { AtletaShell } from '../../components/atleta/AtletaShell'
import { ApiError } from '../../api/competencia'
import { formatDisciplina, formatFecha, getUnidadEsperada, getUnidadLabel } from './portalData'

async function loadApContext(torneoId: string, disciplina: string) {
  const [torneo, competencias, atleta] = await Promise.all([
    fetchTorneo(torneoId),
    fetchCompetenciasPorTorneo(torneoId),
    fetchAtletaMe(),
  ])
  const competencia = competencias.find((item) => item.disciplina === disciplina) ?? null
  const grilla = competencia
    ? await fetchGrillaCompetencia(competencia.competencia_id, competencia.disciplina).catch(() => [])
    : []
  const athleteEntry = grilla.find((entry) => entry.atleta_id === atleta.atleta_id) ?? null

  let apActual: string | null = athleteEntry?.ap_declarado ?? null
  if (!apActual && competencia) {
    try {
      const apDto = await fetchApAtleta(competencia.competencia_id, atleta.atleta_id, disciplina)
      apActual = apDto.ap_declarado
    } catch {
      // sin AP previo
    }
  }

  return { torneo, competencia, athleteEntry, atletaId: atleta.atleta_id, apActual }
}

function getApError(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 409) return 'No se pudo guardar el AP en el estado actual de la disciplina.'
    return error.message
  }
  if (error instanceof Error) return error.message
  return 'No se pudo guardar el AP.'
}

export function AtletaDeclararAPPage() {
  const { torneoId, disciplina } = useParams<{ torneoId: string; disciplina: string }>()
  const navigate = useNavigate()
  const [valorAp, setValorAp] = useState('')
  const query = useQuery({
    queryKey: ['atleta-ap-context', torneoId, disciplina],
    queryFn: () => loadApContext(torneoId ?? '', disciplina ?? ''),
    enabled: Boolean(torneoId && disciplina),
  })

  const mutation = useMutation({
    mutationFn: async () => {
      const atletaId = query.data?.atletaId
      if (!query.data?.competencia || !atletaId || !disciplina) {
        throw new Error('La disciplina todavía no está preparada para anunciar AP.')
      }
      return registrarAP({
        competenciaId: query.data.competencia.competencia_id,
        participanteId: atletaId,
        disciplina,
        valorAp: valorApValue,
        unidad: getUnidadEsperada(disciplina),
      })
    },
    onSuccess: () => {
      navigate('/atleta/mis-inscripciones')
    },
  })

  const unidadEsperada = getUnidadEsperada(disciplina ?? '')
  const unidadLabel = getUnidadLabel(unidadEsperada)
  const currentAp = query.data?.apActual ?? ''
  const valorApValue = valorAp || currentAp

  return (
    <AtletaShell title="Declarar AP" subtitle="Cargá o corregí tu announced performance antes del cierre." showBack>
      {query.isLoading ? (
        <div className="rounded-3xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-300">
          Cargando contexto de AP...
        </div>
      ) : null}

      {query.isError ? (
        <div className="rounded-3xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-100">
          No se pudo cargar el contexto para declarar AP.
        </div>
      ) : null}

      {query.data ? (
        <div className="space-y-4">
          <section className="rounded-[1.75rem] border border-slate-800 bg-slate-900 p-4 text-sm text-slate-300">
            El AP es tu marca anunciada previa. Podés declararla o actualizarla mientras el período siga abierto.
          </section>

          <section className="rounded-[1.75rem] border border-slate-800 bg-slate-900 p-4">
            <p className="text-sm font-semibold text-white">{query.data.torneo.nombre}</p>
            <p className="mt-1 text-xs uppercase tracking-[0.18em] text-sky-300">
              {formatDisciplina(disciplina ?? '')}
            </p>
            <p className="mt-2 text-sm text-slate-400">
              Fecha del torneo: {formatFecha(query.data.torneo.fecha_inicio)}
            </p>
            <p className="mt-2 text-sm text-slate-400">
              Deadline visible: hasta el cierre del período de anuncios del torneo.
            </p>
          </section>

          <section className="rounded-[1.75rem] border border-slate-800 bg-slate-900 p-5">
            <label className="block text-sm text-slate-300">
              AP — {unidadEsperada === 'Segundos' ? 'Tiempo anunciado' : 'Distancia anunciada'} *
              <div className="mt-3 flex items-center gap-3 rounded-3xl border border-sky-500/40 bg-sky-500/10 px-4 py-4">
                <input
                  value={valorApValue}
                  onChange={(event) => setValorAp(event.target.value)}
                  inputMode="decimal"
                  placeholder="0"
                  className="w-full bg-transparent text-3xl font-semibold text-white outline-none"
                />
                <span className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-300">
                  {unidadLabel}
                </span>
              </div>
            </label>
            {currentAp ? (
              <p className="mt-3 text-sm text-slate-400">
                AP actual guardado: {currentAp} {getUnidadLabel(query.data.athleteEntry?.unidad ?? unidadEsperada)}
              </p>
            ) : null}
          </section>

          {!query.data.competencia ? (
            <div className="rounded-3xl border border-amber-400/30 bg-amber-400/10 p-4 text-sm text-amber-100">
              El organizador aún no configuró la competencia de esta disciplina. El AP estará disponible cuando la grilla sea publicada.
            </div>
          ) : null}

          {mutation.isError ? (
            <div className="rounded-3xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-100">
              {getApError(mutation.error)}
            </div>
          ) : null}

          <div className="flex gap-3">
            <button
              type="button"
              onClick={() => navigate('/atleta/mis-inscripciones')}
              className="flex-1 rounded-2xl border border-slate-700 px-4 py-3 text-sm font-semibold text-slate-200"
            >
              Cancelar
            </button>
            <button
              type="button"
              onClick={() => mutation.mutate()}
              disabled={mutation.isPending || !(parseFloat(valorApValue) > 0) || !query.data.competencia}
              className="flex-1 rounded-2xl bg-sky-500 px-4 py-3 text-sm font-semibold uppercase tracking-[0.16em] text-slate-950 disabled:opacity-60"
            >
              {mutation.isPending ? 'Guardando...' : 'Guardar AP'}
            </button>
          </div>
        </div>
      ) : null}
    </AtletaShell>
  )
}
