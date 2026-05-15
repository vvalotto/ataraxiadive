import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { fetchTorneos, listarDisciplinasTorneo } from '../../api/torneo'
import {
  ApiError,
  fetchAtletaMe,
  listarInscripcionesDeAtleta,
  type InscriptoDto,
} from '../../api/registro'
import { AtletaShell } from '../../components/atleta/AtletaShell'
import {
  formatDisciplina,
  formatFecha,
  getEstadoTorneoLabel,
  isTorneoAbierto,
  isTorneoProximo,
} from './portalData'

interface TorneoDetalle {
  torneo: Awaited<ReturnType<typeof fetchTorneos>>[number]
  disciplinas: Awaited<ReturnType<typeof listarDisciplinasTorneo>>
}

interface TorneoInscriptoDetalle extends TorneoDetalle {
  inscripcion: InscriptoDto
}

function sortDetalleByFecha<T extends { torneo: { fecha_inicio: string } }>(items: T[]): T[] {
  return [...items].sort(
    (left, right) =>
      new Date(left.torneo.fecha_inicio).getTime() - new Date(right.torneo.fecha_inicio).getTime(),
  )
}

async function loadTorneos() {
  const atleta = await fetchAtletaMe().catch((err) =>
    err instanceof ApiError && err.status === 404 ? null : Promise.reject(err),
  )
  const [torneos, inscripciones] = await Promise.all([
    fetchTorneos(),
    atleta ? listarInscripcionesDeAtleta(atleta.atleta_id) : Promise.resolve([]),
  ])

  const inscripcionesByTorneoId = new Map(
    inscripciones.map((inscripcion) => [inscripcion.torneo_id, inscripcion]),
  )
  const torneosInscriptos = new Set(inscripcionesByTorneoId.keys())

  const detalle = await Promise.all(
    torneos.map(async (torneo) => {
      try {
        const disciplinas = await listarDisciplinasTorneo(torneo.torneo_id)
        return { torneo, disciplinas }
      } catch {
        return { torneo, disciplinas: [] }
      }
    }),
  )

  return {
    cerrados: sortDetalleByFecha(
      detalle
        .map((item): TorneoInscriptoDetalle | null => {
          const inscripcion = inscripcionesByTorneoId.get(item.torneo.torneo_id)
          if (!inscripcion) return null
          if (item.torneo.estado !== 'CERRADO') return null
          return { ...item, inscripcion }
        })
        .filter((item): item is TorneoInscriptoDetalle => item !== null),
    ).reverse(),
    misTorneos: sortDetalleByFecha(
      detalle
        .map((item): TorneoInscriptoDetalle | null => {
          const inscripcion = inscripcionesByTorneoId.get(item.torneo.torneo_id)
          if (!inscripcion) return null
          if (!['EJECUCION', 'PREMIACION'].includes(item.torneo.estado)) return null
          return { ...item, inscripcion }
        })
        .filter((item): item is TorneoInscriptoDetalle => item !== null),
    ),
    abiertos: sortDetalleByFecha(
      detalle.filter(
        (item) => isTorneoAbierto(item.torneo.estado) && !torneosInscriptos.has(item.torneo.torneo_id),
      ),
    ),
    proximos: sortDetalleByFecha(detalle.filter((item) => isTorneoProximo(item.torneo.estado))),
  }
}

export function AtletaTorneosPage() {
  const query = useQuery({
    queryKey: ['atleta-torneos'],
    queryFn: loadTorneos,
  })

  return (
    <AtletaShell title="Torneos" subtitle="Explorá torneos publicados y revisá si la inscripción está abierta.">
      {query.isLoading ? (
        <div className="rounded-3xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-300">
          Cargando torneos...
        </div>
      ) : null}

      {query.isError ? (
        <div className="rounded-3xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-100">
          No se pudieron cargar los torneos.
        </div>
      ) : null}

      {query.data ? (
        <div className="space-y-5">
          <section>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-emerald-300">
              Mis torneos
            </p>
            <div className="mt-3 space-y-3">
              {query.data.misTorneos.length === 0 ? (
                <div className="rounded-3xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-400">
                  No hay torneos activos en este momento.
                </div>
              ) : null}

              {query.data.misTorneos.map(({ torneo, inscripcion }) => (
                <Link
                  key={torneo.torneo_id}
                  to={`/atleta/torneos/${torneo.torneo_id}`}
                  className="block rounded-3xl border border-emerald-500/30 bg-emerald-500/10 p-4"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h2 className="text-base font-semibold text-white">{torneo.nombre}</h2>
                      <p className="mt-1 text-sm text-slate-300">
                        {formatFecha(torneo.fecha_inicio)} · {torneo.sede.nombre}, {torneo.sede.ciudad}
                      </p>
                    </div>
                    <span className="rounded-full border border-emerald-400/40 bg-emerald-400/10 px-3 py-1 text-xs font-semibold text-emerald-200">
                      {getEstadoTorneoLabel(torneo.estado)}
                    </span>
                  </div>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {inscripcion.disciplinas.length === 0 ? (
                      <span className="rounded-full border border-slate-700 bg-slate-900/80 px-3 py-1 text-xs font-semibold text-slate-400">
                        Por definir
                      </span>
                    ) : null}
                    {inscripcion.disciplinas.map((disciplina) => (
                      <span
                        key={disciplina}
                        className="rounded-full border border-emerald-400/30 bg-slate-950/40 px-3 py-1 text-xs font-semibold text-emerald-100"
                      >
                        {formatDisciplina(disciplina)}
                      </span>
                    ))}
                  </div>
                  <div className="mt-3 flex min-h-9 items-center justify-center rounded-2xl border border-sky-400/30 bg-sky-400/10 px-4 py-2 text-sm font-semibold text-sky-300">
                    Ver detalle
                  </div>
                </Link>
              ))}
            </div>
          </section>

          <section>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-sky-400">
              Inscripciones abiertas
            </p>
            <div className="mt-3 space-y-3">
              {query.data.abiertos.length === 0 ? (
                <div className="rounded-3xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-400">
                  No hay torneos con inscripción abierta.
                </div>
              ) : null}

              {query.data.abiertos.map(({ torneo, disciplinas }) => (
                <Link
                  key={torneo.torneo_id}
                  to={`/atleta/torneos/${torneo.torneo_id}`}
                  className="block rounded-3xl border border-slate-800 bg-slate-900 p-4"
                >
                  <div>
                    <h2 className="text-base font-semibold text-white">{torneo.nombre}</h2>
                    <p className="mt-1 text-sm text-slate-400">
                      {formatFecha(torneo.fecha_inicio)} · {torneo.sede.nombre}, {torneo.sede.ciudad}
                    </p>
                  </div>
                  <p className="mt-3 text-sm text-slate-300">
                    Disciplinas: {disciplinas.map((item) => formatDisciplina(item.disciplina)).join(' · ') || 'Por definir'}
                  </p>
                  <p className="mt-2 text-sm font-semibold text-sky-300">Ver detalle →</p>
                </Link>
              ))}
            </div>
          </section>

          <section>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-500">
              Próximos
            </p>
            <div className="mt-3 space-y-3">
              {query.data.proximos.length === 0 ? (
                <div className="rounded-3xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-400">
                  No hay torneos próximos publicados.
                </div>
              ) : null}

              {query.data.proximos.map(({ torneo }) => (
                <div
                  key={torneo.torneo_id}
                  className="flex items-center justify-between gap-3 rounded-2xl border border-slate-800 bg-slate-900/60 px-4 py-3"
                >
                  <div>
                    <p className="text-sm font-semibold text-slate-200">{torneo.nombre}</p>
                    <p className="mt-0.5 text-xs text-slate-500">
                      {formatFecha(torneo.fecha_inicio)} · {torneo.sede.ciudad}
                    </p>
                  </div>
                  <span className="shrink-0 rounded-full border border-slate-700 px-2.5 py-1 text-xs font-semibold text-slate-500">
                    Próximo
                  </span>
                </div>
              ))}
            </div>
          </section>

          {query.data.cerrados.length > 0 ? (
            <section>
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-amber-400">
                Historial
              </p>
              <div className="mt-3 space-y-3">
                {query.data.cerrados.map(({ torneo }) => (
                  <div
                    key={torneo.torneo_id}
                    className="rounded-3xl border border-slate-800 bg-slate-900 p-4"
                  >
                    <div>
                      <h2 className="text-base font-semibold text-white">{torneo.nombre}</h2>
                      <p className="mt-1 text-sm text-slate-400">
                        {formatFecha(torneo.fecha_inicio)} · {torneo.sede.nombre}, {torneo.sede.ciudad}
                      </p>
                    </div>
                    <Link
                      to={`/atleta/torneos/${torneo.torneo_id}`}
                      className="mt-3 flex min-h-9 items-center justify-center rounded-2xl border border-amber-400/30 bg-amber-400/10 px-4 py-2 text-sm font-semibold text-amber-300"
                    >
                      Ver resultados
                    </Link>
                  </div>
                ))}
              </div>
            </section>
          ) : null}
        </div>
      ) : null}
    </AtletaShell>
  )
}
