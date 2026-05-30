import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useLocation } from 'react-router-dom'
import { fetchTorneos, type EstadoTorneo, type TorneoDto } from '../../api/torneo'
import { OrganizadorLayout } from '../../components/organizador/OrganizadorLayout'


const ESTADO_TORNEO_LABELS: Record<EstadoTorneo, string> = {
  CREADO: 'Creado',
  INSCRIPCION_ABIERTA: 'Inscripción abierta',
  PREPARACION: 'Preparación',
  EJECUCION: 'En ejecución',
  PREMIACION: 'Premiación',
  CERRADO: 'Cerrado',
  CANCELADO: 'Cancelado',
}

type FiltroTorneos = 'vigentes' | 'historico'

const FILTROS_TORNEOS: Array<{ value: FiltroTorneos; label: string }> = [
  { value: 'vigentes', label: 'Vigentes' },
  { value: 'historico', label: 'Histórico' },
]

function formatEstadoTorneo(estado: string): string {
  return ESTADO_TORNEO_LABELS[estado as EstadoTorneo] ?? estado
}

function esTorneoVigente(estado: EstadoTorneo): boolean {
  return (
    estado === 'CREADO' ||
    estado === 'INSCRIPCION_ABIERTA' ||
    estado === 'PREPARACION' ||
    estado === 'EJECUCION' ||
    estado === 'PREMIACION'
  )
}

function esTorneoHistorico(estado: EstadoTorneo): boolean {
  return estado === 'CERRADO' || estado === 'CANCELADO'
}

function filtrarTorneos(torneos: TorneoDto[], filtro: FiltroTorneos): TorneoDto[] {
  const filtrados =
    filtro === 'vigentes'
      ? torneos.filter((torneo) => esTorneoVigente(torneo.estado))
      : torneos.filter((torneo) => esTorneoHistorico(torneo.estado))

  return filtrados
    .map((torneo, index) => ({ torneo, index }))
    .sort((a, b) => {
      const fechaComparison = a.torneo.fecha_inicio.localeCompare(b.torneo.fecha_inicio)
      if (fechaComparison !== 0) return fechaComparison
      return a.index - b.index
    })
    .map(({ torneo }) => torneo)
}

function formatFechaCorta(fecha: string): string {
  return new Date(`${fecha}T00:00:00`).toLocaleDateString('es-AR', {
    day: 'numeric',
    month: 'short',
  })
}

function formatFechaCompleta(fecha: string): string {
  return new Date(`${fecha}T00:00:00`).toLocaleDateString('es-AR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

function formatFechaTorneo(inicio: string, fin: string): string {
  if (inicio === fin) return formatFechaCompleta(inicio)
  return `${formatFechaCorta(inicio)}-${formatFechaCompleta(fin)}`
}

function emptyMessage(filtro: FiltroTorneos): string {
  if (filtro === 'vigentes') return 'No hay torneos vigentes.'
  return 'No hay torneos en el histórico.'
}

function historicalCardClass(estado: EstadoTorneo): string {
  if (estado === 'EJECUCION') {
    return 'border-emerald-500/40 bg-emerald-950/25 shadow-[0_20px_60px_rgba(6,78,59,0.22)]'
  }

  if (estado === 'INSCRIPCION_ABIERTA') {
    return 'border-amber-500/40 bg-amber-950/25 shadow-[0_20px_60px_rgba(120,53,15,0.22)]'
  }

  if (estado === 'CANCELADO') {
    return 'border-red-500/40 bg-red-950/30 shadow-[0_20px_60px_rgba(127,29,29,0.22)]'
  }

  if (estado === 'CERRADO') {
    return 'border-sky-500/40 bg-sky-950/25 shadow-[0_20px_60px_rgba(12,74,110,0.22)]'
  }

  return 'border-slate-700 bg-slate-900/80 shadow-[0_20px_60px_rgba(2,6,23,0.32)]'
}

function historicalTextClass(estado: EstadoTorneo): string {
  if (estado === 'EJECUCION') return 'text-emerald-100'
  if (estado === 'INSCRIPCION_ABIERTA') return 'text-amber-100'
  if (estado === 'CANCELADO') return 'text-red-100'
  if (estado === 'CERRADO') return 'text-sky-100'
  return 'text-slate-300'
}

function stateAccentClass(estado: EstadoTorneo): string {
  if (estado === 'EJECUCION') return 'text-emerald-300'
  if (estado === 'INSCRIPCION_ABIERTA') return 'text-amber-300'
  if (estado === 'CANCELADO') return 'text-red-300'
  if (estado === 'CERRADO') return 'text-sky-300'
  return 'text-slate-400'
}

function actionClass(estado: EstadoTorneo): string {
  if (estado === 'EJECUCION') {
    return 'border-emerald-400/40 bg-emerald-950/40 text-emerald-100'
  }
  if (estado === 'INSCRIPCION_ABIERTA') {
    return 'border-amber-400/40 bg-amber-950/40 text-amber-100'
  }
  if (estado === 'CANCELADO') {
    return 'border-red-400/40 bg-red-950/40 text-red-100'
  }
  if (estado === 'CERRADO') {
    return 'border-sky-400/40 bg-sky-950/40 text-sky-100'
  }
  return 'border-slate-600 bg-slate-800 text-slate-100'
}

export function DashboardPage() {
  const location = useLocation()

  const [filtro, setFiltro] = useState<FiltroTorneos>('vigentes')
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
      title="Inicio"
      subtitle="Tus torneos y acceso rápido a cada uno"
      showTournamentNavigation={false}
    >
      <div className="flex justify-end">
        <Link
          to="/organizador/torneos/nuevo"
          className="rounded-full bg-sky-500 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-slate-950"
        >
          Nuevo torneo
        </Link>
      </div>
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
        <>
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
        </>
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
              className={`rounded-[2rem] border p-5 ${
                filtro === 'historico' ||
                torneo.estado === 'EJECUCION' ||
                torneo.estado === 'INSCRIPCION_ABIERTA'
                  ? historicalCardClass(torneo.estado)
                  : 'border-slate-700 bg-slate-900/80 shadow-[0_20px_60px_rgba(2,6,23,0.32)]'
              }`}
            >
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p
                    className={`text-xs font-semibold uppercase tracking-[0.18em] ${stateAccentClass(
                      torneo.estado,
                    )}`}
                  >
                    {filtro === 'vigentes' ? 'Torneo vigente' : 'Torneo histórico'}
                  </p>
                  <h2 className="mt-2 text-xl font-semibold text-white">{torneo.nombre}</h2>
                  <p
                    className={`mt-2 text-sm ${historicalTextClass(torneo.estado)}`}
                  >
                    {torneo.sede.nombre}, {torneo.sede.ciudad} · {formatEstadoTorneo(torneo.estado)}
                  </p>
                  <p className={`mt-1 text-xs ${historicalTextClass(torneo.estado)}`}>
                    {formatFechaTorneo(torneo.fecha_inicio, torneo.fecha_fin)}
                  </p>
                </div>
                <Link
                  to={`/organizador/panel?torneo_id=${torneo.torneo_id}`}
                  className={`rounded-full border px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] ${actionClass(
                    torneo.estado,
                  )}`}
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
