import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { fetchTorneos, type EstadoTorneo, type TorneoDto } from '../../api/torneo'
import { OrganizadorLayout } from '../../components/organizador/OrganizadorLayout'
import useAuthStore from '../../stores/useAuthStore'

const ESTADO_TORNEO_LABELS: Record<string, string> = {
  CREADO: 'Creado',
  INSCRIPCION_ABIERTA: 'Inscripción abierta',
  PREPARACION: 'Preparación',
  EJECUCION: 'En ejecución',
  PREMIACION: 'Premiación',
  CERRADO: 'Cerrado',
  CANCELADO: 'Cancelado',
}

type FiltroTorneos = 'abiertos' | 'todos' | 'cerrados' | 'cancelados'

const FILTROS_TORNEOS: Array<{ value: FiltroTorneos; label: string }> = [
  { value: 'todos', label: 'Todos' },
  { value: 'abiertos', label: 'Abiertos' },
  { value: 'cerrados', label: 'Cerrados' },
  { value: 'cancelados', label: 'Cancelados' },
]

function formatEstadoTorneo(estado: string): string {
  return ESTADO_TORNEO_LABELS[estado] ?? estado
}

function esTorneoAbierto(estado: EstadoTorneo): boolean {
  return estado !== 'CERRADO' && estado !== 'CANCELADO'
}

function filtrarTorneos(torneos: TorneoDto[], filtro: FiltroTorneos): TorneoDto[] {
  if (filtro === 'todos') return torneos
  if (filtro === 'abiertos') return torneos.filter((torneo) => esTorneoAbierto(torneo.estado))
  if (filtro === 'cerrados') return torneos.filter((torneo) => torneo.estado === 'CERRADO')
  return torneos.filter((torneo) => torneo.estado === 'CANCELADO')
}

function emptyMessage(filtro: FiltroTorneos): string {
  if (filtro === 'abiertos') return 'No hay torneos abiertos.'
  if (filtro === 'cerrados') return 'No hay torneos cerrados.'
  if (filtro === 'cancelados') return 'No hay torneos cancelados.'
  return 'No hay torneos disponibles.'
}

export function DashboardPage() {
  const logout = useAuthStore((s) => s.logout)
  const email = useAuthStore((s) => s.email)
  const [filtro, setFiltro] = useState<FiltroTorneos>('abiertos')
  const torneosQuery = useQuery({
    queryKey: ['torneos-organizador'],
    queryFn: fetchTorneos,
  })
  const torneosFiltrados = useMemo(
    () => filtrarTorneos(torneosQuery.data ?? [], filtro),
    [filtro, torneosQuery.data],
  )

  return (
    <OrganizadorLayout
      title="Panel del organizador"
      subtitle={email ? `Sesion activa: ${email}` : 'Gestion de auditoria y seguimiento'}
      actions={
        <>
          <Link
            to="/organizador/usuarios"
            className="rounded-lg border border-stone-900 px-4 py-2 text-sm font-semibold text-stone-900"
          >
            Usuarios
          </Link>
          <Link
            to="/organizador/torneos/nuevo"
            className="rounded-lg bg-emerald-800 px-4 py-2 text-sm font-semibold text-white"
          >
            Nuevo torneo
          </Link>
          <button
            type="button"
            onClick={logout}
            className="rounded-lg bg-stone-900 px-4 py-2 text-sm font-semibold text-stone-50"
          >
            Cerrar sesion
          </button>
        </>
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

      {!torneosQuery.isLoading && !torneosQuery.isError ? (
        <section className="flex flex-wrap items-center gap-2">
          {FILTROS_TORNEOS.map((item) => {
            const isActive = filtro === item.value
            return (
              <button
                key={item.value}
                type="button"
                onClick={() => setFiltro(item.value)}
                className={
                  isActive
                    ? 'rounded-lg bg-stone-900 px-4 py-2 text-sm font-semibold text-white'
                    : 'rounded-lg border border-stone-300 bg-white/80 px-4 py-2 text-sm font-semibold text-stone-700'
                }
              >
                {item.label}
              </button>
            )
          })}
        </section>
      ) : null}

      {!torneosQuery.isLoading && !torneosQuery.isError && torneosFiltrados.length === 0 ? (
        <section className="rounded-[2rem] border border-stone-300/80 bg-white/80 p-5 text-sm text-stone-600">
          {emptyMessage(filtro)}
        </section>
      ) : null}

      {!torneosQuery.isLoading && !torneosQuery.isError
        ? torneosFiltrados.map((torneo) => (
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
                    {torneo.sede.nombre}, {torneo.sede.ciudad} · {formatEstadoTorneo(torneo.estado)}
                  </p>
                </div>
                <Link
                  to={`/organizador/torneo/${torneo.torneo_id}`}
                  className="rounded-lg border border-stone-900 px-4 py-2 text-sm font-semibold text-stone-900"
                >
                  Gestionar
                </Link>
              </div>
            </article>
          ))
        : null}
    </OrganizadorLayout>
  )
}
