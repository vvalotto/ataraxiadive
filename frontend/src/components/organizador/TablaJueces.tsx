import type { UsuarioDto } from '../../api/identidad'
import type { DisciplinaTorneoDto } from '../../api/torneo'
import { JuezSelector } from './JuezSelector'

interface TablaJuecesProps {
  disciplinas: DisciplinaTorneoDto[]
  jueces: UsuarioDto[]
  savingDisciplina: string | null
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
  onAsignar,
}: TablaJuecesProps) {
  if (disciplinas.length === 0) {
    return (
      <div className="rounded-lg border border-stone-200 bg-stone-50 p-4 text-sm text-stone-600">
        No hay disciplinas asignadas al torneo.
      </div>
    )
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-stone-200">
      <table className="min-w-full divide-y divide-stone-200 text-left text-sm">
        <thead className="bg-stone-50 text-xs font-semibold uppercase text-stone-500">
          <tr>
            <th className="px-4 py-3">Disciplina</th>
            <th className="px-4 py-3">Juez asignado</th>
            <th className="px-4 py-3">Asignacion</th>
            <th className="px-4 py-3">Estado</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-stone-200 bg-white">
          {disciplinas.map((disciplina) => {
            const saving = savingDisciplina === disciplina.disciplina
            return (
              <tr key={disciplina.disciplina}>
                <td className="px-4 py-3 font-semibold text-stone-950">
                  {disciplina.disciplina}
                </td>
                <td className="px-4 py-3 text-stone-700">
                  {juezEmail(jueces, disciplina.juez_id)}
                </td>
                <td className="min-w-64 px-4 py-3">
                  <JuezSelector
                    jueces={jueces}
                    value={disciplina.juez_id}
                    disabled={saving || jueces.length === 0}
                    onChange={(juezId) => onAsignar(disciplina, juezId)}
                  />
                </td>
                <td className="px-4 py-3 text-stone-700">
                  {saving ? 'Guardando...' : disciplina.juez_id ? 'Asignado' : 'Pendiente'}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
