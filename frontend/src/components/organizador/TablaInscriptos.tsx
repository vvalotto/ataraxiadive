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
      <div className="rounded-lg border border-stone-200 bg-stone-50 p-4 text-sm text-stone-600">
        Todavia no hay inscriptos para este torneo
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-stone-600">{rows.length} atletas inscriptos</p>
        <label className="text-sm font-semibold text-stone-900">
          Disciplina
          <select
            value={disciplinaFiltro}
            onChange={(event) => setDisciplinaFiltro(event.target.value)}
            className="ml-0 mt-2 min-h-10 rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm sm:ml-3 sm:mt-0"
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
        <div className="rounded-lg border border-stone-200 bg-stone-50 p-4 text-sm text-stone-600">
          No hay atletas inscriptos en la disciplina seleccionada
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-stone-200">
          <table className="min-w-full divide-y divide-stone-200 text-left text-sm">
            <thead className="bg-stone-50 text-xs font-semibold uppercase text-stone-500">
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
            <tbody className="divide-y divide-stone-200 bg-white">
              {rowsFiltradas.map((row) => (
                <tr key={row.inscripcionId}>
                  <td className="px-4 py-3 font-semibold text-stone-950">{row.nombre}</td>
                  <td className="px-4 py-3 text-stone-700">{row.club}</td>
                  <td className="px-4 py-3 text-stone-700">{row.categoria}</td>
                  <td className="px-4 py-3 text-stone-700">{row.estadoInscripcion}</td>
                  {disciplinasVisibles.map((disciplina) => {
                    if (!row.disciplinas.includes(disciplina)) {
                      return (
                        <td key={disciplina} className="px-4 py-3 text-stone-400">
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
