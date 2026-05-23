import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { agregarRolPropio, quitarRolPropio, refrescarToken, type RolGestionUsuario } from '../../api/identidad'
import useAuthStore from '../../stores/useAuthStore'

const ROLES_TOGGLEABLES: Array<{ value: RolGestionUsuario; label: string }> = [
  { value: 'JUEZ', label: 'Juez' },
  { value: 'ORGANIZADOR', label: 'Organizador' },
]

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) return error.message
  return 'No se pudo completar la operación'
}

export function RolesSection() {
  const userId = useAuthStore((s) => s.userId)
  const roles = useAuthStore((s) => s.roles)
  const login = useAuthStore((s) => s.login)
  const token = useAuthStore((s) => s.token)
  const [error, setError] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const rolesActivos = (roles ?? []).map((r) => r.toUpperCase())

  async function refreshStore() {
    try {
      const { access_token } = await refrescarToken()
      login(access_token)
    } catch {
      // si falla el refresh, el store queda como está
    }
  }

  const agregarMutation = useMutation({
    mutationFn: (rol: RolGestionUsuario) => agregarRolPropio(rol),
    onSuccess: async () => {
      setError(null)
      await refreshStore()
      void queryClient.invalidateQueries({ queryKey: ['usuarios'] })
    },
    onError: (err) => setError(getErrorMessage(err)),
  })

  const quitarMutation = useMutation({
    mutationFn: (rol: RolGestionUsuario) => quitarRolPropio(rol),
    onSuccess: async () => {
      setError(null)
      await refreshStore()
      void queryClient.invalidateQueries({ queryKey: ['usuarios'] })
    },
    onError: (err) => setError(getErrorMessage(err)),
  })

  const isPending = agregarMutation.isPending || quitarMutation.isPending

  if (!userId) return null

  return (
    <div className="rounded-2xl border border-slate-700 bg-slate-900/85 p-5 shadow-lg">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Mis roles</p>
      <p className="mt-1 text-sm text-slate-400">
        Activá o desactivá tus roles de acceso al sistema.
      </p>

      {error ? (
        <div className="mt-3 rounded-xl border border-red-500/40 bg-red-950/40 p-3 text-sm text-red-200">
          {error}
        </div>
      ) : null}

      <div className="mt-4 flex flex-col gap-3">
        {ROLES_TOGGLEABLES.map(({ value, label }) => {
          const activo = rolesActivos.includes(value)
          const esUnico = activo && rolesActivos.length === 1

          return (
            <div key={value} className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <span
                  className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                    activo
                      ? 'bg-sky-500/20 text-sky-300'
                      : 'bg-slate-800 text-slate-500'
                  }`}
                >
                  {label}
                </span>
                {esUnico ? (
                  <span className="text-xs text-slate-600">único rol — no se puede desactivar</span>
                ) : null}
              </div>
              <button
                type="button"
                disabled={isPending || esUnico}
                onClick={() => {
                  if (activo) {
                    quitarMutation.mutate(value)
                  } else {
                    agregarMutation.mutate(value)
                  }
                }}
                className={`rounded-full px-3 py-1 text-xs font-semibold transition disabled:cursor-not-allowed disabled:opacity-40 ${
                  activo
                    ? 'border border-red-500/30 bg-red-500/10 text-red-300 hover:bg-red-500/20'
                    : 'border border-emerald-500/30 bg-emerald-500/10 text-emerald-300 hover:bg-emerald-500/20'
                }`}
              >
                {activo ? 'Desactivar' : 'Activar'}
              </button>
            </div>
          )
        })}
      </div>
    </div>
  )
}
