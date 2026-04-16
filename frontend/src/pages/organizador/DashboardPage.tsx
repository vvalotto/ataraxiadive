import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { fetchTorneos } from '../../api/torneo'
import { OrganizadorLayout } from '../../components/organizador/OrganizadorLayout'
import useAuthStore from '../../stores/useAuthStore'

export function DashboardPage() {
  const logout = useAuthStore((s) => s.logout)
  const email = useAuthStore((s) => s.email)
  const torneosQuery = useQuery({
    queryKey: ['torneos-organizador'],
    queryFn: fetchTorneos,
  })

  return (
    <OrganizadorLayout
      title="Panel del organizador"
      subtitle={email ? `Sesion activa: ${email}` : 'Gestion de auditoria y seguimiento'}
      actions={
        <button
          type="button"
          onClick={logout}
          className="rounded-full bg-stone-900 px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-stone-50"
        >
          Cerrar sesion
        </button>
      }
    >
      {torneosQuery.isLoading ? (
        <section className="rounded-[2rem] border border-stone-300/80 bg-white/80 p-5 text-sm text-stone-600">
          Cargando torneos...
        </section>
      ) : null}

      {torneosQuery.isError ? (
        <section className="rounded-[2rem] border border-red-300/60 bg-red-50 p-5 text-sm text-red-900">
          No se pudieron cargar los torneos.
        </section>
      ) : null}

      {!torneosQuery.isLoading && !torneosQuery.isError && torneosQuery.data?.length === 0 ? (
        <section className="rounded-[2rem] border border-stone-300/80 bg-white/80 p-5 text-sm text-stone-600">
          No hay torneos disponibles para auditoria.
        </section>
      ) : null}

      {!torneosQuery.isLoading && !torneosQuery.isError
        ? torneosQuery.data?.map((torneo) => (
            <article
              key={torneo.torneo_id}
              className="rounded-[2rem] border border-stone-300/80 bg-white/85 p-5 shadow-[0_20px_60px_rgba(120,93,54,0.08)]"
            >
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
                    Torneo
                  </p>
                  <h2 className="mt-2 text-xl font-semibold text-stone-900">{torneo.nombre}</h2>
                  <p className="mt-2 text-sm text-stone-600">
                    {torneo.sede.nombre}, {torneo.sede.ciudad} · {torneo.estado}
                  </p>
                </div>
                <Link
                  to={`/organizador/torneos/${torneo.torneo_id}/competencias`}
                  className="rounded-full border border-stone-900 px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-stone-900"
                >
                  Ver competencias
                </Link>
              </div>
            </article>
          ))
        : null}
    </OrganizadorLayout>
  )
}
