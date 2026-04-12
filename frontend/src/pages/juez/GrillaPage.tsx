import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import {
  fetchGrillaCompetencia,
  fetchPerformanceActual,
  type GrillaAtletaDto,
} from '../../api/competencia'
import { JuezLayout } from '../../components/juez/JuezLayout'
import useCompetenciaStore from '../../stores/useCompetenciaStore'

type RowStatus = 'SIGUIENTE' | 'PENDIENTE' | 'EN_CURSO' | 'REVISION' | 'FINALIZADA'

function resolveRowStatus(
  atleta: GrillaAtletaDto,
  currentPerformanceId: string | null,
  firstPendingPerformanceId: string | null,
): RowStatus {
  if (atleta.performance_id === currentPerformanceId) {
    return 'EN_CURSO'
  }

  if (atleta.estado === 'Ejecutada' || atleta.estado === 'DNS') {
    return 'FINALIZADA'
  }

  if (atleta.estado === 'EnRevision') {
    return 'REVISION'
  }

  if (atleta.estado === 'Llamada' || atleta.estado === 'ResultadoRegistrado') {
    return 'EN_CURSO'
  }

  if (atleta.performance_id === firstPendingPerformanceId) {
    return 'SIGUIENTE'
  }

  return 'PENDIENTE'
}

const STATUS_ORDER: Record<RowStatus, number> = {
  SIGUIENTE: 0,
  EN_CURSO: 1,
  REVISION: 2,
  PENDIENTE: 3,
  FINALIZADA: 4,
}

function statusClasses(status: RowStatus) {
  if (status === 'EN_CURSO') {
    return 'border-cyan-300/60 bg-cyan-400/10'
  }
  if (status === 'SIGUIENTE') {
    return 'border-emerald-300/50 bg-emerald-400/10'
  }
  if (status === 'REVISION') {
    return 'border-amber-300/60 bg-amber-400/10'
  }
  if (status === 'FINALIZADA') {
    return 'border-slate-800 bg-slate-900/40 opacity-50'
  }
  return 'border-slate-800 bg-slate-900/75'
}

export function GrillaPage() {
  const navigate = useNavigate()
  const disciplinaActiva = useCompetenciaStore((s) => s.disciplinaActiva)
  const competenciaId = useCompetenciaStore((s) => s.competenciaId)
  const seleccionarAtleta = useCompetenciaStore((s) => s.seleccionarAtleta)

  const grillaQuery = useQuery({
    queryKey: ['grilla', competenciaId, disciplinaActiva],
    queryFn: () => fetchGrillaCompetencia(competenciaId!, disciplinaActiva!),
    enabled: Boolean(competenciaId && disciplinaActiva),
  })

  const performanceActualQuery = useQuery({
    queryKey: ['performance-actual', competenciaId],
    queryFn: () => fetchPerformanceActual(competenciaId!),
    enabled: Boolean(competenciaId),
    refetchInterval: 5000,
  })

  const firstPendingPerformanceId = useMemo(() => {
    const grilla = grillaQuery.data ?? []
    const first = grilla.find((atleta) => atleta.estado === 'AnunciadaAP')
    return first?.performance_id ?? null
  }, [grillaQuery.data])

  const grillaOrdenada = useMemo(() => {
    const grilla = grillaQuery.data ?? []
    return [...grilla].sort((a, b) => {
      const statusA = resolveRowStatus(
        a,
        performanceActualQuery.data?.performance_id ?? null,
        firstPendingPerformanceId,
      )
      const statusB = resolveRowStatus(
        b,
        performanceActualQuery.data?.performance_id ?? null,
        firstPendingPerformanceId,
      )
      return STATUS_ORDER[statusA] - STATUS_ORDER[statusB]
    })
  }, [grillaQuery.data, performanceActualQuery.data, firstPendingPerformanceId])

  if (!competenciaId || !disciplinaActiva) {
    return (
      <JuezLayout title="Grilla" subtitle="Sin competencia seleccionada">
        <section className="rounded-3xl border border-slate-800 bg-slate-900/70 p-5 text-sm text-slate-300">
          No hay competencia seleccionada.
        </section>
      </JuezLayout>
    )
  }

  return (
    <JuezLayout
      title="Grilla"
      subtitle={`${disciplinaActiva} · ${competenciaId}`}
      actions={
        <Link
          to="/juez/disciplinas"
          className="rounded-full border border-slate-700 px-3 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate-200"
        >
          Volver
        </Link>
      }
    >
      {grillaQuery.isLoading ? (
        <section className="rounded-3xl border border-slate-800 bg-slate-900/70 p-5 text-sm text-slate-300">
          Cargando grilla...
        </section>
      ) : null}

      {grillaQuery.isError ? (
        <section className="rounded-3xl border border-red-500/30 bg-red-500/10 p-5 text-sm text-red-100">
          No se pudo cargar la grilla.
        </section>
      ) : null}

      {grillaOrdenada.map((atleta) => {
        const status = resolveRowStatus(
          atleta,
          performanceActualQuery.data?.performance_id ?? null,
          firstPendingPerformanceId,
        )
        const disabled = status === 'FINALIZADA'

        return (
          <button
            key={atleta.performance_id}
            type="button"
            disabled={disabled}
            onClick={() => {
              seleccionarAtleta({
                performanceId: atleta.performance_id,
                atletaId: atleta.atleta_id,
                nombreAtleta: atleta.nombre_atleta,
                posicion: atleta.posicion,
                andarivel: atleta.andarivel,
                otProgramado: atleta.ot_programado,
                apDeclarado: atleta.ap_declarado,
                unidad: atleta.unidad,
                estado: atleta.estado,
              })
              void navigate('/juez/performance')
            }}
            className={`block w-full rounded-[2rem] border p-5 text-left transition ${statusClasses(status)}`}
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
                  #{atleta.posicion} · andarivel {atleta.andarivel}
                </p>
                <h2 className="mt-2 text-lg font-semibold text-slate-50">{atleta.nombre_atleta}</h2>
                <p className="mt-2 text-sm text-slate-400">
                  AP {atleta.ap_declarado} {atleta.unidad}
                </p>
              </div>
              <span
                className={[
                  'rounded-full px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.18em]',
                  status === 'EN_CURSO' ? 'bg-cyan-400/15 text-cyan-200' : '',
                  status === 'SIGUIENTE' ? 'bg-emerald-400/15 text-emerald-200' : '',
                  status === 'REVISION' ? 'bg-amber-300/15 text-amber-100' : '',
                  status === 'PENDIENTE' ? 'bg-slate-800 text-slate-300' : '',
                  status === 'FINALIZADA' ? 'bg-slate-950 text-slate-500' : '',
                ].join(' ')}
              >
                {status}
              </span>
            </div>
          </button>
        )
      })}
    </JuezLayout>
  )
}
