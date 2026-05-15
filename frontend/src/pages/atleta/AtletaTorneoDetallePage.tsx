import { useQueries, useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { fetchTorneo } from '../../api/torneo'
import { fetchAtletaMe, listarInscripcionesDeAtleta } from '../../api/registro'
import { fetchOverall, fetchRankingCompetencia } from '../../api/resultados'
import { fetchGrillaCompetencia } from '../../api/competencia'
import { AtletaShell } from '../../components/atleta/AtletaShell'
import {
  GrupoResultados,
  findMiResultado,
  type ResultadoEntry,
} from '../../components/atleta/GrupoResultados'
import {
  formatDisciplina,
  formatFecha,
  getEstadoTorneoLabel,
  loadAtletaPortalSnapshot,
} from './portalData'

async function loadTorneoDetalle(torneoId: string) {
  const [torneo, atleta] = await Promise.all([
    fetchTorneo(torneoId),
    fetchAtletaMe(),
  ])
  const inscripciones = await listarInscripcionesDeAtleta(atleta.atleta_id)
  const inscripcion = inscripciones.find((item) => item.torneo_id === torneoId) ?? null

  return { torneo, inscripcion }
}

export function AtletaTorneoDetallePage() {
  const { torneoId } = useParams<{ torneoId: string }>()
  const query = useQuery({
    queryKey: ['atleta-torneo-detalle', torneoId],
    queryFn: () => loadTorneoDetalle(torneoId ?? ''),
    enabled: Boolean(torneoId),
  })

  const esCerrado = query.data?.torneo.estado === 'CERRADO'
  const tieneInscripcion = Boolean(query.data?.inscripcion)

  const snapshotQuery = useQuery({
    queryKey: ['atleta-torneo-detalle-snapshot', torneoId],
    queryFn: loadAtletaPortalSnapshot,
    enabled: esCerrado && tieneInscripcion,
  })

  const entradaTorneo = (snapshotQuery.data?.entries ?? []).filter(
    (e) => e.torneo.torneo_id === torneoId,
  )
  const atletaId = snapshotQuery.data?.atleta?.atleta_id ?? ''

  const rankingQueries = useQueries({
    queries: entradaTorneo.map((entry) => ({
      queryKey: ['atleta-ranking-detalle', entry.competenciaId, entry.disciplina],
      queryFn: () => fetchRankingCompetencia(entry.competenciaId!, entry.disciplina),
      enabled: Boolean(entry.competenciaId),
      retry: false,
    })),
  })

  const grillaQueries = useQueries({
    queries: entradaTorneo.map((entry) => ({
      queryKey: ['atleta-grilla-detalle', entry.competenciaId, entry.disciplina],
      queryFn: () => fetchGrillaCompetencia(entry.competenciaId!, entry.disciplina),
      enabled: Boolean(entry.competenciaId),
      retry: false,
    })),
  })

  const overallQuery = useQuery({
    queryKey: ['atleta-overall-detalle', torneoId],
    queryFn: () => fetchOverall(torneoId!),
    enabled: esCerrado && tieneInscripcion && Boolean(torneoId),
    retry: false,
  })

  const resultados: ResultadoEntry[] = entradaTorneo.map((entry, idx) => {
    const ranking = rankingQueries[idx]?.data ?? null
    return {
      entry,
      ranking,
      miResultado: findMiResultado(ranking, atletaId),
    }
  })

  const nombresPorCompetencia = new Map<string, Map<string, string>>()
  entradaTorneo.forEach((entry, idx) => {
    if (!entry.competenciaId) return
    const grilla = grillaQueries[idx]?.data ?? []
    const mapa = new Map<string, string>()
    grilla.forEach((fila) => mapa.set(fila.atleta_id, fila.nombre_atleta))
    nombresPorCompetencia.set(entry.competenciaId, mapa)
  })

  const overallPorTorneo = new Map([[torneoId ?? '', overallQuery.data ?? null]])

  const grupo =
    entradaTorneo.length > 0
      ? {
          torneoId: torneoId ?? '',
          torneoNombre: query.data?.torneo.nombre ?? '',
          resultados,
        }
      : null

  return (
    <AtletaShell title="Detalle del torneo" subtitle="Revisá condiciones, sede y disciplinas antes de inscribirte." showBack>
      {query.isLoading ? (
        <div className="rounded-3xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-300">
          Cargando torneo...
        </div>
      ) : null}

      {query.isError ? (
        <div className="rounded-3xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-100">
          No se pudo cargar el detalle del torneo.
        </div>
      ) : null}

      {query.data ? (
        <div className="space-y-4">
          <section className="rounded-[1.75rem] border border-slate-800 bg-slate-900 p-5">
            <div className="flex items-start justify-between gap-3">
              <div>
                <h2 className="text-xl font-semibold text-white">{query.data.torneo.nombre}</h2>
                <p className="mt-2 text-sm text-slate-400">
                  {formatFecha(query.data.torneo.fecha_inicio)} al {formatFecha(query.data.torneo.fecha_fin)}
                </p>
              </div>
              <span className="rounded-full border border-sky-500/40 bg-sky-500/10 px-3 py-1 text-xs font-semibold text-sky-300">
                {getEstadoTorneoLabel(query.data.torneo.estado)}
              </span>
            </div>
            <dl className="mt-4 space-y-3 text-sm text-slate-300">
              <div>
                <dt className="text-xs uppercase tracking-[0.18em] text-slate-500">Sede</dt>
                <dd className="mt-1">
                  {query.data.torneo.sede.nombre}, {query.data.torneo.sede.ciudad}, {query.data.torneo.sede.pais}
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-[0.18em] text-slate-500">Descripción</dt>
                <dd className="mt-1">{query.data.torneo.descripcion || 'Sin descripción pública.'}</dd>
              </div>
            </dl>
          </section>

          {query.data.inscripcion && !esCerrado ? (
            <div className="rounded-3xl border border-emerald-500/30 bg-emerald-500/10 p-4">
              <p className="text-sm font-semibold text-emerald-100">Ya estás inscripto en este torneo.</p>
              <p className="mt-2 text-sm text-emerald-50/80">
                Disciplinas: {query.data.inscripcion.disciplinas.map(formatDisciplina).join(' · ') || 'Por definir'}
              </p>
            </div>
          ) : null}

          {esCerrado && tieneInscripcion ? (
            snapshotQuery.isLoading ? (
              <div className="rounded-3xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-300">
                Cargando resultados...
              </div>
            ) : grupo ? (
              <GrupoResultados
                grupo={grupo}
                atletaId={atletaId}
                nombresPorCompetencia={nombresPorCompetencia}
                overallPorTorneo={overallPorTorneo}
              />
            ) : (
              <div className="rounded-3xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-400">
                No hay resultados registrados para este torneo.
              </div>
            )
          ) : null}

          {!query.data.inscripcion && query.data.torneo.estado === 'INSCRIPCION_ABIERTA' ? (
            <Link
              to={`/atleta/torneos/${query.data.torneo.torneo_id}/inscripcion`}
              className="flex min-h-11 items-center justify-center rounded-2xl bg-sky-500 px-4 py-3 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950"
            >
              Inscribirme en este torneo
            </Link>
          ) : null}

          {!query.data.inscripcion && query.data.torneo.estado !== 'INSCRIPCION_ABIERTA' ? (
            <div className="rounded-3xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-400">
              La inscripción no está disponible en el estado actual del torneo.
            </div>
          ) : null}
        </div>
      ) : null}
    </AtletaShell>
  )
}
