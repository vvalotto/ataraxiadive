import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchTorneos } from '../../api/torneo'
import useAuthStore from '../../stores/useAuthStore'

function formatearFecha(fechaIso: string): string {
  const fecha = new Date(fechaIso)
  return new Intl.DateTimeFormat('es-AR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(fecha)
}

export function AtletaDashboardPage() {
  const email = useAuthStore((s) => s.email)
  const logout = useAuthStore((s) => s.logout)
  const torneosQuery = useQuery({
    queryKey: ['torneos-atleta'],
    queryFn: fetchTorneos,
  })
  const torneosDisponibles = useMemo(
    () =>
      (torneosQuery.data ?? []).filter((torneo) => torneo.estado === 'INSCRIPCION_ABIERTA'),
    [torneosQuery.data],
  )

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,#daf1f7_0%,#d5eee4_22%,#f6f2e8_60%,#efe6d4_100%)] text-stone-900">
      <div className="mx-auto max-w-6xl px-5 py-6 sm:px-8 lg:px-10">
        <header className="rounded-[2rem] border border-teal-200/70 bg-white/80 p-6 shadow-[0_20px_60px_rgba(45,94,99,0.12)] backdrop-blur">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div className="max-w-3xl">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-teal-700">
                Atleta
              </p>
              <h1 className="mt-2 text-3xl font-semibold tracking-tight text-stone-900">
                Mi portal
              </h1>
              <p className="mt-2 text-sm text-stone-600">
                Perfil personal y torneos con inscripcion abierta para proximas competencias.
              </p>
            </div>
            <button
              type="button"
              onClick={logout}
              className="rounded-lg bg-stone-900 px-4 py-2 text-sm font-semibold text-stone-50"
            >
              Cerrar sesion
            </button>
          </div>
        </header>

        <main className="mt-6 grid gap-4 lg:grid-cols-[320px_minmax(0,1fr)]">
          <section className="rounded-[2rem] border border-teal-200/70 bg-white/85 p-5 shadow-[0_20px_60px_rgba(45,94,99,0.08)]">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal-700">
              Mi perfil
            </p>
            <div className="mt-5 space-y-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
                  Email
                </p>
                <p className="mt-1 text-base font-semibold text-stone-900">
                  {email ?? 'Sin email disponible'}
                </p>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
                  Rol
                </p>
                <p className="mt-1 text-base font-semibold text-stone-900">Atleta</p>
              </div>
            </div>
          </section>

          <section className="rounded-[2rem] border border-teal-200/70 bg-white/85 p-5 shadow-[0_20px_60px_rgba(45,94,99,0.08)]">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal-700">
                  Torneos disponibles
                </p>
                <h2 className="mt-1 text-xl font-semibold text-stone-900">
                  Inscripcion abierta
                </h2>
              </div>
              <p className="text-sm text-stone-600">
                {torneosDisponibles.length} torneos habilitados
              </p>
            </div>

            {torneosQuery.isLoading ? (
              <div className="mt-5 rounded-xl border border-stone-200 bg-stone-50 p-4 text-sm text-stone-600">
                Cargando torneos disponibles...
              </div>
            ) : null}

            {torneosQuery.isError ? (
              <div className="mt-5 rounded-xl border border-red-300 bg-red-50 p-4 text-sm text-red-900">
                No se pudieron cargar los torneos.
              </div>
            ) : null}

            {!torneosQuery.isLoading && !torneosQuery.isError && torneosDisponibles.length === 0 ? (
              <div className="mt-5 rounded-xl border border-stone-200 bg-stone-50 p-4 text-sm text-stone-600">
                No hay torneos disponibles en este momento
              </div>
            ) : null}

            {!torneosQuery.isLoading && !torneosQuery.isError && torneosDisponibles.length > 0 ? (
              <div className="mt-5 grid gap-4">
                {torneosDisponibles.map((torneo) => (
                  <article
                    key={torneo.torneo_id}
                    className="rounded-[1.5rem] border border-stone-200 bg-[linear-gradient(135deg,#ffffff_0%,#f3fbf7_100%)] p-5"
                  >
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
                      Torneo
                    </p>
                    <h3 className="mt-2 text-lg font-semibold text-stone-900">{torneo.nombre}</h3>
                    <p className="mt-3 text-sm text-stone-600">
                      {torneo.sede.nombre}, {torneo.sede.ciudad}, {torneo.sede.pais}
                    </p>
                    <p className="mt-2 text-sm text-stone-600">
                      {formatearFecha(torneo.fecha_inicio)} al {formatearFecha(torneo.fecha_fin)}
                    </p>
                  </article>
                ))}
              </div>
            ) : null}
          </section>
        </main>
      </div>
    </div>
  )
}
