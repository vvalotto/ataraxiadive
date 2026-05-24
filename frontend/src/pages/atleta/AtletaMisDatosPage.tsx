import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { AtletaShell } from '../../components/atleta/AtletaShell'
import { RolesSection } from '../../components/shared/RolesSection'
import {
  actualizarAtletaMe,
  fetchAtletaMe,
  ApiError,
  type AtletaDto,
} from '../../api/registro'

const CATEGORIAS = [
  { value: 'JUNIOR_MASCULINO', label: 'Junior Masculino' },
  { value: 'JUNIOR_FEMENINO', label: 'Junior Femenino' },
  { value: 'SENIOR_MASCULINO', label: 'Senior Masculino' },
  { value: 'SENIOR_FEMENINO', label: 'Senior Femenino' },
  { value: 'MASTER_MASCULINO', label: 'Master Masculino' },
  { value: 'MASTER_FEMENINO', label: 'Master Femenino' },
]

interface FormState {
  nombre: string
  apellido: string
  categoria: string
  club: string
  fecha_nacimiento: string
  brevet: string
  dni: string
  telefono: string
}

function inputClass(hasError = false): string {
  return [
    'mt-2 w-full rounded-xl border bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none transition placeholder:text-slate-500',
    hasError ? 'border-red-500/60 focus:border-red-400' : 'border-slate-700 focus:border-sky-400',
  ].join(' ')
}

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message
  if (error instanceof Error) return error.message
  return 'No se pudo completar la operación'
}

function toFormState(atleta: AtletaDto): FormState {
  return {
    nombre: atleta.nombre ?? '',
    apellido: atleta.apellido ?? '',
    categoria: atleta.categoria ?? '',
    club: atleta.club ?? '',
    fecha_nacimiento: atleta.fecha_nacimiento ?? '',
    brevet: atleta.brevet ?? '',
    dni: atleta.dni ?? '',
    telefono: atleta.telefono ?? '',
  }
}

export function AtletaMisDatosPage() {
  const [form, setForm] = useState<FormState>({
    nombre: '',
    apellido: '',
    categoria: '',
    club: '',
    fecha_nacimiento: '',
    brevet: '',
    dni: '',
    telefono: '',
  })
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    let cancelled = false

    async function load() {
      setIsLoading(true)
      try {
        const atleta = await fetchAtletaMe()
        if (!cancelled) setForm(toFormState(atleta))
      } catch (err) {
        if (!cancelled) setError(getErrorMessage(err))
      } finally {
        if (!cancelled) setIsLoading(false)
      }
    }

    void load()
    return () => {
      cancelled = true
    }
  }, [])

  function updateField(field: keyof FormState, value: string) {
    setForm((current) => ({ ...current, [field]: value }))
    setError(null)
    setSuccess(false)
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setIsSubmitting(true)
    setError(null)
    setSuccess(false)

    try {
      const updated = await actualizarAtletaMe({
        nombre: form.nombre.trim() || undefined,
        apellido: form.apellido.trim() || undefined,
        categoria: form.categoria || undefined,
        club: form.club.trim() || undefined,
        fecha_nacimiento: form.fecha_nacimiento || undefined,
        brevet: form.brevet.trim() || undefined,
        dni: form.dni.trim() || undefined,
        telefono: form.telefono.trim() || undefined,
      })
      setForm(toFormState(updated))
      setSuccess(true)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <AtletaShell title="Mis Datos" subtitle="Actualizá tu perfil de atleta">
      <RolesSection />
      {isLoading ? (
        <div className="rounded-2xl border border-slate-700 bg-slate-900/70 p-5 text-sm text-slate-300">
          Cargando perfil...
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
              Nombre
              <input
                value={form.nombre}
                onChange={(e) => updateField('nombre', e.target.value)}
                className={inputClass()}
                placeholder="Juan"
              />
            </label>

            <label className="block text-sm font-semibold text-slate-100">
              Apellido
              <input
                value={form.apellido}
                onChange={(e) => updateField('apellido', e.target.value)}
                className={inputClass()}
                placeholder="Pérez"
              />
            </label>

            <label className="block text-sm font-semibold text-slate-100">
              Fecha de nacimiento
              <input
                type="date"
                value={form.fecha_nacimiento}
                onChange={(e) => updateField('fecha_nacimiento', e.target.value)}
                className={inputClass()}
              />
            </label>

            <label className="block text-sm font-semibold text-slate-100">
              DNI <span className="ml-1 text-xs font-normal text-slate-400">(opcional)</span>
              <input
                value={form.dni}
                onChange={(e) => updateField('dni', e.target.value)}
                className={inputClass()}
                placeholder="12345678"
                inputMode="numeric"
              />
            </label>

            <label className="block text-sm font-semibold text-slate-100">
              Teléfono <span className="ml-1 text-xs font-normal text-slate-400">(opcional)</span>
              <input
                value={form.telefono}
                onChange={(e) => updateField('telefono', e.target.value)}
                className={inputClass()}
                placeholder="1123456789"
                inputMode="tel"
              />
            </label>

            <label className="block text-sm font-semibold text-slate-100">
              Categoría
              <select
                value={form.categoria}
                onChange={(e) => updateField('categoria', e.target.value)}
                className={inputClass()}
              >
                <option value="">Seleccionar categoría</option>
                {CATEGORIAS.map((cat) => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </label>

            <label className="block text-sm font-semibold text-slate-100">
              Club
              <input
                value={form.club}
                onChange={(e) => updateField('club', e.target.value)}
                className={inputClass()}
                placeholder="Club Atlético"
              />
            </label>

            <label className="block text-sm font-semibold text-slate-100">
              Brevet
              <input
                value={form.brevet}
                onChange={(e) => updateField('brevet', e.target.value)}
                className={inputClass()}
                placeholder="Número de brevet (opcional)"
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
    </AtletaShell>
  )
}
