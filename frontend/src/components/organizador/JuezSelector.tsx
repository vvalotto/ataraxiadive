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
      className="min-h-10 w-full rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm text-stone-900 disabled:cursor-not-allowed disabled:bg-stone-100 disabled:text-stone-500"
    >
      <option value="">Sin juez asignado</option>
      {jueces.map((juez) => (
        <option key={juez.usuario_id} value={juez.usuario_id}>
          {juez.email}
        </option>
      ))}
    </select>
  )
}
