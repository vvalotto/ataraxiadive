import { useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { useQueries, useQuery } from '@tanstack/react-query'
import {
  fetchCompetenciasPorTorneo,
  fetchEstadoCompetencia,
  fetchGrillaCompetencia,
  fetchProgresoCompetencia,
  fetchProximasPerformances,
  type CompetenciaResumenDto,
  type EstadoCompetenciaDto,
  type GrillaAtletaDto,
  type ProgresoCompetenciaDto,
  type ProximoAtletaDto,
} from '../../api/competencia'
import { fetchTorneo, type EstadoTorneo } from '../../api/torneo'
import { EmptyStateCard } from '../../components/organizador/EmptyStateCard'
import { OrganizadorLayout } from '../../components/organizador/OrganizadorLayout'
import { TorneoRouteSelector } from '../../components/organizador/TorneoRouteSelector'
import { formatMarca } from '../../utils/marca'

type EstadoCompetenciaNormalizado = 'EN_EJECUCION' | 'PENDIENTE' | 'CERRADA' | 'DESCONOCIDO'

interface CompetenciaOperativa {
  competencia: CompetenciaResumenDto
  estadoRaw: string | null
  estado: EstadoCompetenciaNormalizado
  intervaloMinutos: number | null
}

interface KpiCardProps {
  label: string
  value: string
  tone?: 'default' | 'success' | 'warning' | 'accent'
  detail?: string
}

interface AlertItem {
  atleta: string
  disciplina: string
  descripcion: string
  href: string
}

function normalizarClave(valor: string | null | undefined): string {
  return String(valor ?? '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-zA-Z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .toUpperCase()
}

function normalizarEstadoCompetencia(estado: string | null | undefined): EstadoCompetenciaNormalizado {
  const normalized = normalizarClave(estado)
  const compact = normalized.split('_').join('')

  if (normalized === 'EN_EJECUCION' || compact === 'ENEJECUCION') {
    return 'EN_EJECUCION'
  }

  if (
    normalized === 'FINALIZADA' ||
    normalized === 'COMPETENCIA_FINALIZADA' ||
    compact === 'COMPETENCIAFINALIZADA'
  ) {
    return 'CERRADA'
  }

  if (
    normalized === 'CONFIGURADA' ||
    normalized === 'GRILLA_CONFIRMADA' ||
    normalized === 'CREADA' ||
    normalized === 'PENDIENTE'
  ) {
    return 'PENDIENTE'
  }

  return normalized ? 'DESCONOCIDO' : 'DESCONOCIDO'
}

function labelEstadoCompetencia(estado: EstadoCompetenciaNormalizado): string {
  if (estado === 'EN_EJECUCION') return 'EN EJECUCION'
  if (estado === 'CERRADA') return 'CERRADA'
  return 'PENDIENTE'
}

function badgeClass(estado: EstadoCompetenciaNormalizado): string {
  if (estado === 'EN_EJECUCION') {
    return 'border-emerald-500/40 bg-emerald-500/10 text-emerald-200'
  }
  if (estado === 'CERRADA') {
    return 'border-sky-500/40 bg-sky-500/10 text-sky-200'
  }
  return 'border-slate-600 bg-slate-800 text-slate-300'
}

function formatTorneoEstado(estado: EstadoTorneo): string {
  switch (estado) {
    case 'CREADO':
      return 'Creado'
    case 'INSCRIPCION_ABIERTA':
      return 'Inscripcion abierta'
    case 'PREPARACION':
      return 'Preparacion'
    case 'EJECUCION':
      return 'En ejecucion'
    case 'PREMIACION':
      return 'Premiacion'
    case 'CERRADO':
      return 'Cerrado'
    case 'CANCELADO':
      return 'Cancelado'
  }
}

function formatDurationMinutes(totalMinutes: number | null): string {
  if (totalMinutes === null || totalMinutes <= 0) return 'Sin ETA'
  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60
  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`
}

function formatOtHora(ot: string | null | undefined): string {
  if (!ot) return '—'

  const match = ot.match(/T(\d{2}:\d{2})/)
  if (match) return match[1]

  const timeMatch = ot.match(/^(\d{2}:\d{2})/)
  if (timeMatch) return timeMatch[1]

  const date = new Date(ot)
  if (!Number.isNaN(date.getTime())) {
    return date.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit', hour12: false })
  }

  return ot
}

function formatKpiCompletados(progreso: ProgresoCompetenciaDto | undefined): string {
  if (!progreso) return 'Sin datos'
  return `${progreso.completadas} de ${progreso.total}`
}

function formatRevisionCount(alertas: AlertItem[]): string {
  if (alertas.length === 0) return 'Sin alertas'
  if (alertas.length === 1) return '1 tarjeta amarilla'
  return `${alertas.length} tarjetas amarillas`
}

function buildCompetenciasOperativas(
  competencias: CompetenciaResumenDto[],
  estados: Array<EstadoCompetenciaDto | undefined>,
): CompetenciaOperativa[] {
  return competencias.map((competencia, index) => {
    const estadoDto = estados[index]
    return {
      competencia,
      estadoRaw: estadoDto?.estado ?? null,
      estado: normalizarEstadoCompetencia(estadoDto?.estado),
      intervaloMinutos: estadoDto?.intervalo_minutos ?? null,
    }
  })
}

function pickCompetenciaActiva(competencias: CompetenciaOperativa[]): CompetenciaOperativa | null {
  return (
    competencias.find((item) => item.estado === 'EN_EJECUCION') ??
    competencias.find((item) => item.estado === 'PENDIENTE') ??
    competencias[0] ??
    null
  )
}

function isPerformanceFinalizada(estado: GrillaAtletaDto['estado']): boolean {
  return estado === 'Ejecutada' || estado === 'DNS'
}

function buildAlertas(
  grilla: GrillaAtletaDto[],
  competenciaActiva: CompetenciaOperativa | null,
): AlertItem[] {
  if (!competenciaActiva) return []

  return grilla
    .filter((fila) => fila.estado === 'EnRevision')
    .map((fila) => ({
      atleta: fila.nombre_atleta,
      disciplina: competenciaActiva.competencia.disciplina,
      descripcion: `Performance en revision en OT ${formatOtHora(fila.ot_programado)} con AP ${formatMarca(fila.ap_declarado, fila.unidad)}`,
      href: `/organizador/grilla?torneo_id=${competenciaActiva.competencia.torneo_id}`,
    }))
}

function buildProximos(
  grilla: GrillaAtletaDto[],
  proximas: ProximoAtletaDto[],
): Array<{
  atleta: string
  andarivel: number | string
  ap: string
  ot: string
}> {
  if (proximas.length > 0) {
    const filasProximas = proximas.map((item) => {
      const match =
        grilla.find((fila) => fila.posicion === item.posicion) ??
        grilla.find((fila) => fila.nombre_atleta === item.nombre_atleta)
      return {
        atleta: item.nombre_atleta,
        andarivel: match?.andarivel ?? '—',
        ap: formatMarca(item.ap_declarado, item.unidad),
        ot: formatOtHora(match?.ot_programado),
      }
    })

    const atletasIncluidos = new Set(filasProximas.map((fila) => fila.atleta))
    const filasRestantes = grilla
      .filter(
        (fila) =>
          !isPerformanceFinalizada(fila.estado) &&
          fila.estado !== 'EnRevision' &&
          !atletasIncluidos.has(fila.nombre_atleta),
      )
      .sort((a, b) => a.posicion - b.posicion)
      .map((fila) => ({
        atleta: fila.nombre_atleta,
        andarivel: fila.andarivel,
        ap: formatMarca(fila.ap_declarado, fila.unidad),
        ot: formatOtHora(fila.ot_programado),
      }))

    return [...filasProximas, ...filasRestantes].slice(0, 6)
  }

  return grilla
    .filter((fila) => !isPerformanceFinalizada(fila.estado) && fila.estado !== 'EnRevision')
    .sort((a, b) => a.posicion - b.posicion)
    .slice(0, 6)
    .map((fila) => ({
      atleta: fila.nombre_atleta,
      andarivel: fila.andarivel,
      ap: formatMarca(fila.ap_declarado, fila.unidad),
      ot: formatOtHora(fila.ot_programado),
    }))
}

function estimateRemainingMinutes(
  progreso: ProgresoCompetenciaDto | undefined,
  competenciaActiva: CompetenciaOperativa | null,
): number | null {
  if (!progreso || !competenciaActiva?.intervaloMinutos) return null
  const restantes = Math.max(progreso.total - progreso.ejecutadas, 0)
  return restantes * competenciaActiva.intervaloMinutos
}

function toneClasses(tone: KpiCardProps['tone']): string {
  if (tone === 'success') return 'text-emerald-300'
  if (tone === 'warning') return 'text-amber-300'
  if (tone === 'accent') return 'text-sky-300'
  return 'text-white'
}

function KpiCard({ label, value, tone = 'default', detail }: KpiCardProps) {
  return (
    <article className="rounded-[2rem] border border-slate-700 bg-slate-900/80 p-5 shadow-[0_20px_60px_rgba(2,6,23,0.24)]">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">{label}</p>
      <p className={`mt-3 text-3xl font-semibold tracking-tight ${toneClasses(tone)}`}>{value}</p>
      {detail ? <p className="mt-2 text-sm text-slate-400">{detail}</p> : null}
    </article>
  )
}

function DisciplinaProgress({ completadas, total }: { completadas: number; total: number }) {
  const safeTotal = Math.max(total, 0)
  const safeCompleted = Math.min(Math.max(completadas, 0), safeTotal)
  const percent = safeTotal === 0 ? 0 : Math.round((safeCompleted / safeTotal) * 100)

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between text-sm">
        <span className="text-slate-300">
          {safeCompleted} de {safeTotal} atletas completados
        </span>
        <span className="font-semibold text-emerald-300">{percent}%</span>
      </div>
      <div className="h-3 overflow-hidden rounded-full bg-slate-800">
        <div
          className="h-full rounded-full bg-emerald-500 transition-[width]"
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  )
}

export function DashboardOperativoPage() {
  const [searchParams] = useSearchParams()
  const torneoId = searchParams.get('torneo_id')

  if (!torneoId) {
    return (
      <OrganizadorLayout
        title="Panel"
        subtitle="Estado general y alertas del torneo activo"
        showTournamentNavigation={false}
        simpleHeader
      >
        <TorneoRouteSelector
          description="El Panel es la vista ejecutiva del torneo operativo. Selecciona un torneo para cargar KPIs, disciplina activa, alertas y proximos atletas."
          ctaLabel="Abrir panel"
          buildHref={(nextTorneoId) => `/organizador/panel?torneo_id=${nextTorneoId}`}
        />
      </OrganizadorLayout>
    )
  }

  return <DashboardOperativoContent torneoId={torneoId} />
}

function DashboardOperativoContent({ torneoId }: { torneoId: string }) {
  const [disciplinaSeleccionada, setDisciplinaSeleccionada] = useState<string>('')

  const torneoQuery = useQuery({
    queryKey: ['torneo', torneoId],
    queryFn: () => fetchTorneo(torneoId),
  })

  const competenciasQuery = useQuery({
    queryKey: ['competencias-torneo', torneoId],
    queryFn: () => fetchCompetenciasPorTorneo(torneoId),
  })

  const estadoCompetenciasQueries = useQueries({
    queries:
      competenciasQuery.data?.map((competencia) => ({
        queryKey: ['panel-estado-competencia', competencia.competencia_id, competencia.disciplina],
        queryFn: () => fetchEstadoCompetencia(competencia.competencia_id, competencia.disciplina),
        enabled: Boolean(competencia.competencia_id && competencia.disciplina),
      })) ?? [],
  })

  const competenciasOperativas = useMemo(
    () =>
      buildCompetenciasOperativas(
        competenciasQuery.data ?? [],
        estadoCompetenciasQueries.map((query) => query.data),
      ),
    [competenciasQuery.data, estadoCompetenciasQueries],
  )

  const competenciaActiva = useMemo(() => {
    if (disciplinaSeleccionada) {
      return competenciasOperativas.find(
        (item) => item.competencia.disciplina === disciplinaSeleccionada,
      ) ?? pickCompetenciaActiva(competenciasOperativas)
    }
    return pickCompetenciaActiva(competenciasOperativas)
  }, [competenciasOperativas, disciplinaSeleccionada])

  const progresoQuery = useQuery({
    queryKey: ['panel-progreso', competenciaActiva?.competencia.competencia_id],
    queryFn: () => fetchProgresoCompetencia(competenciaActiva!.competencia.competencia_id),
    enabled: Boolean(competenciaActiva),
  })

  const grillaActivaQuery = useQuery({
    queryKey: [
      'panel-grilla-activa',
      competenciaActiva?.competencia.competencia_id,
      competenciaActiva?.competencia.disciplina,
    ],
    queryFn: () =>
      fetchGrillaCompetencia(
        competenciaActiva!.competencia.competencia_id,
        competenciaActiva!.competencia.disciplina,
      ),
    enabled: Boolean(competenciaActiva),
  })

  const proximasQuery = useQuery({
    queryKey: [
      'panel-proximas',
      competenciaActiva?.competencia.competencia_id,
      competenciaActiva?.competencia.disciplina,
    ],
    queryFn: () =>
      fetchProximasPerformances(
        competenciaActiva!.competencia.competencia_id,
        competenciaActiva!.competencia.disciplina,
      ),
    enabled: Boolean(competenciaActiva),
  })

  const loadingCompetencias =
    competenciasQuery.isLoading || estadoCompetenciasQueries.some((query) => query.isLoading)

  const grillaActiva = useMemo(() => grillaActivaQuery.data ?? [], [grillaActivaQuery.data])
  const alertas = useMemo(
    () => buildAlertas(grillaActiva, competenciaActiva),
    [grillaActiva, competenciaActiva],
  )
  const proximos = useMemo(
    () => buildProximos(grillaActiva, proximasQuery.data ?? []),
    [grillaActiva, proximasQuery.data],
  )

  const totalAtletas = progresoQuery.data?.total ?? grillaActiva.length
  const tiempoEstimado = formatDurationMinutes(
    estimateRemainingMinutes(progresoQuery.data, competenciaActiva),
  )
  const atletasDisciplinaActiva =
    grillaActiva.length > 0 ? grillaActiva.length : progresoQuery.data?.total ?? 0

  return (
    <OrganizadorLayout
      title="Panel"
      activeTournamentId={torneoId}
      activeTournamentState={torneoQuery.data?.estado}
      subtitle="Estado general y alertas del torneo activo"
    >
      {torneoQuery.isLoading || loadingCompetencias ? (
        <section className="rounded-[2rem] border border-slate-700 bg-slate-900/70 p-5 text-sm text-slate-300">
          Cargando panel operativo...
        </section>
      ) : null}

      {torneoQuery.isError || competenciasQuery.isError ? (
        <section className="rounded-[2rem] border border-red-500/40 bg-red-950/40 p-5 text-sm text-red-100">
          No se pudo cargar el contexto operativo del torneo.
        </section>
      ) : null}

      {!torneoQuery.isLoading &&
      !torneoQuery.isError &&
      !competenciasQuery.isLoading &&
      !competenciasQuery.isError &&
      competenciasOperativas.length === 0 ? (
        <EmptyStateCard message="Este torneo todavía no tiene competencias operativas." />
      ) : null}

      {competenciasOperativas.length > 1 ? (
        <div className="flex gap-1 rounded-[2rem] border border-slate-700 bg-slate-900/85 overflow-hidden">
          {competenciasOperativas.map((item) => {
            const disc = item.competencia.disciplina
            const isActive = (disciplinaSeleccionada || competenciaActiva?.competencia.disciplina) === disc
            return (
              <button
                key={disc}
                type="button"
                onClick={() => setDisciplinaSeleccionada(disc)}
                className={`flex-1 py-2.5 text-xs font-semibold uppercase tracking-[0.18em] transition-colors ${
                  isActive ? 'bg-slate-800 text-sky-400' : 'text-slate-500 hover:text-slate-300'
                }`}
              >
                {disc}
              </button>
            )
          })}
        </div>
      ) : null}

      {competenciaActiva ? (
        <>
          <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <KpiCard
              label="Atletas totales"
              value={String(totalAtletas)}
              detail={`Disciplina activa: ${competenciaActiva.competencia.disciplina}`}
            />
            <KpiCard
              label="Completados"
              value={formatKpiCompletados(progresoQuery.data)}
              tone="success"
              detail="Ejecucion consolidada de la disciplina activa"
            />
            <KpiCard
              label="En revision"
              value={formatRevisionCount(alertas)}
              tone="warning"
              detail="Alertas operativas pendientes de resolucion"
            />
            <KpiCard
              label="Tiempo estimado (hh:mm)"
              value={tiempoEstimado}
              tone="accent"
              detail="Estimacion basada en intervalo configurado y atletas pendientes"
            />
          </section>

          <section className="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
            <article className="rounded-[2rem] border border-slate-700 bg-slate-900/85 p-6 shadow-[0_20px_60px_rgba(2,6,23,0.24)]">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                Proximos atletas
              </p>
              <h3 className="mt-2 text-xl font-semibold text-white">
                Cola operativa de la disciplina activa
              </h3>

              <div className="mt-4 overflow-hidden rounded-[1.25rem] border border-slate-700">
                <table className="min-w-full divide-y divide-slate-700 text-sm">
                  <thead className="bg-slate-950/70 text-slate-400">
                    <tr>
                      <th className="px-4 py-3 text-left font-semibold">Atleta</th>
                      <th className="px-4 py-3 text-left font-semibold">Andarivel</th>
                      <th className="px-4 py-3 text-left font-semibold">OT</th>
                      <th className="px-4 py-3 text-left font-semibold">AP</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 bg-slate-900/70 text-slate-200">
                    {proximos.length > 0 ? (
                      proximos.map((fila, index) => (
                        <tr
                          key={`${fila.atleta}-${fila.ot}-${index}`}
                          className={
                            index === 0
                              ? 'bg-emerald-500/20 ring-1 ring-emerald-400/50 text-white'
                              : index < 3
                                ? 'bg-emerald-500/10 text-slate-50'
                              : 'bg-slate-900/40 text-slate-200'
                          }
                        >
                          <td className="px-4 py-3 font-medium">{fila.atleta}</td>
                          <td className="px-4 py-3 text-slate-300">{fila.andarivel}</td>
                          <td className="px-4 py-3 text-slate-300">{fila.ot}</td>
                          <td className="px-4 py-3 text-slate-300">{fila.ap}</td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={4} className="px-4 py-4 text-slate-300">
                          No hay proximos atletas listados para la disciplina activa.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </article>

            <div className="grid gap-4">
              <article className="rounded-[2rem] border border-slate-700 bg-slate-900/85 p-6 shadow-[0_20px_60px_rgba(2,6,23,0.24)]">
                <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                      Disciplina activa
                    </p>
                    <h2 className="mt-2 text-2xl font-semibold text-white">
                      {competenciaActiva.competencia.disciplina}
                    </h2>
                    <p className="mt-2 text-sm text-slate-300">
                      {atletasDisciplinaActiva} atletas · intervalo{' '}
                      {competenciaActiva.intervaloMinutos ?? '—'} min
                    </p>
                  </div>
                  <span
                    className={`rounded-full border px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.16em] ${badgeClass(
                      competenciaActiva.estado,
                    )}`}
                  >
                    {labelEstadoCompetencia(competenciaActiva.estado)}
                  </span>
                </div>

                <div className="mt-6">
                  <DisciplinaProgress
                    completadas={progresoQuery.data?.completadas ?? 0}
                    total={progresoQuery.data?.total ?? atletasDisciplinaActiva}
                  />
                </div>
              </article>

              <article className="rounded-[2rem] border border-slate-700 bg-slate-900/85 p-6 shadow-[0_20px_60px_rgba(2,6,23,0.24)]">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                      Alertas activas
                    </p>
                    <h3 className="mt-2 text-xl font-semibold text-white">Operacion en revision</h3>
                  </div>
                </div>

                <div className="mt-4 space-y-3">
                  {alertas.length > 0 ? (
                    alertas.map((alerta) => (
                      <Link
                        key={`${alerta.disciplina}-${alerta.atleta}`}
                        to={alerta.href}
                        className="block rounded-[1.25rem] border border-amber-500/30 bg-amber-950/30 p-4 transition hover:border-amber-400/50"
                      >
                        <p className="text-sm font-semibold text-amber-100">
                          {alerta.atleta} · {alerta.disciplina}
                        </p>
                        <p className="mt-2 text-sm text-amber-50/90">{alerta.descripcion}</p>
                      </Link>
                    ))
                  ) : (
                    <div className="rounded-[1.25rem] border border-slate-700 bg-slate-950/70 p-4 text-sm text-slate-300">
                      Sin alertas
                    </div>
                  )}
                </div>
              </article>
            </div>
          </section>
        </>
      ) : null}
    </OrganizadorLayout>
  )
}
