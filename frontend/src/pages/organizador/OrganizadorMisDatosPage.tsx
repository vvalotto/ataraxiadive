import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { useSearchParams } from 'react-router-dom'
import { OrganizadorLayout } from '../../components/organizador/OrganizadorLayout'
import { RolesSection } from '../../components/shared/RolesSection'
import {
  actualizarOrganizadorMe,
  crearOrganizadorMe,
  fetchOrganizadorMe,
  ApiError,
} from '../../api/registro'

interface FormState {
  nombre_organizacion: string
}

function inputClass(): string {
  return 'mt-2 w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-sky-400'
}

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message
  if (error instanceof Error) return error.message
  return 'No se pudo completar la operación'
}

export function OrganizadorMisDatosPage() {
  const [searchParams] = useSearchParams()
  const torneoId = searchParams.get('torneo_id')
  const [perfilExiste, setPerfilExiste] = useState<boolean | null>(null)
  const [form, setForm] = useState<FormState>({ nombre_organizacion: '' })
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    let cancelled = false
    async function load() {
      setIsLoading(true)
      try {
        const org = await fetchOrganizadorMe()
        if (!cancelled) {
          if (org) {
            setPerfilExiste(true)
            setForm({ nombre_organizacion: org.nombre_organizacion ?? '' })
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
      const org = await crearOrganizadorMe()
      setPerfilExiste(true)
      setForm({ nombre_organizacion: org.nombre_organizacion ?? '' })
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
      const updated = await actualizarOrganizadorMe({
        nombre_organizacion: form.nombre_organizacion.trim() || undefined,
      })
      setForm({ nombre_organizacion: updated.nombre_organizacion ?? '' })
      setSuccess(true)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <OrganizadorLayout
      title="Mis Datos"
      subtitle="Perfil de organizador"
      showTournamentNavigation={true}
      activeTournamentId={torneoId ?? undefined}
    >
      <RolesSection />
      {isLoading ? (
        <div className="rounded-2xl border border-slate-700 bg-slate-900/70 p-5 text-sm text-slate-300">
          Cargando perfil...
        </div>
      ) : perfilExiste === false ? (
        <div className="rounded-2xl border border-slate-700 bg-slate-900/85 p-5 shadow-lg max-w-md">
          <p className="mb-4 text-sm text-slate-400">
            Todavía no tenés un perfil de organizador. Crealo para agregar el nombre de tu organización.
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
            {isSubmitting ? 'Creando...' : 'Crear mi perfil de organizador'}
          </button>
        </div>
      ) : (
        <form
          onSubmit={handleSubmit}
          className="rounded-2xl border border-slate-700 bg-slate-900/85 p-5 shadow-lg max-w-md"
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
              Nombre de organización <span className="ml-1 text-xs font-normal text-slate-400">(opcional)</span>
              <input
                value={form.nombre_organizacion}
                onChange={(e) => updateField('nombre_organizacion', e.target.value)}
                className={inputClass()}
                placeholder="Club Apnea BA"
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
    </OrganizadorLayout>
  )
}
