import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { loginApi } from '../api/auth'
import useAuthStore from '../stores/useAuthStore'

export function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate()
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
    void navigate('/juez/disciplinas', { replace: true })
    return null
  }
  if (rol === 'organizador') {
    void navigate('/organizador/dashboard', { replace: true })
    return null
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate()
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 text-gray-900">
      <div className="w-full max-w-sm bg-white rounded-xl shadow-md p-8">
        <h1 className="text-2xl font-bold text-gray-800 mb-6 text-center">AtaraxiaDive</h1>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-sky-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-sky-500"
            />
          </div>

          {mutation.isError && (
            <p className="text-sm text-red-600 text-center">
              {mutation.error instanceof Error ? mutation.error.message : 'Error al iniciar sesión'}
            </p>
          )}

          <button
            type="submit"
            disabled={mutation.isPending}
            className="bg-sky-600 hover:bg-sky-700 text-white font-medium py-2 rounded-lg text-sm transition-colors disabled:opacity-50"
          >
            {mutation.isPending ? 'Iniciando sesión...' : 'Iniciar sesión'}
          </button>
        </form>
      </div>
    </div>
  )
}
