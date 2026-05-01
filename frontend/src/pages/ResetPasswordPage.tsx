import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, Navigate, useNavigate, useSearchParams } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { ApiError, resetPassword } from '../api/identidad'
import useAuthStore from '../stores/useAuthStore'
import { PasswordStrengthBar } from '../components/PasswordStrengthBar'

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const rol = useAuthStore((s) => s.rol)
  const [passwordNueva, setPasswordNueva] = useState('')
  const [passwordConfirmacion, setPasswordConfirmacion] = useState('')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const token = searchParams.get('token') ?? ''

  const mutation = useMutation({
    mutationFn: resetPassword,
    onSuccess: () => {
      navigate('/login?reset=1', { replace: true })
    },
    onError: (error) => {
      setErrorMessage(
        error instanceof ApiError || error instanceof Error
          ? error.message
          : 'No se pudo restablecer la contrasena',
      )
    },
  })

  if (rol === 'juez') return <Navigate to="/juez/disciplinas" replace />
  if (rol === 'organizador') return <Navigate to="/organizador/dashboard" replace />
  if (rol === 'atleta') return <Navigate to="/atleta" replace />

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!token) {
      setErrorMessage('El enlace de recuperacion es invalido')
      return
    }
    if (passwordNueva.length < 10) {
      setErrorMessage('La contrasena debe tener al menos 10 caracteres')
      return
    }
    if (!/[A-Z]/.test(passwordNueva)) {
      setErrorMessage('La contrasena debe incluir al menos una mayuscula')
      return
    }
    if (!/[0-9]/.test(passwordNueva)) {
      setErrorMessage('La contrasena debe incluir al menos un numero')
      return
    }
    if (passwordNueva !== passwordConfirmacion) {
      setErrorMessage('Las contrasenas no coinciden')
      return
    }

    setErrorMessage(null)
    mutation.mutate({ token, password_nueva: passwordNueva })
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto flex min-h-screen w-full max-w-md items-center px-4 py-8">
        <div className="w-full rounded-[2rem] border border-slate-800 bg-slate-900/80 p-8 shadow-[0_24px_80px_-50px_rgba(34,211,238,0.7)]">
          <p className="text-center text-xs font-semibold uppercase tracking-[0.24em] text-sky-400">
            AtaraxiaDive
          </p>
          <h1 className="mb-2 mt-3 text-center text-3xl font-semibold text-slate-50">
            Restablecer contrasena
          </h1>
          <p className="mb-6 text-center text-sm text-slate-400">
            Defini una nueva clave para recuperar el acceso a tu cuenta.
          </p>

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <label className="text-sm font-medium text-slate-300">
              Nueva contrasena
              <input
                type="password"
                value={passwordNueva}
                onChange={(event) => setPasswordNueva(event.target.value)}
                required
                className="mt-1 w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-sky-500"
              />
              <PasswordStrengthBar password={passwordNueva} />
            </label>

            <label className="text-sm font-medium text-slate-300">
              Repetir contrasena
              <input
                type="password"
                value={passwordConfirmacion}
                onChange={(event) => setPasswordConfirmacion(event.target.value)}
                required
                className="mt-1 w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-sky-500"
              />
            </label>

            {errorMessage ? (
              <p className="rounded-2xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-center text-sm text-red-100">
                {errorMessage}
              </p>
            ) : null}

            <button
              type="submit"
              disabled={mutation.isPending}
              className="rounded-2xl bg-sky-500 py-3 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950 transition-colors hover:bg-sky-400 disabled:opacity-50"
            >
              {mutation.isPending ? 'Actualizando...' : 'Guardar nueva contrasena'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-400">
            <Link to="/login" className="font-semibold text-sky-300 hover:text-sky-200">
              Volver a iniciar sesion
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
