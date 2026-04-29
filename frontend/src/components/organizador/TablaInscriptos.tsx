import { useMemo, useState } from 'react'
import { EstadoAPBadge } from './EstadoAPBadge'

export interface EstadoAP {
  estado: 'pendiente' | 'declarado' | 'cerrado'
  ap: string | null
  unidad: string | null
}

export interface InscriptoRow {
  inscripcionId: string
  atletaId: string
  nombre: string
  club: string
  categoria: string
  estadoInscripcion: string
  disciplinas: string[]
  estadoApPorDisciplina: Record<string, EstadoAP>
}

interface TablaInscriptosProps {
  rows: InscriptoRow[]
  disciplinas: string[]
}

export function TablaInscriptos({ rows, disciplinas }: TablaInscriptosProps) {
  const [disciplinaFiltro, setDisciplinaFiltro] = useState('TODAS')
  const disciplinasVisibles =
    disciplinaFiltro === 'TODAS' ? disciplinas : disciplinas.filter((d) => d === disciplinaFiltro)
  const rowsFiltradas = useMemo(() => {
    if (disciplinaFiltro === 'TODAS') return rows
    return rows.filter((row) => row.disciplinas.includes(disciplinaFiltro))
  }, [disciplinaFiltro, rows])

  if (rows.length === 0) {
    return (
      <div className="rounded-[1.5rem] border border-slate-700 bg-slate-950/70 p-4 text-sm text-slate-300">
        Todavía no hay inscriptos para este torneo
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-slate-300">{rows.length} atletas inscriptos</p>
        <label className="text-sm font-semibold text-slate-200">
          Disciplina
          <select
            value={disciplinaFiltro}
            onChange={(event) => setDisciplinaFiltro(event.target.value)}
            className="ml-0 mt-2 min-h-10 rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 sm:ml-3 sm:mt-0"
          >
            <option value="TODAS">Todas</option>
            {disciplinas.map((disciplina) => (
              <option key={disciplina} value={disciplina}>
                {disciplina}
              </option>
            ))}
          </select>
        </label>
      </div>

      {rowsFiltradas.length === 0 ? (
        <div className="rounded-[1.5rem] border border-slate-700 bg-slate-950/70 p-4 text-sm text-slate-300">
          No hay atletas inscriptos en la disciplina seleccionada
        </div>
      ) : (
        <div className="overflow-x-auto rounded-[1.5rem] border border-slate-700">
          <table className="min-w-full divide-y divide-slate-700 text-left text-sm">
            <thead className="bg-slate-950/80 text-xs font-semibold uppercase text-slate-400">
              <tr>
                <th className="px-4 py-3">Atleta</th>
                <th className="px-4 py-3">Club</th>
                <th className="px-4 py-3">Categoria</th>
                <th className="px-4 py-3">Inscripcion</th>
                {disciplinasVisibles.map((disciplina) => (
                  <th key={disciplina} className="px-4 py-3">
                    {disciplina}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 bg-slate-900/70">
              {rowsFiltradas.map((row) => (
                <tr key={row.inscripcionId}>
                  <td className="px-4 py-3 font-semibold text-white">{row.nombre}</td>
                  <td className="px-4 py-3 text-slate-300">{row.club}</td>
                  <td className="px-4 py-3 text-slate-300">{row.categoria}</td>
                  <td className="px-4 py-3 text-slate-300">{row.estadoInscripcion}</td>
                  {disciplinasVisibles.map((disciplina) => {
                    if (!row.disciplinas.includes(disciplina)) {
                      return (
                        <td key={disciplina} className="px-4 py-3 text-slate-500">
                          No inscripto
                        </td>
                      )
                    }
                    const estado = row.estadoApPorDisciplina[disciplina]
                    return (
                      <td key={disciplina} className="px-4 py-3">
                        <EstadoAPBadge
                          estado={estado?.estado ?? 'pendiente'}
                          ap={estado?.ap}
                          unidad={estado?.unidad}
                        />
                      </td>
                    )
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
