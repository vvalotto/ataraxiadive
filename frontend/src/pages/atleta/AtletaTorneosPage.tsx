import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { fetchTorneos } from '../../api/torneo'
import { AtletaShell } from '../../components/atleta/AtletaShell'
import {
  formatDisciplina,
  formatFecha,
  getEstadoTorneoLabel,
  isTorneoAbierto,
  isTorneoProximo,
} from './portalData'
import { listarDisciplinasTorneo } from '../../api/torneo'

function sortDetalleByFecha<T extends { torneo: { fecha_inicio: string } }>(items: T[]): T[] {
  return [...items].sort(
    (left, right) =>
      new Date(left.torneo.fecha_inicio).getTime() - new Date(right.torneo.fecha_inicio).getTime(),
  )
}

async function loadTorneos() {
  const torneos = await fetchTorneos()
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
    abiertos: sortDetalleByFecha(detalle.filter((item) => isTorneoAbierto(item.torneo.estado))),
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
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h2 className="text-base font-semibold text-white">{torneo.nombre}</h2>
                      <p className="mt-1 text-sm text-slate-400">
                        {formatFecha(torneo.fecha_inicio)} · {torneo.sede.nombre}, {torneo.sede.ciudad}
                      </p>
                    </div>
                    <span className="rounded-full border border-sky-500/40 bg-sky-500/10 px-3 py-1 text-xs font-semibold text-sky-300">
                      {getEstadoTorneoLabel(torneo.estado)}
                    </span>
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
                  className="rounded-3xl border border-slate-800 bg-slate-900/70 p-4 opacity-80"
                >
                  <h2 className="text-base font-semibold text-white">{torneo.nombre}</h2>
                  <p className="mt-1 text-sm text-slate-400">
                    {formatFecha(torneo.fecha_inicio)} · {torneo.sede.ciudad}
                  </p>
                  <p className="mt-2 text-sm text-slate-500">Aún sin inscripción habilitada.</p>
                </div>
              ))}
            </div>
          </section>
        </div>
      ) : null}
    </AtletaShell>
  )
}
