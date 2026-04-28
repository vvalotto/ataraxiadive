import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useLocation } from 'react-router-dom'
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
  const location = useLocation()
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
            to="/cambiar-password"
            className="rounded-full border border-slate-600 bg-slate-800 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-slate-100"
          >
            Password
          </Link>
          <Link
            to="/organizador/usuarios"
            className="rounded-full border border-slate-600 bg-slate-800 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-slate-100"
          >
            Usuarios
          </Link>
          <Link
            to="/organizador/torneos/nuevo"
            className="rounded-full bg-sky-500 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-slate-950"
          >
            Nuevo torneo
          </Link>
          <button
            type="button"
            onClick={logout}
            className="rounded-full border border-slate-600 bg-slate-900 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-slate-100"
          >
            Cerrar sesion
          </button>
        </>
      }
    >
      {location.state && (location.state as { passwordUpdated?: boolean }).passwordUpdated ? (
        <section className="rounded-[2rem] border border-emerald-300 bg-emerald-50 p-5 text-sm text-emerald-900">
          Contrasena actualizada correctamente.
        </section>
      ) : null}

      {torneosQuery.isLoading ? (
        <section className="rounded-[2rem] border border-slate-700 bg-slate-900/70 p-5 text-sm text-slate-300">
          Cargando torneos...
        </section>
      ) : null}

      {torneosQuery.isError ? (
        <section className="rounded-[2rem] border border-red-500/40 bg-red-950/50 p-5 text-sm text-red-100">
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
                    ? 'rounded-full border border-sky-400 bg-sky-400/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-sky-300'
                    : 'rounded-full border border-slate-700 bg-slate-900 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-slate-300'
                }
              >
                {item.label}
              </button>
            )
          })}
        </section>
      ) : null}

      {!torneosQuery.isLoading && !torneosQuery.isError && torneosFiltrados.length === 0 ? (
        <section className="rounded-[2rem] border border-slate-700 bg-slate-900/70 p-5 text-sm text-slate-300">
          {emptyMessage(filtro)}
        </section>
      ) : null}

      {!torneosQuery.isLoading && !torneosQuery.isError
        ? torneosFiltrados.map((torneo) => (
            <article
              key={torneo.torneo_id}
              className="rounded-[2rem] border border-slate-700 bg-slate-900/80 p-5 shadow-[0_20px_60px_rgba(2,6,23,0.32)]"
            >
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                    Torneo
                  </p>
                  <h2 className="mt-2 text-xl font-semibold text-white">{torneo.nombre}</h2>
                  <p className="mt-2 text-sm text-slate-300">
                    {torneo.sede.nombre}, {torneo.sede.ciudad} · {formatEstadoTorneo(torneo.estado)}
                  </p>
                </div>
                <Link
                  to={`/organizador/torneo/${torneo.torneo_id}`}
                  className="rounded-full border border-slate-600 bg-slate-800 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-slate-100"
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
