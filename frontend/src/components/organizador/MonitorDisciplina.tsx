import type {
  CompetenciaResumenDto,
  GrillaAtletaDto,
  PerformanceActualDto,
  ProgresoCompetenciaDto,
  ProximoAtletaDto,
} from '../../api/competencia'
import { ProgressBar } from './ProgressBar'

interface MonitorDisciplinaProps {
  competencia: CompetenciaResumenDto
  progreso: ProgresoCompetenciaDto
  performanceActual: PerformanceActualDto | null
  proximas: ProximoAtletaDto[]
  grilla: GrillaAtletaDto[]
}

function formatOt(value?: string) {
  if (!value) return null
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleTimeString('es-AR', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
}

function findOtByPerformance(grilla: GrillaAtletaDto[], performanceId?: string) {
  if (!performanceId) return null
  return formatOt(grilla.find((row) => row.performance_id === performanceId)?.ot_programado)
}

function findOtByPosition(grilla: GrillaAtletaDto[], position: number) {
  return formatOt(grilla.find((row) => row.posicion === position)?.ot_programado)
}

export function MonitorDisciplina({
  competencia,
  progreso,
  performanceActual,
  proximas,
  grilla,
}: MonitorDisciplinaProps) {
  const pendientes = Math.max(progreso.total - progreso.completadas, 0)
  const otActual = findOtByPerformance(grilla, performanceActual?.performance_id)

  return (
    <article className="rounded-lg border border-stone-300 bg-white p-5 shadow-[0_20px_60px_rgba(120,93,54,0.08)]">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase text-stone-500">Disciplina</p>
          <h3 className="mt-1 text-xl font-semibold text-stone-950">{competencia.disciplina}</h3>
        </div>
        <span className="rounded-lg border border-emerald-700 bg-emerald-50 px-3 py-2 text-sm font-semibold text-emerald-900">
          En ejecucion
        </span>
      </div>

      <div className="mt-5">
        <ProgressBar completed={progreso.completadas} total={progreso.total} />
        <p className="mt-2 text-sm text-stone-600">
          {progreso.ejecutadas} ejecutadas · {progreso.dns_count} DNS · {pendientes} pendientes
        </p>
      </div>

      <div className="mt-5 rounded-lg border border-stone-200 bg-stone-50 p-4">
        <p className="text-xs font-semibold uppercase text-stone-500">En curso</p>
        {performanceActual ? (
          <div className="mt-2">
            <p className="text-lg font-semibold text-stone-950">
              {performanceActual.nombre_atleta}
            </p>
            <p className="mt-1 text-sm text-stone-600">
              {otActual ? `OT ${otActual} · ` : ''}
              Andarivel {performanceActual.andarivel || '-'} · AP{' '}
              {performanceActual.ap_declarado || '-'} {performanceActual.unidad}
            </p>
          </div>
        ) : (
          <p className="mt-2 text-lg font-semibold text-stone-700">- En espera -</p>
        )}
      </div>

      <div className="mt-5">
        <p className="text-xs font-semibold uppercase text-stone-500">Proximos</p>
        {proximas.length > 0 ? (
          <ol className="mt-3 divide-y divide-stone-200 rounded-lg border border-stone-200">
            {proximas.map((atleta) => {
              const ot = findOtByPosition(grilla, atleta.posicion)
              return (
                <li
                  key={`${atleta.posicion}-${atleta.nombre_atleta}`}
                  className="flex flex-col gap-1 p-3 sm:flex-row sm:items-center sm:justify-between"
                >
                  <span className="font-semibold text-stone-900">{atleta.nombre_atleta}</span>
                  <span className="text-sm text-stone-600">
                    {ot ? `OT ${ot} · ` : ''}
                    Posicion {atleta.posicion}
                  </span>
                </li>
              )
            })}
          </ol>
        ) : (
          <p className="mt-2 rounded-lg border border-stone-200 bg-stone-50 p-3 text-sm text-stone-600">
            No hay proximos atletas.
          </p>
        )}
      </div>
    </article>
  )
}
