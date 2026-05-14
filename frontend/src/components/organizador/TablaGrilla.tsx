import { useState } from 'react'
import type { CambioGrillaPayload, GrillaAtletaDto } from '../../api/competencia'
import { formatMarca } from '../../utils/marca'

interface TablaGrillaProps {
  rows: GrillaAtletaDto[]
  readOnly: boolean
  isSaving: boolean
  onReorder: (rows: GrillaAtletaDto[], cambios: CambioGrillaPayload[]) => void
}

function formatOt(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value.slice(0, 5)
  }
  return new Intl.DateTimeFormat('es-AR', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).format(date)
}

function moveRow(rows: GrillaAtletaDto[], fromIndex: number, toIndex: number) {
  const next = [...rows]
  const [moved] = next.splice(fromIndex, 1)
  next.splice(toIndex, 0, moved)
  return next.map((row, index) => ({ ...row, posicion: index + 1 }))
}

export function TablaGrilla({ rows, readOnly, isSaving, onReorder }: TablaGrillaProps) {
  const [draggedId, setDraggedId] = useState<string | null>(null)
  const [overId, setOverId] = useState<string | null>(null)

  function handleDrop(targetId: string) {
    if (readOnly || !draggedId || draggedId === targetId) {
      setDraggedId(null)
      setOverId(null)
      return
    }

    const fromIndex = rows.findIndex((row) => row.performance_id === draggedId)
    const toIndex = rows.findIndex((row) => row.performance_id === targetId)
    if (fromIndex < 0 || toIndex < 0) return

    const reordered = moveRow(rows, fromIndex, toIndex)
    const cambios = reordered
      .filter((row) => rows.find((original) => original.performance_id === row.performance_id)?.posicion !== row.posicion)
      .map((row) => ({
        performance_id: row.performance_id,
        campo: 'posicion_grilla' as const,
        valor_nuevo: row.posicion,
      }))

    setDraggedId(null)
    setOverId(null)
    if (cambios.length > 0) {
      onReorder(reordered, cambios)
    }
  }

  if (rows.length === 0) {
    return (
      <div className="rounded-xl border border-slate-700 bg-slate-950/70 p-4 text-sm text-slate-300">
        No hay atletas en la grilla de esta disciplina.
      </div>
    )
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-700">
      <table className="min-w-full divide-y divide-slate-700 text-left text-sm">
        <thead className="bg-slate-950/80 text-xs font-semibold uppercase text-slate-400">
          <tr>
            <th className="px-4 py-3">Posicion</th>
            <th className="px-4 py-3">Atleta</th>
            <th className="px-4 py-3 text-center">Anuncio</th>
            <th className="px-4 py-3 text-center">Andarivel</th>
            <th className="px-4 py-3 text-center">OT</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800 bg-slate-900/70">
          {rows.map((row) => (
            <tr
              key={row.performance_id}
              draggable={!readOnly && !isSaving}
              onDragStart={() => setDraggedId(row.performance_id)}
              onDragOver={(event) => {
                if (!readOnly) {
                  event.preventDefault()
                  setOverId(row.performance_id)
                }
              }}
              onDragLeave={() => setOverId(null)}
              onDrop={() => handleDrop(row.performance_id)}
              className={[
                !readOnly ? 'cursor-grab active:cursor-grabbing' : '',
                overId === row.performance_id ? 'bg-emerald-500/10' : '',
              ].join(' ')}
            >
              <td className="px-4 py-3 font-semibold text-white">{row.posicion}</td>
              <td className="px-4 py-3 text-slate-100">{row.nombre_atleta}</td>
              <td className="px-4 py-3 text-center text-slate-300">
                {formatMarca(row.ap_declarado, row.unidad)}
              </td>
              <td className="px-4 py-3 text-center text-slate-300">{row.andarivel}</td>
              <td className="px-4 py-3 text-center font-semibold text-slate-100">
                {formatOt(row.ot_programado)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
