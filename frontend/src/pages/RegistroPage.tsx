import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import {
  ApiError,
  crearUsuario,
  type CrearUsuarioRequest,
  type RolGestionUsuario,
} from '../api/identidad'
import useAuthStore from '../stores/useAuthStore'
import { PasswordStrengthBar } from '../components/PasswordStrengthBar'

type FormState = CrearUsuarioRequest & { confirmarPassword: string }

type FormErrors = Partial<Record<keyof FormState | 'general', string>>

const INITIAL_FORM: FormState = {
  nombre: '',
  apellido: '',
  email: '',
  password: '',
  confirmarPassword: '',
  rol: 'ATLETA',
}

const ROLES: Array<{ value: RolGestionUsuario; label: string }> = [
  { value: 'ATLETA', label: 'Atleta' },
  { value: 'JUEZ', label: 'Juez' },
  { value: 'ORGANIZADOR', label: 'Organizador' },
]

function inputClass(hasError: boolean): string {
  return [
    'w-full rounded-2xl border px-4 py-3 text-sm text-slate-100 focus:outline-none focus:ring-2',
    hasError
      ? 'border-red-500 bg-red-950/30 focus:ring-red-500'
      : 'border-slate-700 bg-slate-950 focus:ring-sky-500',
  ].join(' ')
}

function resolveApiError(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 409) return 'Este email ya esta registrado'
    if (error.status === 422) return error.message
    if (error.status === 403) return 'El rol ADMIN no esta permitido en el auto-registro'
    return error.message
  }
  if (error instanceof Error) return error.message
  return 'No se pudo crear la cuenta'
}

export function RegistroPage() {
  const navigate = useNavigate()
  const rol = useAuthStore((s) => s.rol)
  const [form, setForm] = useState<FormState>(INITIAL_FORM)
  const [errors, setErrors] = useState<FormErrors>({})

  const mutation = useMutation({
    mutationFn: crearUsuario,
    onSuccess: () => {
      navigate('/login?registered=1', { replace: true })
    },
    onError: (error) => {
      const message = resolveApiError(error)
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

  if (rol === 'juez') return <Navigate to="/juez/disciplinas" replace />
  if (rol === 'organizador') return <Navigate to="/organizador/dashboard" replace />
  if (rol === 'atleta') return <Navigate to="/atleta/dashboard" replace />

  function updateField<T extends keyof FormState>(field: T, value: FormState[T]) {
    setForm((current) => ({ ...current, [field]: value }))
    setErrors((current) => ({ ...current, [field]: undefined, general: undefined }))
  }

  function validate(): FormErrors {
    const nextErrors: FormErrors = {}
    if (!form.nombre.trim()) nextErrors.nombre = 'El nombre es requerido'
    if (!form.apellido.trim()) nextErrors.apellido = 'El apellido es requerido'
    if (!form.email.trim()) nextErrors.email = 'El email es obligatorio'
    if (!form.password) {
      nextErrors.password = 'La contrasena es obligatoria'
    } else if (form.password.length < 10) {
      nextErrors.password = 'La contrasena debe tener al menos 10 caracteres'
    } else if (!/[A-Z]/.test(form.password)) {
      nextErrors.password = 'La contrasena debe incluir al menos una mayuscula'
    } else if (!/[0-9]/.test(form.password)) {
      nextErrors.password = 'La contrasena debe incluir al menos un numero'
    }
    if (!form.confirmarPassword) {
      nextErrors.confirmarPassword = 'Confirma tu contrasena'
    } else if (form.password !== form.confirmarPassword) {
      nextErrors.confirmarPassword = 'Las contrasenas no coinciden'
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

    mutation.mutate({
      nombre: form.nombre.trim(),
      apellido: form.apellido.trim(),
      email: form.email.trim(),
      password: form.password,
      rol: form.rol,
    })
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto flex min-h-screen w-full max-w-md items-center px-4 py-8">
        <div className="w-full rounded-[2rem] border border-slate-800 bg-slate-900/80 p-8 shadow-[0_24px_80px_-50px_rgba(34,211,238,0.7)]">
          <p className="text-center text-xs font-semibold uppercase tracking-[0.24em] text-sky-400">
            AtaraxiaDive
          </p>
          <h1 className="mb-2 mt-3 text-center text-3xl font-semibold text-slate-50">
            Crear cuenta
          </h1>
          <p className="mb-6 text-center text-sm text-slate-400">
            Registro publico para atletas, jueces y organizadores
          </p>

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="text-sm font-medium text-slate-300">
                Nombre
                <input
                  type="text"
                  value={form.nombre}
                  onChange={(event) => updateField('nombre', event.target.value)}
                  className={inputClass(Boolean(errors.nombre))}
                />
                {errors.nombre ? (
                  <span className="mt-1 block text-sm text-red-300">{errors.nombre}</span>
                ) : null}
              </label>
              <label className="text-sm font-medium text-slate-300">
                Apellido
                <input
                  type="text"
                  value={form.apellido}
                  onChange={(event) => updateField('apellido', event.target.value)}
                  className={inputClass(Boolean(errors.apellido))}
                />
                {errors.apellido ? (
                  <span className="mt-1 block text-sm text-red-300">{errors.apellido}</span>
                ) : null}
              </label>
            </div>

            <label className="text-sm font-medium text-slate-300">
              Email
              <input
                type="email"
                value={form.email}
                onChange={(event) => updateField('email', event.target.value)}
                className={inputClass(Boolean(errors.email))}
              />
              {errors.email ? <span className="mt-1 block text-sm text-red-300">{errors.email}</span> : null}
            </label>

            <label className="text-sm font-medium text-slate-300">
              Contraseña
              <input
                type="password"
                value={form.password}
                onChange={(event) => updateField('password', event.target.value)}
                className={inputClass(Boolean(errors.password))}
              />
              <PasswordStrengthBar password={form.password} />
              {errors.password ? (
                <span className="mt-1 block text-sm text-red-300">{errors.password}</span>
              ) : null}
            </label>

            <label className="text-sm font-medium text-slate-300">
              Confirmar contraseña
              <input
                type="password"
                value={form.confirmarPassword}
                onChange={(event) => updateField('confirmarPassword', event.target.value)}
                className={inputClass(Boolean(errors.confirmarPassword))}
              />
              {errors.confirmarPassword ? (
                <span className="mt-1 block text-sm text-red-300">{errors.confirmarPassword}</span>
              ) : null}
            </label>

            <label className="text-sm font-medium text-slate-300">
              Rol
              <select
                value={form.rol}
                onChange={(event) => updateField('rol', event.target.value as RolGestionUsuario)}
                className={inputClass(false)}
              >
                {ROLES.map((rolOption) => (
                  <option key={rolOption.value} value={rolOption.value}>
                    {rolOption.label}
                  </option>
                ))}
              </select>
            </label>

            {errors.general ? (
              <p className="rounded-2xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-center text-sm text-red-100">
                {errors.general}
              </p>
            ) : null}

            <button
              type="submit"
              disabled={mutation.isPending}
              className="rounded-2xl bg-sky-500 py-3 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950 transition-colors hover:bg-sky-400 disabled:opacity-50"
            >
              {mutation.isPending ? 'Creando cuenta...' : 'Registrarme'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-400">
            ¿Ya tenes cuenta?{' '}
            <Link to="/login" className="font-semibold text-sky-300 hover:text-sky-200">
              Inicia sesion
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
