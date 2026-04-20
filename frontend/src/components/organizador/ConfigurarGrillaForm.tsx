import { useState } from 'react'

interface ConfigurarGrillaFormProps {
  disciplina: string
  isSubmitting: boolean
  onSubmit: (payload: { intervaloMinutos: number; primerOt: string }) => void
}

export function ConfigurarGrillaForm({
  disciplina,
  isSubmitting,
  onSubmit,
}: ConfigurarGrillaFormProps) {
  const [intervaloMinutos, setIntervaloMinutos] = useState('8')
  const [primerOt, setPrimerOt] = useState('09:00')
  const [error, setError] = useState('')

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const intervalo = Number(intervaloMinutos)
    if (!Number.isInteger(intervalo) || intervalo <= 0) {
      setError('El intervalo OT debe ser mayor a cero.')
      return
    }
    if (!primerOt) {
      setError('El primer OT es obligatorio.')
      return
    }
    setError('')
    onSubmit({ intervaloMinutos: intervalo, primerOt })
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="grid gap-4 rounded-lg border border-stone-200 bg-stone-50 p-4 sm:grid-cols-[1fr_1fr_auto]"
    >
      <label className="text-sm font-semibold text-stone-900">
        Intervalo OT
        <input
          type="number"
          min="1"
          step="1"
          value={intervaloMinutos}
          onChange={(event) => setIntervaloMinutos(event.target.value)}
          className="mt-2 min-h-10 w-full rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm"
        />
      </label>
      <label className="text-sm font-semibold text-stone-900">
        Primer OT
        <input
          type="time"
          value={primerOt}
          onChange={(event) => setPrimerOt(event.target.value)}
          className="mt-2 min-h-10 w-full rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm"
        />
      </label>
      <button
        type="submit"
        disabled={isSubmitting || !disciplina}
        className="min-h-10 self-end rounded-lg bg-stone-900 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-stone-300"
      >
        {isSubmitting ? 'Generando...' : 'Generar grilla'}
      </button>
      {error ? <p className="text-sm text-red-700 sm:col-span-3">{error}</p> : null}
    </form>
  )
}
