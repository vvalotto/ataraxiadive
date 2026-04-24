import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { ApiError, solicitarResetPassword } from '../api/identidad'

export function RecuperarPasswordPage() {
  const [email, setEmail] = useState('')
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: solicitarResetPassword,
    onSuccess: (data) => {
      setSuccessMessage(data.detail)
      setErrorMessage(null)
    },
    onError: (error) => {
      setSuccessMessage(null)
      setErrorMessage(
        error instanceof ApiError || error instanceof Error
          ? error.message
          : 'No se pudo procesar la solicitud',
      )
    },
  })

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setErrorMessage(null)
    setSuccessMessage(null)
    mutation.mutate({ email: email.trim() })
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto flex min-h-screen w-full max-w-md items-center px-4 py-8">
        <div className="w-full rounded-[2rem] border border-slate-800 bg-slate-900/80 p-8 shadow-[0_24px_80px_-50px_rgba(34,211,238,0.7)]">
          <p className="text-center text-xs font-semibold uppercase tracking-[0.24em] text-sky-400">
            AtaraxiaDive
          </p>
          <h1 className="mb-2 mt-3 text-center text-3xl font-semibold text-slate-50">
            Recuperar contrasena
          </h1>
          <p className="mb-6 text-center text-sm text-slate-400">
            Ingresa tu email y te enviaremos un enlace para restablecerla.
          </p>

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <label className="text-sm font-medium text-slate-300">
              Email
              <input
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
                className="mt-1 w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-sky-500"
              />
            </label>

            {successMessage ? (
              <p className="rounded-2xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-center text-sm text-emerald-100">
                {successMessage}
              </p>
            ) : null}
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
              {mutation.isPending ? 'Enviando...' : 'Enviar enlace'}
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
