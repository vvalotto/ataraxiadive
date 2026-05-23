import { useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  ApiError,
  agregarRolUsuario,
  crearUsuario,
  listarTodosLosUsuarios,
  quitarRolUsuario,
  type RolGestionUsuario,
  type UsuarioDto,
} from '../../api/identidad'
import { OrganizadorLayout } from '../../components/organizador/OrganizadorLayout'

interface FormState {
  nombre: string
  apellido: string
  email: string
  password: string
  rol: RolGestionUsuario
}

type FormErrors = Partial<Record<keyof FormState | 'general', string>>

const INITIAL_FORM: FormState = {
  nombre: '',
  apellido: '',
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
    const rolCompare = (a.roles[0] ?? '').localeCompare(b.roles[0] ?? '')
    if (rolCompare !== 0) return rolCompare
    return a.email.localeCompare(b.email)
  })
}

export function UsuariosPage() {
  const queryClient = useQueryClient()
  const [form, setForm] = useState<FormState>(INITIAL_FORM)
  const [errors, setErrors] = useState<FormErrors>({})
  const [addingRolFor, setAddingRolFor] = useState<string | null>(null)
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
  const agregarRolMutation = useMutation({
    mutationFn: ({ usuarioId, rol }: { usuarioId: string; rol: RolGestionUsuario }) =>
      agregarRolUsuario(usuarioId, rol),
    onSuccess: async () => {
      setAddingRolFor(null)
      await queryClient.invalidateQueries({ queryKey: ['usuarios'] })
    },
  })
  const quitarRolMutation = useMutation({
    mutationFn: ({ usuarioId, rol }: { usuarioId: string; rol: RolGestionUsuario }) =>
      quitarRolUsuario(usuarioId, rol),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['usuarios'] })
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
    if (!form.nombre.trim()) {
      nextErrors.nombre = 'El nombre es obligatorio'
    }
    if (!form.apellido.trim()) {
      nextErrors.apellido = 'El apellido es obligatorio'
    }
    if (!form.password) {
      nextErrors.password = 'La contrasena es obligatoria'
    } else if (form.password.length < 10) {
      nextErrors.password = 'La contrasena debe tener al menos 10 caracteres'
    } else if (!/[A-Z]/.test(form.password)) {
      nextErrors.password = 'La contrasena debe incluir al menos una mayuscula'
    } else if (!/[0-9]/.test(form.password)) {
      nextErrors.password = 'La contrasena debe incluir al menos un numero'
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
      nombre: form.nombre.trim(),
      apellido: form.apellido.trim(),
      email: form.email.trim(),
      password: form.password,
      roles: [form.rol],
    })
  }

  return (
    <OrganizadorLayout
      title="Gestion de usuarios"
      subtitle="Alta de jueces, atletas y organizadores para operar el torneo"
      actions={
        <Link
          to="/organizador/torneo"
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
                    <th className="px-4 py-3 font-semibold">Nombre</th>
                    <th className="px-4 py-3 font-semibold">Apellido</th>
                    <th className="px-4 py-3 font-semibold">Email</th>
                    <th className="px-4 py-3 font-semibold">Roles</th>
                    <th className="px-4 py-3 font-semibold">Estado</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-stone-200">
                  {usuarios.map((usuario) => {
                    const rolesGestionables = usuario.roles.filter(
                      (r): r is RolGestionUsuario => r !== 'ADMIN',
                    )
                    const rolesDisponibles = ROLES_GESTIONABLES.filter(
                      (r) => !usuario.roles.includes(r.value),
                    )
                    const isAddingThis = addingRolFor === usuario.usuario_id
                    return (
                      <tr key={usuario.usuario_id} className="bg-white">
                        <td className="px-4 py-3 text-stone-900">{usuario.nombre}</td>
                        <td className="px-4 py-3 text-stone-900">{usuario.apellido}</td>
                        <td className="px-4 py-3 font-medium text-stone-900">{usuario.email}</td>
                        <td className="px-4 py-3">
                          <div className="flex flex-wrap items-center gap-1">
                            {rolesGestionables.map((rol) => (
                              <span
                                key={rol}
                                className="inline-flex items-center gap-1 rounded-full bg-stone-100 px-2 py-0.5 text-xs font-semibold text-stone-700"
                              >
                                {ROL_LABELS[rol] ?? rol}
                                {rolesGestionables.length > 1 ? (
                                  <button
                                    type="button"
                                    onClick={() =>
                                      quitarRolMutation.mutate({
                                        usuarioId: usuario.usuario_id,
                                        rol,
                                      })
                                    }
                                    disabled={quitarRolMutation.isPending}
                                    className="ml-0.5 text-stone-400 hover:text-red-600 disabled:opacity-40"
                                    title={`Quitar rol ${ROL_LABELS[rol]}`}
                                  >
                                    ×
                                  </button>
                                ) : null}
                              </span>
                            ))}
                            {usuario.roles.includes('ADMIN') ? (
                              <span className="inline-flex rounded-full bg-amber-100 px-2 py-0.5 text-xs font-semibold text-amber-800">
                                Admin
                              </span>
                            ) : null}
                            {rolesDisponibles.length > 0 ? (
                              isAddingThis ? (
                                <select
                                  autoFocus
                                  className="rounded border border-stone-300 px-1 py-0.5 text-xs text-stone-900 outline-none focus:border-emerald-600"
                                  defaultValue=""
                                  onChange={(e) => {
                                    const rol = e.target.value as RolGestionUsuario
                                    if (rol) {
                                      agregarRolMutation.mutate({
                                        usuarioId: usuario.usuario_id,
                                        rol,
                                      })
                                    }
                                  }}
                                  onBlur={() => setAddingRolFor(null)}
                                >
                                  <option value="" disabled>
                                    Agregar...
                                  </option>
                                  {rolesDisponibles.map((r) => (
                                    <option key={r.value} value={r.value}>
                                      {r.label}
                                    </option>
                                  ))}
                                </select>
                              ) : (
                                <button
                                  type="button"
                                  onClick={() => setAddingRolFor(usuario.usuario_id)}
                                  className="inline-flex h-5 w-5 items-center justify-center rounded-full border border-stone-300 text-xs text-stone-400 hover:border-emerald-600 hover:text-emerald-700"
                                  title="Agregar rol"
                                >
                                  +
                                </button>
                              )
                            ) : null}
                          </div>
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
                    )
                  })}
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
            Nombre
            <input
              type="text"
              value={form.nombre}
              onChange={(event) => updateField('nombre', event.target.value)}
              className={inputClass(Boolean(errors.nombre))}
              placeholder="Ana"
            />
            {errors.nombre ? (
              <span className="mt-1 block text-sm text-red-700">{errors.nombre}</span>
            ) : null}
          </label>

          <label className="mt-4 block text-sm font-semibold text-stone-900">
            Apellido
            <input
              type="text"
              value={form.apellido}
              onChange={(event) => updateField('apellido', event.target.value)}
              className={inputClass(Boolean(errors.apellido))}
              placeholder="Garcia"
            />
            {errors.apellido ? (
              <span className="mt-1 block text-sm text-red-700">{errors.apellido}</span>
            ) : null}
          </label>

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
