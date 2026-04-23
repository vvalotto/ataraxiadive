import { useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  ApiError,
  crearUsuario,
  listarTodosLosUsuarios,
  type RolGestionUsuario,
  type UsuarioDto,
} from '../../api/identidad'
import { OrganizadorLayout } from '../../components/organizador/OrganizadorLayout'

interface FormState {
  email: string
  password: string
  rol: RolGestionUsuario
}

type FormErrors = Partial<Record<keyof FormState | 'general', string>>

const INITIAL_FORM: FormState = {
  email: '',
  password: '',
  rol: 'JUEZ',
}

const ROLES_GESTIONABLES: Array<{ value: RolGestionUsuario; label: string }> = [
  { value: 'JUEZ', label: 'Juez' },
  { value: 'ATLETA', label: 'Atleta' },
  { value: 'ORGANIZADOR', label: 'Organizador' },
]

const ROL_LABELS: Record<string, string> = {
  JUEZ: 'Juez',
  ATLETA: 'Atleta',
  ORGANIZADOR: 'Organizador',
  ADMIN: 'Admin',
}

function inputClass(hasError: boolean): string {
  return [
    'mt-2 w-full rounded-lg border bg-white px-3 py-2 text-sm text-stone-900 outline-none transition',
    hasError ? 'border-red-400 focus:border-red-600' : 'border-stone-300 focus:border-emerald-700',
  ].join(' ')
}

function getUsuarioError(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 409) return 'Este email ya esta registrado'
    if (error.status === 422) return 'La contrasena debe tener al menos 8 caracteres'
    return error.message
  }
  if (error instanceof Error) return error.message
  return 'No se pudo crear el usuario'
}

function ordenarUsuarios(usuarios: UsuarioDto[]): UsuarioDto[] {
  return [...usuarios].sort((a, b) => {
    const rolCompare = a.rol.localeCompare(b.rol)
    if (rolCompare !== 0) return rolCompare
    return a.email.localeCompare(b.email)
  })
}

export function UsuariosPage() {
  const queryClient = useQueryClient()
  const [form, setForm] = useState<FormState>(INITIAL_FORM)
  const [errors, setErrors] = useState<FormErrors>({})
  const usuariosQuery = useQuery({
    queryKey: ['usuarios'],
    queryFn: listarTodosLosUsuarios,
  })
  const usuarios = useMemo(
    () => ordenarUsuarios(usuariosQuery.data ?? []),
    [usuariosQuery.data],
  )
  const crearUsuarioMutation = useMutation({
    mutationFn: crearUsuario,
    onSuccess: async () => {
      setForm(INITIAL_FORM)
      setErrors({})
      await queryClient.invalidateQueries({ queryKey: ['usuarios'] })
    },
    onError: (error) => {
      const message = getUsuarioError(error)
      if (error instanceof ApiError && error.status === 409) {
        setErrors((current) => ({ ...current, email: message, general: undefined }))
        return
      }
      if (error instanceof ApiError && error.status === 422) {
        setErrors((current) => ({ ...current, password: message, general: undefined }))
        return
      }
      setErrors((current) => ({ ...current, general: message }))
    },
  })

  function updateField<T extends keyof FormState>(field: T, value: FormState[T]) {
    setForm((current) => ({ ...current, [field]: value }))
    setErrors((current) => ({ ...current, [field]: undefined, general: undefined }))
  }

  function validate(): FormErrors {
    const nextErrors: FormErrors = {}
    if (!form.email.trim()) {
      nextErrors.email = 'El email es obligatorio'
    }
    if (!form.password) {
      nextErrors.password = 'La contrasena es obligatoria'
    } else if (form.password.length < 8) {
      nextErrors.password = 'La contrasena debe tener al menos 8 caracteres'
    }
    return nextErrors
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const validationErrors = validate()
    setErrors(validationErrors)
    if (Object.keys(validationErrors).length > 0) {
      return
    }

    crearUsuarioMutation.mutate({
      email: form.email.trim(),
      password: form.password,
      rol: form.rol,
    })
  }

  return (
    <OrganizadorLayout
      title="Gestion de usuarios"
      subtitle="Alta de jueces, atletas y organizadores para operar el torneo"
      actions={
        <Link
          to="/organizador/dashboard"
          className="rounded-lg border border-stone-900 px-4 py-2 text-sm font-semibold text-stone-900"
        >
          Volver
        </Link>
      }
    >
      <section className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_380px]">
        <div className="rounded-lg border border-stone-300 bg-white p-5 shadow-[0_20px_60px_rgba(120,93,54,0.08)]">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase text-stone-500">Usuarios</p>
              <h2 className="mt-1 text-xl font-semibold text-stone-900">Registrados</h2>
            </div>
            <p className="text-sm text-stone-600">{usuarios.length} usuarios</p>
          </div>

          {usuariosQuery.isLoading ? (
            <div className="mt-5 rounded-lg border border-stone-200 bg-stone-50 p-4 text-sm text-stone-600">
              Cargando usuarios...
            </div>
          ) : null}

          {usuariosQuery.isError ? (
            <div className="mt-5 rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-900">
              No se pudieron cargar los usuarios.
            </div>
          ) : null}

          {!usuariosQuery.isLoading && !usuariosQuery.isError && usuarios.length === 0 ? (
            <div className="mt-5 rounded-lg border border-stone-200 bg-stone-50 p-4 text-sm text-stone-600">
              No hay usuarios registrados.
            </div>
          ) : null}

          {!usuariosQuery.isLoading && !usuariosQuery.isError && usuarios.length > 0 ? (
            <div className="mt-5 overflow-hidden rounded-lg border border-stone-200">
              <table className="w-full border-collapse text-left text-sm">
                <thead className="bg-stone-100 text-xs uppercase text-stone-500">
                  <tr>
                    <th className="px-4 py-3 font-semibold">Email</th>
                    <th className="px-4 py-3 font-semibold">Rol</th>
                    <th className="px-4 py-3 font-semibold">Estado</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-stone-200">
                  {usuarios.map((usuario) => (
                    <tr key={usuario.usuario_id} className="bg-white">
                      <td className="px-4 py-3 font-medium text-stone-900">{usuario.email}</td>
                      <td className="px-4 py-3 text-stone-700">
                        {ROL_LABELS[usuario.rol] ?? usuario.rol}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={
                            usuario.activo
                              ? 'inline-flex rounded-lg bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-800'
                              : 'inline-flex rounded-lg bg-stone-100 px-2 py-1 text-xs font-semibold text-stone-600'
                          }
                        >
                          {usuario.activo ? 'Activo' : 'Inactivo'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}
        </div>

        <form
          onSubmit={handleSubmit}
          className="rounded-lg border border-stone-300 bg-white p-5 shadow-[0_20px_60px_rgba(120,93,54,0.08)]"
        >
          <p className="text-xs font-semibold uppercase text-stone-500">Nuevo usuario</p>
          <h2 className="mt-1 text-xl font-semibold text-stone-900">Crear acceso</h2>

          {errors.general ? (
            <div className="mt-4 rounded-lg border border-red-300 bg-red-50 p-3 text-sm text-red-900">
              {errors.general}
            </div>
          ) : null}

          <label className="mt-5 block text-sm font-semibold text-stone-900">
            Email
            <input
              type="email"
              value={form.email}
              onChange={(event) => updateField('email', event.target.value)}
              className={inputClass(Boolean(errors.email))}
              placeholder="juez@email.com"
            />
            {errors.email ? <span className="mt-1 block text-sm text-red-700">{errors.email}</span> : null}
          </label>

          <label className="mt-4 block text-sm font-semibold text-stone-900">
            Password
            <input
              type="password"
              value={form.password}
              onChange={(event) => updateField('password', event.target.value)}
              className={inputClass(Boolean(errors.password))}
              placeholder="Minimo 8 caracteres"
            />
            {errors.password ? (
              <span className="mt-1 block text-sm text-red-700">{errors.password}</span>
            ) : null}
          </label>

          <label className="mt-4 block text-sm font-semibold text-stone-900">
            Rol
            <select
              value={form.rol}
              onChange={(event) => updateField('rol', event.target.value as RolGestionUsuario)}
              className={inputClass(Boolean(errors.rol))}
            >
              {ROLES_GESTIONABLES.map((rol) => (
                <option key={rol.value} value={rol.value}>
                  {rol.label}
                </option>
              ))}
            </select>
          </label>

          <button
            type="submit"
            disabled={crearUsuarioMutation.isPending}
            className="mt-6 w-full rounded-lg bg-emerald-800 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-stone-400"
          >
            {crearUsuarioMutation.isPending ? 'Creando...' : 'Crear usuario'}
          </button>
        </form>
      </section>
    </OrganizadorLayout>
  )
}
