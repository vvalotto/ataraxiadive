import type { UsuarioDto } from '../../api/identidad'

interface JuezSelectorProps {
  jueces: UsuarioDto[]
  value: string | null
  disabled: boolean
  onChange: (juezId: string) => void
}

export function JuezSelector({ jueces, value, disabled, onChange }: JuezSelectorProps) {
  return (
    <select
      value={value ?? ''}
      disabled={disabled}
      onChange={(event) => {
        if (event.target.value) {
          onChange(event.target.value)
        }
      }}
      className="min-h-10 w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 disabled:cursor-not-allowed disabled:bg-slate-900 disabled:text-slate-500"
    >
      <option value="">Sin juez asignado</option>
      {jueces.map((juez) => (
        <option key={juez.usuario_id} value={juez.usuario_id}>
          {[juez.nombre, juez.apellido].filter(Boolean).join(' ').trim() || juez.email}
        </option>
      ))}
    </select>
  )
}
