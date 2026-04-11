import useAuthStore from '../../stores/useAuthStore'

export function DashboardPage() {
  const logout = useAuthStore((s) => s.logout)
  const email = useAuthStore((s) => s.email)

  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-4 p-8">
      <h1 className="text-2xl font-bold text-gray-800">Panel del Organizador</h1>
      <p className="text-gray-500">Dashboard — {email}</p>
      <button
        onClick={logout}
        className="text-sm text-red-600 hover:underline"
      >
        Cerrar sesión
      </button>
    </div>
  )
}
