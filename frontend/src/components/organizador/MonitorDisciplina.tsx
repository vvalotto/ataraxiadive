import { useState } from 'react'
import type { CompetenciaResumenDto, GrillaAtletaDto, ProgresoCompetenciaDto } from '../../api/competencia'
import { ProgressBar } from './ProgressBar'

interface MonitorDisciplinaProps {
  competencia: CompetenciaResumenDto
  progreso: ProgresoCompetenciaDto
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

function formatMarca(value?: string | null, unidad?: string) {
  if (!value) return '-'
  return unidad ? `${value} ${unidad}` : value
}

export function MonitorDisciplina({
  competencia,
  progreso,
  grilla,
}: MonitorDisciplinaProps) {
  const pendientes = Math.max(progreso.total - progreso.completadas, 0)

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

      <GrillaCompleta
        grilla={grilla}
        completadas={progreso.completadas}
        total={progreso.total}
      />
    </article>
  )
}

interface GrillaCompletaProps {
  grilla: GrillaAtletaDto[]
  completadas: number
  total: number
}

function GrillaCompleta({ grilla, completadas, total }: GrillaCompletaProps) {
  const [showGrilla, setShowGrilla] = useState(false)

  return (
    <div className="mt-5 rounded-lg border border-sky-700 bg-sky-50/40">
      <button
        type="button"
        onClick={() => setShowGrilla((current) => !current)}
        className="flex min-h-12 w-full items-center justify-between gap-3 px-4 py-3 text-left"
        aria-expanded={showGrilla}
      >
        <span>
          <span className="block text-sm font-semibold text-stone-950">Grilla completa</span>
          <span className="block text-xs text-stone-600">
            {completadas} / {total} completadas · {grilla.length} atletas
          </span>
        </span>
        <span className="rounded-lg border border-sky-700 bg-white px-3 py-1 text-sm font-semibold text-sky-900">
          {showGrilla ? 'Ocultar' : 'Mostrar grilla'}
        </span>
      </button>

      {showGrilla ? (
        <div className="overflow-x-auto border-t border-sky-200 bg-white">
          <table className="min-w-full divide-y divide-stone-200 text-left text-sm">
            <thead className="bg-stone-50 text-xs font-semibold uppercase text-stone-500">
              <tr>
                <th className="px-4 py-3">Nombre</th>
                <th className="px-4 py-3">Andarivel</th>
                <th className="px-4 py-3">OT</th>
                <th className="px-4 py-3">AP</th>
                <th className="px-4 py-3">Performance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-200 bg-white">
              {grilla.map((row) => (
                <tr key={row.performance_id}>
                  <td className="px-4 py-3 font-semibold text-stone-950">
                    {row.nombre_atleta}
                  </td>
                  <td className="px-4 py-3 text-stone-700">{row.andarivel}</td>
                  <td className="px-4 py-3 text-stone-700">
                    {formatOt(row.ot_programado) ?? '-'}
                  </td>
                  <td className="px-4 py-3 text-stone-700">
                    {formatMarca(row.ap_declarado, row.unidad)}
                  </td>
                  <td className="px-4 py-3 text-stone-700">
                    {row.estado === 'DNS'
                      ? 'DNS'
                      : formatMarca(row.performance, row.performance ? row.unidad : '')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </div>
  )
}
