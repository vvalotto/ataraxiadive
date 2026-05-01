import { useState } from 'react'

interface ConfigurarGrillaFormProps {
  disciplina: string
  isSubmitting: boolean
  requiresIntervalo?: boolean
  fechaInicioTorneo?: string
  fechaFinTorneo?: string
  submitLabel?: string
  submittingLabel?: string
  onSubmit: (payload: {
    fechaOt: string
    primerOt: string
    intervaloMinutos: number | null
    andariveles: number
  }) => void
}

export function ConfigurarGrillaForm({
  disciplina,
  isSubmitting,
  requiresIntervalo = false,
  fechaInicioTorneo,
  fechaFinTorneo,
  submitLabel = 'Generar grilla',
  submittingLabel = 'Generando...',
  onSubmit,
}: ConfigurarGrillaFormProps) {
  const [intervaloMinutos, setIntervaloMinutos] = useState('8')
  const [andariveles, setAndariveles] = useState('1')
  const defaultFechaOt = fechaInicioTorneo?.slice(0, 10) ?? ''
  const defaultPrimerOt = (() => {
    if (!fechaInicioTorneo) return '09:00'
    const parsed = new Date(fechaInicioTorneo)
    if (Number.isNaN(parsed.getTime())) return '09:00'
    return new Intl.DateTimeFormat('en-GB', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
      timeZone: 'UTC',
    }).format(parsed)
  })()
  const [fechaOt, setFechaOt] = useState(defaultFechaOt)
  const [primerOt, setPrimerOt] = useState(defaultPrimerOt)
  const [error, setError] = useState('')

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    let intervalo: number | null = null
    if (requiresIntervalo) {
      intervalo = Number(intervaloMinutos)
      if (!Number.isInteger(intervalo) || intervalo <= 0) {
        setError('El intervalo OT debe ser mayor a cero.')
        return
      }
    }
    const andarivelesValue = Number(andariveles)
    if (!Number.isInteger(andarivelesValue) || andarivelesValue <= 0) {
      setError('La cantidad de andariveles debe ser mayor a cero.')
      return
    }
    if (!primerOt) {
      setError('El primer OT es obligatorio.')
      return
    }
    if (!fechaOt) {
      setError('La fecha del primer OT es obligatoria.')
      return
    }
    const fechaMin = fechaInicioTorneo?.slice(0, 10)
    const fechaMax = fechaFinTorneo?.slice(0, 10)
    if ((fechaMin && fechaOt < fechaMin) || (fechaMax && fechaOt > fechaMax)) {
      setError('La fecha del primer OT debe estar dentro del rango del torneo.')
      return
    }
    setError('')
    onSubmit({ fechaOt, primerOt, intervaloMinutos: intervalo, andariveles: andarivelesValue })
  }

  return (
    <form
      onSubmit={handleSubmit}
      className={`grid gap-4 rounded-[1.25rem] border border-slate-700 bg-slate-950/70 p-4 ${
        requiresIntervalo
          ? 'sm:grid-cols-[1fr_1fr_1fr_1fr_auto]'
          : 'sm:grid-cols-[1fr_1fr_1fr_auto]'
      }`}
    >
      {requiresIntervalo ? (
        <label className="text-sm font-semibold text-slate-200">
          Intervalo OT
          <input
            type="number"
            min="1"
            step="1"
            value={intervaloMinutos}
            onChange={(event) => setIntervaloMinutos(event.target.value)}
            className="mt-2 min-h-10 w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white outline-none transition focus:border-sky-400"
          />
        </label>
      ) : null}
      <label className="text-sm font-semibold text-slate-200">
        Andariveles
        <input
          type="number"
          min="1"
          step="1"
          value={andariveles}
          onChange={(event) => setAndariveles(event.target.value)}
          className="mt-2 min-h-10 w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white outline-none transition focus:border-sky-400"
        />
      </label>
      <label className="text-sm font-semibold text-slate-200">
        Fecha
        <input
          type="date"
          value={fechaOt}
          min={fechaInicioTorneo?.slice(0, 10)}
          max={fechaFinTorneo?.slice(0, 10)}
          onChange={(event) => setFechaOt(event.target.value)}
          className="mt-2 min-h-10 w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white outline-none transition focus:border-sky-400"
        />
      </label>
      <label className="text-sm font-semibold text-slate-200">
        Primer OT
        <input
          type="time"
          value={primerOt}
          onChange={(event) => setPrimerOt(event.target.value)}
          className="mt-2 min-h-10 w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white outline-none transition focus:border-sky-400"
        />
      </label>
      <button
        type="submit"
        disabled={isSubmitting || !disciplina}
        className="min-h-10 self-end rounded-xl bg-sky-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-sky-400 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
      >
        {isSubmitting ? submittingLabel : submitLabel}
      </button>
      {error ? (
        <p className={`text-sm text-red-300 ${requiresIntervalo ? 'sm:col-span-5' : 'sm:col-span-4'}`}>
          {error}
        </p>
      ) : null}
    </form>
  )
}
