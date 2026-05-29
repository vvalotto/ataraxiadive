import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import {
  ApiError,
  actualizarTorneo,
  asignarDisciplinas,
  crearTorneo,
  fetchTorneo,
  listarDisciplinasTorneo,
  type ActualizarTorneoPayload,
  type CrearTorneoPayload,
  type DisciplinaCodigo,
  type GrupoEtario,
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

type FormErrors = Partial<Record<keyof FormState | 'disciplinas' | 'gruposEtarios' | 'general', string>>

const GRUPOS_ETARIOS: GrupoEtario[] = ['JUNIOR', 'SENIOR', 'MASTER']

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

function inputClass(hasError: boolean, disabled = false): string {
  return [
    'mt-2 w-full rounded-lg border bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none transition placeholder:text-slate-500',
    disabled ? 'cursor-not-allowed opacity-50' : '',
    hasError
      ? 'border-red-500/60 focus:border-red-400'
      : 'border-slate-700 focus:border-sky-400',
  ]
    .filter(Boolean)
    .join(' ')
}

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message
  if (error instanceof Error) return error.message
  return 'No se pudo completar la operacion'
}

type PageMode = 'crear' | 'editar-disciplinas' | 'editar-torneo'

function detectMode(pathname: string, torneoId: string | undefined): PageMode {
  if (!torneoId) return 'crear'
  if (pathname.endsWith('/editar')) return 'editar-torneo'
  return 'editar-disciplinas'
}

export function CrearTorneoPage() {
  const navigate = useNavigate()
  const { torneoId } = useParams<{ torneoId: string }>()
  const mode = detectMode(window.location.pathname, torneoId)
  const isEditing = mode !== 'crear'
  const isEditingDisciplinas = mode === 'editar-disciplinas'
  const isEditingTorneo = mode === 'editar-torneo'

  const [form, setForm] = useState<FormState>(INITIAL_FORM)
  const [disciplinas, setDisciplinas] = useState<DisciplinaCodigo[]>([])
  const [gruposEtarios, setGruposEtarios] = useState<GrupoEtario[]>(['JUNIOR', 'SENIOR', 'MASTER'])
  const [errors, setErrors] = useState<FormErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isLoading, setIsLoading] = useState(isEditing)
  const [torneoCreadoSinDisciplinas, setTorneoCreadoSinDisciplinas] = useState<string | null>(null)

  useEffect(() => {
    if (!torneoId) return
    const currentTorneoId = torneoId

    let cancelled = false

    async function loadTorneo() {
      setIsLoading(true)
      try {
        const [torneo, disciplinasActuales] = await Promise.all([
          fetchTorneo(currentTorneoId),
          listarDisciplinasTorneo(currentTorneoId),
        ])

        if (cancelled) return

        setForm({
          nombre: torneo.nombre,
          descripcion: torneo.descripcion,
          fechaInicio: torneo.fecha_inicio,
          fechaFin: torneo.fecha_fin,
          sedeNombre: torneo.sede.nombre,
          sedeCiudad: torneo.sede.ciudad,
          sedePais: torneo.sede.pais,
          entidadNombre: torneo.entidad_organizadora.nombre,
          entidadTipo: torneo.entidad_organizadora.tipo,
        })
        setGruposEtarios(torneo.grupos_etarios)
        setDisciplinas(disciplinasActuales.map((item) => item.disciplina))

        if (isEditingDisciplinas && torneo.estado !== 'CREADO') {
          setErrors({
            general:
              'Solo se pueden modificar disciplinas mientras el torneo este en estado Creado.',
          })
        }
        if (
          isEditingTorneo &&
          torneo.estado !== 'CREADO' &&
          torneo.estado !== 'INSCRIPCION_ABIERTA'
        ) {
          setErrors({
            general: 'Solo se pueden editar torneos en estado Creado o Inscripcion abierta.',
          })
        }
      } catch (error) {
        if (cancelled) return
        setErrors({ general: getErrorMessage(error) })
      } finally {
        if (!cancelled) setIsLoading(false)
      }
    }

    void loadTorneo()

    return () => {
      cancelled = true
    }
  }, [torneoId, isEditingDisciplinas, isEditingTorneo])

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
    if (!isEditingDisciplinas && gruposEtarios.length === 0) {
      nextErrors.gruposEtarios = 'Selecciona al menos una categoría'
    }
    return nextErrors
  }

  function buildCrearPayload(): CrearTorneoPayload {
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
      grupos_etarios: gruposEtarios,
    }
  }

  function buildActualizarPayload(): ActualizarTorneoPayload {
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
      grupos_etarios: gruposEtarios,
    }
  }

  function toggleGrupoEtario(grupo: GrupoEtario) {
    setGruposEtarios((current) =>
      current.includes(grupo)
        ? current.filter((item) => item !== grupo)
        : GRUPOS_ETARIOS.filter((item) => item === grupo || current.includes(item)),
    )
    setErrors((current) => ({ ...current, gruposEtarios: undefined, general: undefined }))
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
      if (isEditingTorneo && torneoId) {
        await actualizarTorneo(torneoId, buildActualizarPayload())
        navigate(`/organizador/torneo/${torneoId}`)
        return
      }

      if (isEditingDisciplinas && torneoId) {
        await asignarDisciplinas(torneoId, disciplinas)
        navigate(`/organizador/torneo/${torneoId}`)
        return
      }

      const response = await crearTorneo(buildCrearPayload())
      if (disciplinas.length > 0) {
        try {
          await asignarDisciplinas(response.torneo_id, disciplinas)
        } catch (error) {
          setTorneoCreadoSinDisciplinas(response.torneo_id)
          setErrors({ general: `Torneo creado sin disciplinas: ${getErrorMessage(error)}` })
          return
        }
      }
      navigate(`/organizador/panel?torneo_id=${response.torneo_id}`)
    } catch (error) {
      setErrors({ general: getErrorMessage(error) })
    } finally {
      setIsSubmitting(false)
    }
  }

  const pageTitle = isEditingTorneo
    ? 'Editar torneo'
    : isEditingDisciplinas
      ? 'Editar disciplinas'
      : 'Nuevo torneo'

  const pageSubtitle = isEditingTorneo
    ? 'Actualiza el nombre, sede, fechas y categorías del torneo'
    : isEditingDisciplinas
      ? 'Mismo formulario de alta reutilizado para ajustar disciplinas mientras el torneo sigue en estado Creado'
      : 'Alta del torneo y configuracion inicial de disciplinas'

  const submitLabel = isSubmitting
    ? isEditingTorneo
      ? 'Guardando...'
      : isEditingDisciplinas
        ? 'Guardando...'
        : 'Creando...'
    : isEditingTorneo
      ? 'Guardar cambios'
      : isEditingDisciplinas
        ? 'Guardar disciplinas'
        : 'Crear Torneo'

  const metadataDisabled = isEditingDisciplinas

  return (
    <OrganizadorLayout
      title={pageTitle}
      subtitle={pageSubtitle}
      showTournamentNavigation={false}
      simpleHeader
    >
      <div className="flex justify-end">
        <Link
          to={torneoId ? `/organizador/torneo/${torneoId}` : '/organizador/torneo'}
          className="rounded-full border border-slate-600 bg-slate-800 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-slate-100"
        >
          Volver
        </Link>
      </div>
      <form
        onSubmit={handleSubmit}
        className="rounded-[2rem] border border-slate-700 bg-slate-900/85 p-6 shadow-[0_20px_60px_rgba(2,6,23,0.24)]"
      >
        {isLoading ? (
          <div className="mb-5 rounded-[1.5rem] border border-slate-700 bg-slate-950/40 p-4 text-sm text-slate-300">
            Cargando torneo...
          </div>
        ) : null}

        {errors.general ? (
          <div className="mb-5 rounded-[1.5rem] border border-red-500/40 bg-red-950/40 p-4 text-sm text-red-100">
            <p>{errors.general}</p>
            {torneoCreadoSinDisciplinas ? (
              <Link
                to={`/organizador/torneo/${torneoCreadoSinDisciplinas}`}
                className="mt-3 inline-flex rounded-full border border-red-400/40 bg-red-950/40 px-3 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-red-100"
              >
                Ir al detalle del torneo
              </Link>
            ) : null}
          </div>
        ) : null}

        <div className="grid gap-5 lg:grid-cols-2">
          <label className="block text-sm font-semibold text-slate-100">
            Nombre
            <input
              value={form.nombre}
              onChange={(event) => updateField('nombre', event.target.value)}
              className={inputClass(Boolean(errors.nombre), metadataDisabled)}
              placeholder="BA 2026"
              disabled={metadataDisabled}
            />
            {errors.nombre ? <span className="mt-1 block text-sm text-red-300">{errors.nombre}</span> : null}
          </label>

          <label className="block text-sm font-semibold text-slate-100">
            Descripcion
            <input
              value={form.descripcion}
              onChange={(event) => updateField('descripcion', event.target.value)}
              className={inputClass(Boolean(errors.descripcion), metadataDisabled)}
              placeholder="Torneo nacional indoor"
              disabled={metadataDisabled}
            />
          </label>

          <label className="block text-sm font-semibold text-slate-100">
            Fecha de inicio
            <input
              type="date"
              value={form.fechaInicio}
              onChange={(event) => updateField('fechaInicio', event.target.value)}
              className={inputClass(Boolean(errors.fechaInicio), metadataDisabled)}
              required
              disabled={metadataDisabled}
            />
          </label>

          <label className="block text-sm font-semibold text-slate-100">
            Fecha de fin
            <input
              type="date"
              value={form.fechaFin}
              onChange={(event) => updateField('fechaFin', event.target.value)}
              className={inputClass(Boolean(errors.fechaFin), metadataDisabled)}
              required
              disabled={metadataDisabled}
            />
            {errors.fechaFin ? (
              <span className="mt-1 block text-sm text-red-300">{errors.fechaFin}</span>
            ) : null}
          </label>
        </div>

        <div className="mt-6 grid gap-5 lg:grid-cols-3">
          <label className="block text-sm font-semibold text-slate-100">
            Sede
            <input
              value={form.sedeNombre}
              onChange={(event) => updateField('sedeNombre', event.target.value)}
              className={inputClass(Boolean(errors.sedeNombre), metadataDisabled)}
              placeholder="Club Nautico"
              required
              disabled={metadataDisabled}
            />
          </label>

          <label className="block text-sm font-semibold text-slate-100">
            Ciudad
            <input
              value={form.sedeCiudad}
              onChange={(event) => updateField('sedeCiudad', event.target.value)}
              className={inputClass(Boolean(errors.sedeCiudad), metadataDisabled)}
              placeholder="Buenos Aires"
              required
              disabled={metadataDisabled}
            />
          </label>

          <label className="block text-sm font-semibold text-slate-100">
            Pais
            <input
              value={form.sedePais}
              onChange={(event) => updateField('sedePais', event.target.value)}
              className={inputClass(Boolean(errors.sedePais), metadataDisabled)}
              required
              disabled={metadataDisabled}
            />
          </label>
        </div>

        {!isEditingTorneo ? (
          <div className="mt-6 grid gap-5 lg:grid-cols-2">
            <label className="block text-sm font-semibold text-slate-100">
              Entidad organizadora
              <input
                value={form.entidadNombre}
                onChange={(event) => updateField('entidadNombre', event.target.value)}
                className={inputClass(Boolean(errors.entidadNombre), metadataDisabled)}
                placeholder="FAAS"
                required
                disabled={metadataDisabled}
              />
            </label>

            <label className="block text-sm font-semibold text-slate-100">
              Tipo de entidad
              <input
                value={form.entidadTipo}
                onChange={(event) => updateField('entidadTipo', event.target.value)}
                className={inputClass(Boolean(errors.entidadTipo), metadataDisabled)}
                placeholder="Federacion"
                required
                disabled={metadataDisabled}
              />
            </label>
          </div>
        ) : null}

        <div className="mt-6">
          {!isEditingDisciplinas ? (
            <fieldset className="mb-6">
              <legend className="text-sm font-semibold text-slate-100">Categorías</legend>
              <div className="mt-3 flex flex-wrap gap-2">
                {GRUPOS_ETARIOS.map((grupo) => {
                  const selected = gruposEtarios.includes(grupo)
                  return (
                    <button
                      key={grupo}
                      type="button"
                      onClick={() => toggleGrupoEtario(grupo)}
                      className={[
                        'rounded-full border px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] transition',
                        selected
                          ? 'border-sky-400 bg-sky-400/10 text-sky-300'
                          : 'border-slate-700 bg-slate-950 text-slate-300 hover:border-slate-500',
                      ].join(' ')}
                      aria-pressed={selected}
                    >
                      {grupo}
                    </button>
                  )
                })}
              </div>
              {errors.gruposEtarios ? (
                <p className="mt-2 text-sm text-red-300">{errors.gruposEtarios}</p>
              ) : null}
            </fieldset>
          ) : null}

          {!isEditingTorneo ? (
            <DisciplinaSelector
              value={disciplinas}
              onChange={(nextValue) => {
                setDisciplinas(nextValue)
                setErrors((current) => ({ ...current, disciplinas: undefined, general: undefined }))
              }}
              error={errors.disciplinas}
            />
          ) : null}
        </div>

        <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-end">
          <Link
            to={torneoId ? `/organizador/torneo/${torneoId}` : '/organizador/torneo'}
            className="rounded-full border border-slate-700 bg-slate-950 px-4 py-2 text-center text-xs font-semibold uppercase tracking-[0.16em] text-slate-200"
          >
            Cancelar
          </Link>
          <button
            type="submit"
            disabled={
              isSubmitting ||
              isLoading ||
              Boolean(errors.general) ||
              (!isEditingDisciplinas && gruposEtarios.length === 0)
            }
            className="rounded-full bg-sky-500 px-5 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-slate-950 disabled:cursor-not-allowed disabled:bg-slate-600 disabled:text-slate-300"
          >
            {submitLabel}
          </button>
        </div>
      </form>
    </OrganizadorLayout>
  )
}
