import { useState } from 'react'
import type { FormEvent } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import { ApiError, cambiarPassword } from '../api/identidad'
import useAuthStore from '../stores/useAuthStore'
import { PasswordStrengthBar } from '../components/PasswordStrengthBar'
import { HOME_BY_ROL } from '../utils/auth'

interface FormState {
  passwordActual: string
  passwordNueva: string
  confirmacion: string
}

type FormErrors = Partial<Record<keyof FormState | 'general', string>>

const INITIAL_FORM: FormState = {
  passwordActual: '',
  passwordNueva: '',
  confirmacion: '',
}

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
    if (error.status === 401) return 'La contrasena actual es incorrecta'
    if (error.status === 422) return error.message
    return error.message
  }
  if (error instanceof Error) return error.message
  return 'No se pudo actualizar la contrasena'
}

export function CambiarPasswordPage() {
  const navigate = useNavigate()
  const rol = useAuthStore((s) => s.rol)
  const [form, setForm] = useState<FormState>(INITIAL_FORM)
  const [errors, setErrors] = useState<FormErrors>({})

  const mutation = useMutation({
    mutationFn: cambiarPassword,
    onSuccess: () => {
      if (rol) {
        navigate(HOME_BY_ROL[rol], {
          replace: true,
          state: { passwordUpdated: true },
        })
      }
    },
    onError: (error) => {
      const message = resolveApiError(error)
      if (error instanceof ApiError && error.status === 401) {
        setErrors((current) => ({ ...current, passwordActual: message, general: undefined }))
        return
      }
      if (error instanceof ApiError && error.status === 422) {
        setErrors((current) => ({ ...current, passwordNueva: message, general: undefined }))
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
    if (!form.passwordActual) nextErrors.passwordActual = 'La contrasena actual es obligatoria'
    if (!form.passwordNueva) {
      nextErrors.passwordNueva = 'La contrasena nueva es obligatoria'
    } else if (form.passwordNueva.length < 10) {
      nextErrors.passwordNueva = 'La contrasena debe tener al menos 10 caracteres'
    } else if (!/[A-Z]/.test(form.passwordNueva)) {
      nextErrors.passwordNueva = 'La contrasena debe incluir al menos una mayuscula'
    } else if (!/[0-9]/.test(form.passwordNueva)) {
      nextErrors.passwordNueva = 'La contrasena debe incluir al menos un numero'
    }
    if (!form.confirmacion) {
      nextErrors.confirmacion = 'Debes confirmar la contrasena nueva'
    } else if (form.confirmacion !== form.passwordNueva) {
      nextErrors.confirmacion = 'Las contrasenas no coinciden'
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
      password_actual: form.passwordActual,
      password_nueva: form.passwordNueva,
    })
  }

  const backHref = rol ? HOME_BY_ROL[rol] : '/'

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto flex min-h-screen w-full max-w-md items-center px-4 py-8">
        <div className="w-full rounded-[2rem] border border-slate-800 bg-slate-900/80 p-8 shadow-[0_24px_80px_-50px_rgba(34,211,238,0.7)]">
          <p className="text-center text-xs font-semibold uppercase tracking-[0.24em] text-sky-400">
            Seguridad
          </p>
          <h1 className="mb-2 mt-3 text-center text-3xl font-semibold text-slate-50">
            Cambiar contrasena
          </h1>
          <p className="mb-6 text-center text-sm text-slate-400">
            Actualiza tu acceso ingresando primero la contrasena actual.
          </p>

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <label className="text-sm font-medium text-slate-300">
              Contrasena actual
              <input
                type="password"
                value={form.passwordActual}
                onChange={(event) => updateField('passwordActual', event.target.value)}
                className={inputClass(Boolean(errors.passwordActual))}
              />
              {errors.passwordActual ? (
                <span className="mt-1 block text-sm text-red-300">{errors.passwordActual}</span>
              ) : null}
            </label>

            <label className="text-sm font-medium text-slate-300">
              Nueva contrasena
              <input
                type="password"
                value={form.passwordNueva}
                onChange={(event) => updateField('passwordNueva', event.target.value)}
                className={inputClass(Boolean(errors.passwordNueva))}
              />
              <PasswordStrengthBar password={form.passwordNueva} />
              {errors.passwordNueva ? (
                <span className="mt-1 block text-sm text-red-300">{errors.passwordNueva}</span>
              ) : null}
            </label>

            <label className="text-sm font-medium text-slate-300">
              Confirmar nueva contrasena
              <input
                type="password"
                value={form.confirmacion}
                onChange={(event) => updateField('confirmacion', event.target.value)}
                className={inputClass(Boolean(errors.confirmacion))}
              />
              {errors.confirmacion ? (
                <span className="mt-1 block text-sm text-red-300">{errors.confirmacion}</span>
              ) : null}
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
              {mutation.isPending ? 'Actualizando...' : 'Actualizar contrasena'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-400">
            <Link to={backHref} className="font-semibold text-sky-300 hover:text-sky-200">
              Volver
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
