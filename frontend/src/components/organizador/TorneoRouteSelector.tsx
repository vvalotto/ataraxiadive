import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { fetchTorneos, type EstadoTorneo } from '../../api/torneo'

interface TorneoRouteSelectorProps {
  description: string
  ctaLabel: string
  buildHref: (torneoId: string) => string
}

const ESTADO_TORNEO_LABELS: Record<EstadoTorneo, string> = {
  CREADO: 'Creado',
  INSCRIPCION_ABIERTA: 'Inscripción abierta',
  PREPARACION: 'Preparación',
  EJECUCION: 'En ejecución',
  PREMIACION: 'Premiación',
  CERRADO: 'Cerrado',
  CANCELADO: 'Cancelado',
}

export function TorneoRouteSelector({
  description,
  ctaLabel,
  buildHref,
}: TorneoRouteSelectorProps) {
  const torneosQuery = useQuery({
    queryKey: ['torneos-organizador'],
    queryFn: fetchTorneos,
  })

  if (torneosQuery.isLoading) {
    return (
      <section className="rounded-[2rem] border border-slate-700 bg-slate-900/70 p-5 text-sm text-slate-300">
        Cargando torneos...
      </section>
    )
  }

  if (torneosQuery.isError) {
    return (
      <section className="rounded-[2rem] border border-red-500/40 bg-red-950/50 p-5 text-sm text-red-100">
        No se pudieron cargar los torneos.
      </section>
    )
  }

  if ((torneosQuery.data ?? []).length === 0) {
    return (
      <section className="rounded-[2rem] border border-slate-700 bg-slate-900/70 p-5 text-sm text-slate-300">
        No hay torneos disponibles para esta sección.
      </section>
    )
  }

  return (
    <>
      <section className="rounded-[2rem] border border-slate-700 bg-slate-900/75 p-5 text-sm text-slate-300">
        {description}
      </section>

      {(torneosQuery.data ?? []).map((torneo) => (
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
                {torneo.sede.nombre}, {torneo.sede.ciudad} · {ESTADO_TORNEO_LABELS[torneo.estado]}
              </p>
            </div>
            <Link
              to={buildHref(torneo.torneo_id)}
              className="rounded-full border border-sky-400 bg-sky-400/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-sky-300"
            >
              {ctaLabel}
            </Link>
          </div>
        </article>
      ))}
    </>
  )
}
