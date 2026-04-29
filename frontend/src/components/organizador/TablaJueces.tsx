import type { UsuarioDto } from '../../api/identidad'
import type { DisciplinaTorneoDto } from '../../api/torneo'
import { JuezSelector } from './JuezSelector'

interface TablaJuecesProps {
  disciplinas: DisciplinaTorneoDto[]
  jueces: UsuarioDto[]
  savingDisciplina: string | null
  asignablePorDisciplina: Map<string, boolean>
  onAsignar: (disciplina: DisciplinaTorneoDto, juezId: string) => void
}

function juezEmail(jueces: UsuarioDto[], juezId: string | null) {
  if (!juezId) return 'Sin juez asignado'
  return jueces.find((juez) => juez.usuario_id === juezId)?.email ?? 'Juez no encontrado'
}

export function TablaJueces({
  disciplinas,
  jueces,
  savingDisciplina,
  asignablePorDisciplina,
  onAsignar,
}: TablaJuecesProps) {
  if (disciplinas.length === 0) {
    return (
      <div className="rounded-xl border border-slate-700 bg-slate-950/70 p-4 text-sm text-slate-300">
        No hay disciplinas asignadas al torneo.
      </div>
    )
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-700">
      <table className="min-w-full divide-y divide-slate-700 text-left text-sm">
        <thead className="bg-slate-950/80 text-xs font-semibold uppercase text-slate-400">
          <tr>
            <th className="px-4 py-3">Disciplina</th>
            <th className="px-4 py-3">Juez asignado</th>
            <th className="px-4 py-3">Asignacion</th>
            <th className="px-4 py-3">Estado</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800 bg-slate-900/70">
          {disciplinas.map((disciplina) => {
            const saving = savingDisciplina === disciplina.disciplina
            const puedeAsignar = asignablePorDisciplina.get(disciplina.disciplina) ?? false
            return (
              <tr key={disciplina.disciplina}>
                <td className="px-4 py-3 font-semibold text-white">
                  {disciplina.disciplina}
                </td>
                <td className="px-4 py-3 text-slate-300">
                  {juezEmail(jueces, disciplina.juez_id)}
                </td>
                <td className="min-w-64 px-4 py-3">
                  <JuezSelector
                    jueces={jueces}
                    value={disciplina.juez_id}
                    disabled={saving || jueces.length === 0 || !puedeAsignar}
                    onChange={(juezId) => onAsignar(disciplina, juezId)}
                  />
                </td>
                <td className="px-4 py-3 text-slate-300">
                  {saving
                    ? 'Guardando...'
                    : !puedeAsignar
                      ? `Falta generar la grilla de ${disciplina.disciplina} en la vista Grilla`
                      : disciplina.juez_id
                        ? 'Asignado'
                        : 'Pendiente'}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
