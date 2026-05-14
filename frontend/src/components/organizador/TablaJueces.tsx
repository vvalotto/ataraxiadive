import type { UsuarioDto } from '../../api/identidad'
import { formatMarca } from '../../utils/marca'
import { JuezSelector } from './JuezSelector'

export interface FilaJuezPerformance {
  competenciaId: string
  disciplina: string
  performanceId: string
  atletaId: string
  nombreAtleta: string
  posicion: number
  andarivel: number
  otProgramado: string
  apDeclarado: string
  unidad: string
  juezId: string | null
}

interface TablaJuecesProps {
  rows: FilaJuezPerformance[]
  jueces: UsuarioDto[]
  savingKey: string | null
  disciplina: string | null
  onAsignar: (row: FilaJuezPerformance, juezId: string) => void
}

function formatOt(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('es-AR', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function TablaJueces({
  rows,
  jueces,
  savingKey,
  disciplina,
  onAsignar,
}: TablaJuecesProps) {
  if (rows.length === 0) {
    return (
      <div className="rounded-xl border border-slate-700 bg-slate-950/70 p-4 text-sm text-slate-300">
        No hay performances listas para asignar. Primero debes generar y confirmar la grilla.
      </div>
    )
  }

  return (
    <section className="rounded-[1.25rem] border border-slate-700 bg-slate-950/60">
      <div className="flex items-center justify-between border-b border-slate-800 px-4 py-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
            Disciplina
          </p>
          <h3 className="mt-1 text-lg font-semibold text-white">{disciplina ?? 'Sin selección'}</h3>
        </div>
        <span className="rounded-full border border-slate-700 bg-slate-900 px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] text-slate-300">
          {rows.filter((row) => row.juezId).length}/{rows.length} asignadas
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-800 text-left text-sm">
          <thead className="bg-slate-950/80 text-xs font-semibold uppercase text-slate-400">
            <tr>
              <th className="px-4 py-3">Atleta</th>
              <th className="px-4 py-3">And.</th>
              <th className="px-4 py-3">OT</th>
              <th className="px-4 py-3">AP</th>
              <th className="px-4 py-3">Juez asignado</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800 bg-slate-900/70">
            {rows.map((row) => {
              const rowSavingKey = `${row.competenciaId}:${row.performanceId}`
              const saving = savingKey === rowSavingKey
              return (
                <tr key={row.performanceId}>
                  <td className="px-4 py-3">
                    <p className="font-semibold text-white">{row.nombreAtleta}</p>
                    <p className="mt-1 text-xs text-slate-400">Posición {row.posicion}</p>
                  </td>
                  <td className="px-4 py-3 text-center font-semibold text-slate-200">
                    {row.andarivel}
                  </td>
                  <td className="px-4 py-3 text-slate-300">{formatOt(row.otProgramado)}</td>
                  <td className="px-4 py-3 text-slate-300">
                    {formatMarca(row.apDeclarado, row.unidad)}
                  </td>
                  <td className="min-w-64 px-4 py-3">
                    <JuezSelector
                      jueces={jueces}
                      value={row.juezId}
                      disabled={saving || jueces.length === 0}
                      onChange={(juezId) => onAsignar(row, juezId)}
                    />
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </section>
  )
}
