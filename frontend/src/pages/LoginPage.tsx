import { useState } from 'react'
import { Navigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { loginApi } from '../api/auth'
import useAuthStore from '../stores/useAuthStore'

export function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const login = useAuthStore((s) => s.login)
  const rol = useAuthStore((s) => s.rol)

  const mutation = useMutation({
    mutationFn: () => loginApi(email, password),
    onSuccess: (data) => {
      login(data.access_token)
    },
  })

  // Redirect si ya tiene sesión activa
  if (rol === 'juez') {
    return <Navigate to="/juez/disciplinas" replace />
  }
  if (rol === 'organizador') {
    return <Navigate to="/organizador/dashboard" replace />
  }
  if (rol === 'atleta') {
    return <Navigate to="/atleta/dashboard" replace />
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate()
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto flex min-h-screen w-full max-w-sm items-center px-4 py-6">
        <div className="w-full rounded-[2rem] border border-slate-800 bg-slate-900/80 p-8 shadow-[0_24px_80px_-50px_rgba(34,211,238,0.7)]">
          <p className="text-center text-xs font-semibold uppercase tracking-[0.24em] text-sky-400">
            AtaraxiaDive
          </p>
          <h1 className="mb-2 mt-3 text-center text-3xl font-semibold text-slate-50">
            Iniciar sesión
          </h1>
          <p className="mb-6 text-center text-sm text-slate-400">
            Portal del juez, organizador y atleta
          </p>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-300">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-sky-500"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-300">Contraseña</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-sky-500"
            />
          </div>

          {mutation.isError && (
            <p className="rounded-2xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-center text-sm text-red-100">
              {mutation.error instanceof Error ? mutation.error.message : 'Error al iniciar sesión'}
            </p>
          )}

          <button
            type="submit"
            disabled={mutation.isPending}
            className="rounded-2xl bg-sky-500 py-3 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950 transition-colors hover:bg-sky-400 disabled:opacity-50"
          >
            {mutation.isPending ? 'Iniciando sesión...' : 'Iniciar sesión'}
          </button>
        </form>
      </div>
      </div>
    </div>
  )
}
