const reasonLabels: Record<string, string> = {
  BKO_SUPERFICIE: 'Black-out en superficie',
  BKO_SUBACUATICO: 'Black-out subacuatico',
  PROTOCOLO_SUPERFICIE: 'No siguio protocolo de superficie',
  INFRACCION_TECNICA_DQ: 'Infraccion tecnica',
  NO_INICIO_EN_VENTANA: 'No inicio en ventana',
  SALIDA_EN_FALSO: 'Salida en falso',
}

interface MotivoDqSelectorProps {
  value: string
  options: readonly string[]
  onChange: (value: string) => void
}

export function MotivoDqSelector({ value, options, onChange }: MotivoDqSelectorProps) {
  return (
    <div className="space-y-3 rounded-2xl bg-slate-950/70 p-4">
      <label className="block text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
        Motivo DQ
      </label>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="w-full rounded-2xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-white"
      >
        <option value="">Seleccionar</option>
        {options.map((reason) => (
          <option key={reason} value={reason}>
            {reasonLabels[reason] ?? reason}
          </option>
        ))}
      </select>
    </div>
  )
}
