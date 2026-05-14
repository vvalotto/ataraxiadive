import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import {
  fetchPerformanceActual,
  type GrillaAtletaDto,
} from '../../api/competencia'
import { useGrillaQueue, projectedEstado } from '../../hooks/useGrillaQueue'
import { formatMarca } from '../../utils/marca'
import { usePrecarga } from '../../hooks/usePrecarga'
import { JuezLayout } from '../../components/juez/JuezLayout'
import useCompetenciaStore from '../../stores/useCompetenciaStore'
import useConnectionStore from '../../stores/useConnectionStore'
import useAuthStore from '../../stores/useAuthStore'

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

const STATUS_LABEL: Record<RowStatus, string> = {
  EN_CURSO: 'En curso',
  SIGUIENTE: 'Siguiente',
  REVISION: 'Revisión',
  PENDIENTE: 'Pendiente',
  FINALIZADA: 'Finalizada',
}

const STATUS_ORDER: Record<RowStatus, number> = {
  SIGUIENTE: 0,
  EN_CURSO: 1,
  REVISION: 2,
  PENDIENTE: 3,
  FINALIZADA: 4,
}

function parsePayload(payload: string): Record<string, unknown> {
  try {
    return JSON.parse(payload) as Record<string, unknown>
  } catch {
    return {}
  }
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
  const isOnline = useConnectionStore((s) => s.isOnline)
  const pendingCount = useConnectionStore((s) => s.pendingCount)
  const juezId = useAuthStore((s) => s.userId)

  const precargaQuery = usePrecarga({
    competenciaId,
    disciplina: disciplinaActiva,
    isOnline,
  })

  const performanceActualQuery = useQuery({
    queryKey: ['performance-actual', competenciaId],
    queryFn: () => fetchPerformanceActual(competenciaId!),
    enabled: Boolean(competenciaId && isOnline),
    refetchInterval: 5000,
  })

  const { queueData, pendingByAtleta } = useGrillaQueue(competenciaId)

  const firstPendingPerformanceId = useMemo(() => {
    const grillaBase = (precargaQuery.payload?.grilla ?? []).filter(
      (atleta) => atleta.juez_id === juezId,
    )
    const queue = queueData
    const grillaMap = new Map(grillaBase.map((atleta) => [atleta.atleta_id, { ...atleta }]))

    for (const cmd of queue) {
      const payload = parsePayload(cmd.payload)
      const participanteId = String(payload.participante_id ?? '')
      if (!participanteId) continue
      const atleta = grillaMap.get(participanteId)
      if (!atleta) continue
      atleta.estado = projectedEstado(cmd.tipo, payload)
      grillaMap.set(participanteId, atleta)
    }

    const grilla = Array.from(grillaMap.values())
    const first = grilla.find((atleta) => atleta.estado === 'AnunciadaAP')
    return first?.performance_id ?? null
  }, [juezId, precargaQuery.payload?.grilla, queueData])

  const grillaOrdenada = useMemo(() => {
    const grillaBase = (precargaQuery.payload?.grilla ?? []).filter(
      (atleta) => atleta.juez_id === juezId,
    )
    const queue = queueData
    const grillaMap = new Map(grillaBase.map((atleta) => [atleta.atleta_id, { ...atleta }]))

    for (const cmd of queue) {
      const payload = parsePayload(cmd.payload)
      const participanteId = String(payload.participante_id ?? '')
      if (!participanteId) continue
      const atleta = grillaMap.get(participanteId)
      if (!atleta) continue
      atleta.estado = projectedEstado(cmd.tipo, payload)
      grillaMap.set(participanteId, atleta)
    }

    return Array.from(grillaMap.values()).sort((a, b) => {
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
  }, [firstPendingPerformanceId, juezId, performanceActualQuery.data, precargaQuery.payload?.grilla, queueData])

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
      subtitle={`${disciplinaActiva}${pendingCount > 0 ? ` · ${pendingCount} pendientes` : ''}`}
      actions={
        <Link
          to="/juez/disciplinas"
          className="rounded-full border border-slate-700 px-3 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate-200"
        >
          Volver
        </Link>
      }
    >
      {precargaQuery.isLoading ? (
        <section className="rounded-3xl border border-slate-800 bg-slate-900/70 p-5 text-sm text-slate-300">
          Cargando grilla...
        </section>
      ) : null}

      {precargaQuery.errorCode === 'NO_CACHE_OFFLINE' ? (
        <section className="rounded-3xl border border-red-500/30 bg-red-500/10 p-5 text-sm text-red-100">
          Sin datos disponibles. Conectate a internet para cargar la disciplina por primera vez.
        </section>
      ) : null}

      {precargaQuery.isError && precargaQuery.errorCode !== 'NO_CACHE_OFFLINE' ? (
        <section className="rounded-3xl border border-red-500/30 bg-red-500/10 p-5 text-sm text-red-100">
          No se pudo cargar la grilla ni recuperar cache local.
        </section>
      ) : null}

      {precargaQuery.payload && !isOnline ? (
        <section className="rounded-3xl border border-amber-300/30 bg-amber-400/10 p-4 text-sm text-amber-100">
          Modo offline. {precargaQuery.cacheAgeLabel}
        </section>
      ) : null}

      {precargaQuery.payload && precargaQuery.isCacheExpired ? (
        <section className="rounded-3xl border border-amber-300/30 bg-amber-400/10 p-4 text-sm text-amber-100">
          El cache tiene mas de 24 horas. Los datos pueden estar desactualizados.
        </section>
      ) : null}

      {grillaOrdenada.map((atleta) => {
        const status = resolveRowStatus(
          atleta,
          performanceActualQuery.data?.performance_id ?? null,
          firstPendingPerformanceId,
        )
        const disabled = status === 'FINALIZADA'
        const pendientes = pendingByAtleta.get(atleta.atleta_id) ?? 0

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
            className={`block w-full rounded-[2rem] border px-4 py-3 text-left transition ${statusClasses(status)}`}
          >
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
                  #{atleta.posicion} · andarivel {atleta.andarivel}
                </p>
                <h2 className="mt-1 text-base font-semibold text-slate-50">{atleta.nombre_atleta}</h2>
                <p className="mt-1 text-sm text-slate-400">
                  AP {formatMarca(atleta.ap_declarado, atleta.unidad)}
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
                {STATUS_LABEL[status]}
                {pendientes > 0 ? ` ⏳ ${pendientes}` : ''}
              </span>
            </div>
          </button>
        )
      })}

      {!precargaQuery.isLoading && grillaOrdenada.length === 0 ? (
        <section className="rounded-3xl border border-slate-800 bg-slate-900/70 p-5 text-sm text-slate-300">
          No tienes atletas asignados en esta disciplina.
        </section>
      ) : null}
    </JuezLayout>
  )
}
