import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  ApiError,
  asignarDisciplinas,
  crearTorneo,
  type CrearTorneoPayload,
  type DisciplinaCodigo,
} from '../../api/torneo'
import { DisciplinaSelector } from '../../components/organizador/DisciplinaSelector'
import { OrganizadorLayout } from '../../components/organizador/OrganizadorLayout'

interface FormState {
  nombre: string
  descripcion: string
  fechaInicio: string
  fechaFin: string
  sedeNombre: string
  sedeCiudad: string
  sedePais: string
  entidadNombre: string
  entidadTipo: string
}

type FormErrors = Partial<Record<keyof FormState | 'disciplinas' | 'general', string>>

const INITIAL_FORM: FormState = {
  nombre: '',
  descripcion: '',
  fechaInicio: '',
  fechaFin: '',
  sedeNombre: '',
  sedeCiudad: '',
  sedePais: 'Argentina',
  entidadNombre: '',
  entidadTipo: '',
}

function inputClass(hasError: boolean): string {
  return [
    'mt-2 w-full rounded-lg border bg-white px-3 py-2 text-sm text-stone-900 outline-none transition',
    hasError ? 'border-red-400 focus:border-red-600' : 'border-stone-300 focus:border-emerald-700',
  ].join(' ')
}

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message
  if (error instanceof Error) return error.message
  return 'No se pudo completar la operacion'
}

export function CrearTorneoPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState<FormState>(INITIAL_FORM)
  const [disciplinas, setDisciplinas] = useState<DisciplinaCodigo[]>([])
  const [errors, setErrors] = useState<FormErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [torneoCreadoSinDisciplinas, setTorneoCreadoSinDisciplinas] = useState<string | null>(null)

  function updateField(field: keyof FormState, value: string) {
    setForm((current) => ({ ...current, [field]: value }))
    setErrors((current) => ({ ...current, [field]: undefined, general: undefined }))
  }

  function validate(): FormErrors {
    const nextErrors: FormErrors = {}
    if (!form.nombre.trim()) {
      nextErrors.nombre = 'El nombre es obligatorio'
    }
    if (form.fechaInicio && form.fechaFin && form.fechaFin < form.fechaInicio) {
      nextErrors.fechaFin = 'La fecha de fin debe ser igual o posterior a la de inicio'
    }
    if (disciplinas.length === 0) {
      nextErrors.disciplinas = 'Selecciona al menos una disciplina'
    }
    return nextErrors
  }

  function buildPayload(): CrearTorneoPayload {
    return {
      nombre: form.nombre.trim(),
      descripcion: form.descripcion.trim(),
      fecha_inicio: form.fechaInicio,
      fecha_fin: form.fechaFin,
      sede: {
        nombre: form.sedeNombre.trim(),
        ciudad: form.sedeCiudad.trim(),
        pais: form.sedePais.trim(),
      },
      entidad_organizadora: {
        nombre: form.entidadNombre.trim(),
        tipo: form.entidadTipo.trim(),
      },
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const validationErrors = validate()
    setErrors(validationErrors)
    setTorneoCreadoSinDisciplinas(null)

    if (Object.keys(validationErrors).length > 0) {
      return
    }

    setIsSubmitting(true)
    try {
      const response = await crearTorneo(buildPayload())
      try {
        await asignarDisciplinas(response.torneo_id, disciplinas)
      } catch (error) {
        setTorneoCreadoSinDisciplinas(response.torneo_id)
        setErrors({ general: `Torneo creado sin disciplinas: ${getErrorMessage(error)}` })
        return
      }
      navigate(`/organizador/panel?torneo_id=${response.torneo_id}`)
    } catch (error) {
      setErrors({ general: getErrorMessage(error) })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <OrganizadorLayout
      title="Nuevo torneo"
      subtitle="Alta del torneo y configuracion inicial de disciplinas"
      actions={
        <Link
          to="/organizador/torneo"
          className="rounded-lg border border-stone-900 px-4 py-2 text-sm font-semibold text-stone-900"
        >
          Volver
        </Link>
      }
    >
      <form
        onSubmit={handleSubmit}
        className="rounded-lg border border-stone-300 bg-white p-5 shadow-[0_20px_60px_rgba(120,93,54,0.08)]"
      >
        {errors.general ? (
          <div className="mb-5 rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-900">
            <p>{errors.general}</p>
            {torneoCreadoSinDisciplinas ? (
              <Link
                to={`/organizador/torneo/${torneoCreadoSinDisciplinas}`}
                className="mt-3 inline-flex rounded-lg border border-red-800 px-3 py-2 text-sm font-semibold text-red-900"
              >
                Ir al detalle del torneo
              </Link>
            ) : null}
          </div>
        ) : null}

        <div className="grid gap-5 lg:grid-cols-2">
          <label className="block text-sm font-semibold text-stone-900">
            Nombre
            <input
              value={form.nombre}
              onChange={(event) => updateField('nombre', event.target.value)}
              className={inputClass(Boolean(errors.nombre))}
              placeholder="BA 2026"
            />
            {errors.nombre ? <span className="mt-1 block text-sm text-red-700">{errors.nombre}</span> : null}
          </label>

          <label className="block text-sm font-semibold text-stone-900">
            Descripcion
            <input
              value={form.descripcion}
              onChange={(event) => updateField('descripcion', event.target.value)}
              className={inputClass(Boolean(errors.descripcion))}
              placeholder="Torneo nacional indoor"
            />
          </label>

          <label className="block text-sm font-semibold text-stone-900">
            Fecha de inicio
            <input
              type="date"
              value={form.fechaInicio}
              onChange={(event) => updateField('fechaInicio', event.target.value)}
              className={inputClass(Boolean(errors.fechaInicio))}
              required
            />
          </label>

          <label className="block text-sm font-semibold text-stone-900">
            Fecha de fin
            <input
              type="date"
              value={form.fechaFin}
              onChange={(event) => updateField('fechaFin', event.target.value)}
              className={inputClass(Boolean(errors.fechaFin))}
              required
            />
            {errors.fechaFin ? (
              <span className="mt-1 block text-sm text-red-700">{errors.fechaFin}</span>
            ) : null}
          </label>
        </div>

        <div className="mt-6 grid gap-5 lg:grid-cols-3">
          <label className="block text-sm font-semibold text-stone-900">
            Sede
            <input
              value={form.sedeNombre}
              onChange={(event) => updateField('sedeNombre', event.target.value)}
              className={inputClass(Boolean(errors.sedeNombre))}
              placeholder="Club Nautico"
              required
            />
          </label>

          <label className="block text-sm font-semibold text-stone-900">
            Ciudad
            <input
              value={form.sedeCiudad}
              onChange={(event) => updateField('sedeCiudad', event.target.value)}
              className={inputClass(Boolean(errors.sedeCiudad))}
              placeholder="Buenos Aires"
              required
            />
          </label>

          <label className="block text-sm font-semibold text-stone-900">
            Pais
            <input
              value={form.sedePais}
              onChange={(event) => updateField('sedePais', event.target.value)}
              className={inputClass(Boolean(errors.sedePais))}
              required
            />
          </label>
        </div>

        <div className="mt-6 grid gap-5 lg:grid-cols-2">
          <label className="block text-sm font-semibold text-stone-900">
            Entidad organizadora
            <input
              value={form.entidadNombre}
              onChange={(event) => updateField('entidadNombre', event.target.value)}
              className={inputClass(Boolean(errors.entidadNombre))}
              placeholder="FAAS"
              required
            />
          </label>

          <label className="block text-sm font-semibold text-stone-900">
            Tipo de entidad
            <input
              value={form.entidadTipo}
              onChange={(event) => updateField('entidadTipo', event.target.value)}
              className={inputClass(Boolean(errors.entidadTipo))}
              placeholder="Federacion"
              required
            />
          </label>
        </div>

        <div className="mt-6">
          <DisciplinaSelector
            value={disciplinas}
            onChange={(nextValue) => {
              setDisciplinas(nextValue)
              setErrors((current) => ({ ...current, disciplinas: undefined, general: undefined }))
            }}
            error={errors.disciplinas}
          />
        </div>

        <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-end">
          <Link
            to="/organizador/torneo"
            className="rounded-lg border border-stone-300 px-4 py-2 text-center text-sm font-semibold text-stone-800"
          >
            Cancelar
          </Link>
          <button
            type="submit"
            disabled={isSubmitting}
            className="rounded-lg bg-stone-900 px-5 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-stone-500"
          >
            {isSubmitting ? 'Creando...' : 'Crear Torneo'}
          </button>
        </div>
      </form>
    </OrganizadorLayout>
  )
}
