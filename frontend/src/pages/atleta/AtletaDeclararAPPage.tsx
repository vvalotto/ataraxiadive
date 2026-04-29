import { useMutation, useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { fetchCompetenciasPorTorneo, fetchGrillaCompetencia } from '../../api/competencia'
import { fetchApInscripcion, fetchAtletaMe, guardarApInscripcion, listarInscripcionesDeAtleta } from '../../api/registro'
import { fetchTorneo } from '../../api/torneo'
import { AtletaShell } from '../../components/atleta/AtletaShell'
import { ApiError } from '../../api/registro'
import { esDisciplinaTiempo, formatAp, formatDisciplina, formatFecha, getUnidadEsperada, getUnidadLabel, isApInputValido, normalizeApInput } from './portalData'

async function loadApContext(torneoId: string, disciplina: string) {
  const [torneo, competencias, atleta] = await Promise.all([
    fetchTorneo(torneoId),
    fetchCompetenciasPorTorneo(torneoId),
    fetchAtletaMe(),
  ])
  const inscripciones = await listarInscripcionesDeAtleta(atleta.atleta_id)
  const inscripcion =
    inscripciones.find(
      (item) => item.torneo_id === torneoId && item.disciplinas.includes(disciplina),
    ) ?? null
  const competencia = competencias.find((item) => item.disciplina === disciplina) ?? null
  const grilla = competencia
    ? await fetchGrillaCompetencia(competencia.competencia_id, competencia.disciplina).catch(() => [])
    : []
  const athleteEntry = grilla.find((entry) => entry.atleta_id === atleta.atleta_id) ?? null

  let apActual: string | null = athleteEntry?.ap_declarado ?? null
  if (!apActual && inscripcion) {
    try {
      const apDto = await fetchApInscripcion(inscripcion.inscripcion_id, disciplina)
      apActual = apDto.ap
    } catch {
      // sin AP previo
    }
  }

  return { torneo, competencia, athleteEntry, apActual, inscripcion }
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
      const inscripcionId = query.data?.inscripcion?.inscripcion_id
      if (!inscripcionId || !disciplina) {
        throw new Error('No se encontró la inscripción activa para esta disciplina.')
      }
      return guardarApInscripcion({
        inscripcionId,
        disciplina,
        valorAp: normalizeApInput(valorApValue, disciplina),
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
  const apBloqueado = Boolean(currentAp)
  const puedeGuardar = isApInputValido(valorApValue, disciplina ?? '')

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
              AP — {unidadEsperada === 'Segundos' ? 'Tiempo anunciado (mm:ss)' : 'Distancia anunciada'} *
              <div className="mt-3 flex items-center gap-3 rounded-3xl border border-sky-500/40 bg-sky-500/10 px-4 py-4">
                <input
                  value={valorApValue}
                  onChange={(event) => setValorAp(event.target.value)}
                  inputMode={esDisciplinaTiempo(disciplina ?? '') ? 'text' : 'decimal'}
                  placeholder={esDisciplinaTiempo(disciplina ?? '') ? 'mm:ss' : '0'}
                  disabled={apBloqueado}
                  className="w-full bg-transparent text-3xl font-semibold text-white outline-none"
                />
                <span className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-300">
                  {unidadLabel}
                </span>
              </div>
            </label>
            {currentAp ? (
              <p className="mt-3 text-sm text-slate-400">
                AP actual guardado: {formatAp(currentAp, query.data.athleteEntry?.unidad ?? unidadEsperada)}
              </p>
            ) : null}
            {apBloqueado ? (
              <p className="mt-3 text-sm text-amber-300">
                El AP ya fue declarado y no puede volver a editarse.
              </p>
            ) : null}
          </section>

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
              disabled={apBloqueado || mutation.isPending || !puedeGuardar}
              className="flex-1 rounded-2xl bg-sky-500 px-4 py-3 text-sm font-semibold uppercase tracking-[0.16em] text-slate-950 disabled:opacity-60"
            >
              {apBloqueado ? 'AP bloqueado' : mutation.isPending ? 'Guardando...' : 'Guardar AP'}
            </button>
          </div>
        </div>
      ) : null}
    </AtletaShell>
  )
}
