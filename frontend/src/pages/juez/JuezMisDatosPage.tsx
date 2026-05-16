import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { JuezLayout } from '../../components/juez/JuezLayout'
import { actualizarJuezMe, crearJuezMe, fetchJuezMe, ApiError } from '../../api/registro'

interface FormState {
  numero_licencia: string
  federacion: string
}

function inputClass(): string {
  return 'mt-2 w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-sky-400'
}

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message
  if (error instanceof Error) return error.message
  return 'No se pudo completar la operación'
}

export function JuezMisDatosPage() {
  const [perfilExiste, setPerfilExiste] = useState<boolean | null>(null)
  const [form, setForm] = useState<FormState>({ numero_licencia: '', federacion: '' })
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    let cancelled = false
    async function load() {
      setIsLoading(true)
      try {
        const juez = await fetchJuezMe()
        if (!cancelled) {
          if (juez) {
            setPerfilExiste(true)
            setForm({
              numero_licencia: juez.numero_licencia ?? '',
              federacion: juez.federacion ?? '',
            })
          } else {
            setPerfilExiste(false)
          }
        }
      } catch (err) {
        if (!cancelled) setError(getErrorMessage(err))
      } finally {
        if (!cancelled) setIsLoading(false)
      }
    }
    void load()
    return () => { cancelled = true }
  }, [])

  function updateField(field: keyof FormState, value: string) {
    setForm((current) => ({ ...current, [field]: value }))
    setError(null)
    setSuccess(false)
  }

  async function handleCrear() {
    setIsSubmitting(true)
    setError(null)
    try {
      const juez = await crearJuezMe()
      setPerfilExiste(true)
      setForm({ numero_licencia: juez.numero_licencia ?? '', federacion: juez.federacion ?? '' })
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setIsSubmitting(true)
    setError(null)
    setSuccess(false)
    try {
      const updated = await actualizarJuezMe({
        numero_licencia: form.numero_licencia.trim() || undefined,
        federacion: form.federacion.trim() || undefined,
      })
      setForm({
        numero_licencia: updated.numero_licencia ?? '',
        federacion: updated.federacion ?? '',
      })
      setSuccess(true)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <JuezLayout title="Mis Datos" subtitle="Perfil de juez">
      {isLoading ? (
        <div className="rounded-2xl border border-slate-700 bg-slate-900/70 p-5 text-sm text-slate-300">
          Cargando perfil...
        </div>
      ) : perfilExiste === false ? (
        <div className="rounded-2xl border border-slate-700 bg-slate-900/85 p-5 shadow-lg">
          <p className="mb-4 text-sm text-slate-400">
            Todavía no tenés un perfil de juez. Crealo para agregar tu licencia y federación.
          </p>
          {error ? (
            <div className="mb-4 rounded-xl border border-red-500/40 bg-red-950/40 p-3 text-sm text-red-200">
              {error}
            </div>
          ) : null}
          <button
            onClick={() => void handleCrear()}
            disabled={isSubmitting}
            className="w-full rounded-full bg-sky-500 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-slate-950 disabled:cursor-not-allowed disabled:bg-slate-600 disabled:text-slate-300"
          >
            {isSubmitting ? 'Creando...' : 'Crear mi perfil de juez'}
          </button>
        </div>
      ) : (
        <form
          onSubmit={handleSubmit}
          className="rounded-2xl border border-slate-700 bg-slate-900/85 p-5 shadow-lg"
        >
          {success ? (
            <div className="mb-4 rounded-xl border border-emerald-500/40 bg-emerald-950/40 p-3 text-sm text-emerald-200">
              Datos actualizados correctamente.
            </div>
          ) : null}
          {error ? (
            <div className="mb-4 rounded-xl border border-red-500/40 bg-red-950/40 p-3 text-sm text-red-200">
              {error}
            </div>
          ) : null}
          <div className="grid gap-4">
            <label className="block text-sm font-semibold text-slate-100">
              Número de licencia <span className="ml-1 text-xs font-normal text-slate-400">(opcional)</span>
              <input
                value={form.numero_licencia}
                onChange={(e) => updateField('numero_licencia', e.target.value)}
                className={inputClass()}
                placeholder="LIC-001"
              />
            </label>
            <label className="block text-sm font-semibold text-slate-100">
              Federación <span className="ml-1 text-xs font-normal text-slate-400">(opcional)</span>
              <input
                value={form.federacion}
                onChange={(e) => updateField('federacion', e.target.value)}
                className={inputClass()}
                placeholder="AIDA, CMAS..."
              />
            </label>
          </div>
          <div className="mt-5">
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full rounded-full bg-sky-500 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-slate-950 disabled:cursor-not-allowed disabled:bg-slate-600 disabled:text-slate-300"
            >
              {isSubmitting ? 'Guardando...' : 'Guardar cambios'}
            </button>
          </div>
        </form>
      )}
    </JuezLayout>
  )
}
