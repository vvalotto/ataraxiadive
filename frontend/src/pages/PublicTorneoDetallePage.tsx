import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { fetchTorneo, type EstadoTorneo } from '../api/torneo'
import useAuthStore from '../stores/useAuthStore'
import { formatFecha } from './atleta/portalData'

const ESTADO_BADGE: Record<EstadoTorneo, { label: string; classes: string }> = {
  CREADO: { label: 'Próximo', classes: 'border-slate-600/40 bg-slate-600/10 text-slate-300' },
  INSCRIPCION_ABIERTA: { label: 'Inscripciones abiertas', classes: 'border-sky-500/40 bg-sky-500/10 text-sky-300' },
  PREPARACION: { label: 'Preparación', classes: 'border-yellow-500/40 bg-yellow-500/10 text-yellow-300' },
  EJECUCION: { label: 'En ejecución', classes: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300' },
  PREMIACION: { label: 'Premiación', classes: 'border-amber-400/40 bg-amber-400/10 text-amber-300' },
  CERRADO: { label: 'Cerrado', classes: 'border-slate-700/40 bg-slate-700/10 text-slate-400' },
  CANCELADO: { label: 'Cancelado', classes: 'border-red-500/40 bg-red-500/10 text-red-400' },
}

export function PublicTorneoDetallePage() {
  const { torneoId } = useParams<{ torneoId: string }>()
  const rol = useAuthStore((s) => s.rol)

  const { data: torneo, isLoading, isError } = useQuery({
    queryKey: ['torneo', torneoId],
    queryFn: () => fetchTorneo(torneoId ?? ''),
    enabled: Boolean(torneoId),
  })

  const portalLink =
    rol === 'juez' ? '/juez/disciplinas'
    : rol === 'organizador' ? '/organizador/torneo'
    : rol === 'atleta' ? '/atleta'
    : null

  const puedeVerPodios = torneo ? ['PREMIACION', 'CERRADO'].includes(torneo.estado) : false

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 bg-slate-900/80 px-4 py-3">
        <div className="mx-auto flex max-w-lg items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-[0.24em] text-sky-400">
            AtaraxiaDive
          </span>
          {portalLink ? (
            <Link
              to={portalLink}
              className="rounded-2xl bg-sky-500 px-4 py-2 text-xs font-semibold text-slate-950 transition-colors hover:bg-sky-400"
            >
              Mi portal
            </Link>
          ) : (
            <Link
              to="/login"
              className="rounded-2xl border border-slate-700 bg-slate-800 px-4 py-2 text-xs font-semibold text-slate-200 transition-colors hover:bg-slate-700"
            >
              Iniciar sesión
            </Link>
          )}
        </div>
      </header>

      <main className="mx-auto max-w-lg px-4 py-6">
        <Link
          to="/portalapnea"
          className="mb-4 flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200"
        >
          ← Torneos
        </Link>

        {isLoading ? (
          <div className="rounded-3xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-300">
            Cargando torneo...
          </div>
        ) : null}

        {isError ? (
          <div className="rounded-3xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-100">
            No se pudo cargar el torneo.
          </div>
        ) : null}

        {torneo ? (
          <div className="rounded-3xl border border-slate-800 bg-slate-900 p-5">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <h1 className="text-xl font-semibold text-white">{torneo.nombre}</h1>
                <p className="mt-1 text-sm text-slate-400">
                  {formatFecha(torneo.fecha_inicio)}
                  {torneo.fecha_fin !== torneo.fecha_inicio
                    ? ` — ${formatFecha(torneo.fecha_fin)}`
                    : null}{' '}
                  · {torneo.sede.ciudad}, {torneo.sede.pais}
                </p>
                <p className="mt-0.5 text-sm text-slate-500">
                  {torneo.entidad_organizadora.nombre}
                </p>
              </div>
              <span
                className={`shrink-0 rounded-full border px-3 py-1 text-xs font-semibold ${ESTADO_BADGE[torneo.estado].classes}`}
              >
                {ESTADO_BADGE[torneo.estado].label}
              </span>
            </div>

            <div className="mt-5 flex flex-col gap-3 sm:flex-row">
              <Link
                to={`/portalapnea/${torneoId}/resultados`}
                className="flex-1 rounded-2xl bg-sky-500 px-4 py-3 text-center text-sm font-semibold text-slate-950 transition-colors hover:bg-sky-400"
              >
                Resultados
              </Link>
              {puedeVerPodios ? (
                <Link
                  to={`/portalapnea/${torneoId}/podios`}
                  className="flex-1 rounded-2xl border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-center text-sm font-semibold text-amber-300 transition-colors hover:bg-amber-500/20"
                >
                  Podios
                </Link>
              ) : (
                <button
                  disabled
                  title="Disponible al finalizar la competencia"
                  className="flex-1 cursor-not-allowed rounded-2xl border border-slate-700 bg-slate-800/50 px-4 py-3 text-center text-sm font-semibold text-slate-600"
                >
                  Podios
                </button>
              )}
            </div>
          </div>
        ) : null}
      </main>
    </div>
  )
}
