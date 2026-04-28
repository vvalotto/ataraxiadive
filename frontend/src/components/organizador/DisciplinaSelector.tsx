import type { DisciplinaCodigo } from '../../api/torneo'

interface DisciplinaOption {
  value: DisciplinaCodigo
  label: string
  detail: string
}

const DISCIPLINAS: DisciplinaOption[] = [
  { value: 'STA', label: 'STA', detail: 'Apnea estatica' },
  { value: 'DNF', label: 'DNF', detail: 'Dinamica sin aletas' },
  { value: 'DYN', label: 'DYN', detail: 'Dinamica con aletas' },
  { value: 'DBF', label: 'DBF', detail: 'Dinamica bi-fins' },
  { value: 'SPE_2X50', label: 'SPE 2x50', detail: 'Speed endurance' },
  { value: 'SPE_4X50', label: 'SPE 4x50', detail: 'Speed endurance' },
  { value: 'SPE_8X50', label: 'SPE 8x50', detail: 'Speed endurance' },
  { value: 'SPE_16X50', label: 'SPE 16x50', detail: 'Speed endurance' },
]

interface DisciplinaSelectorProps {
  value: DisciplinaCodigo[]
  onChange: (value: DisciplinaCodigo[]) => void
  error?: string
}

export function DisciplinaSelector({ value, onChange, error }: DisciplinaSelectorProps) {
  function toggleDisciplina(disciplina: DisciplinaCodigo) {
    if (value.includes(disciplina)) {
      onChange(value.filter((item) => item !== disciplina))
      return
    }
    onChange([...value, disciplina])
  }

  return (
    <fieldset className="space-y-3">
      <legend className="text-sm font-semibold text-slate-100">Disciplinas</legend>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {DISCIPLINAS.map((disciplina) => {
          const checked = value.includes(disciplina.value)
          return (
            <label
              key={disciplina.value}
              className={[
                'flex min-h-24 cursor-pointer items-start gap-3 rounded-lg border p-4 transition',
                checked
                  ? 'border-sky-400 bg-sky-400/10 text-sky-100'
                  : 'border-slate-700 bg-slate-900/80 text-slate-200 hover:border-slate-500',
              ].join(' ')}
            >
              <input
                type="checkbox"
                checked={checked}
                onChange={() => toggleDisciplina(disciplina.value)}
                className="mt-1 h-4 w-4 accent-sky-400"
              />
              <span>
                <span className="block text-sm font-semibold">{disciplina.label}</span>
                <span className="mt-1 block text-xs text-slate-400">{disciplina.detail}</span>
              </span>
            </label>
          )
        })}
      </div>
      {error ? <p className="text-sm text-red-300">{error}</p> : null}
    </fieldset>
  )
}
