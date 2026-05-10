import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import {
  fetchCompetenciasPorTorneo,
  fetchGrillaCompetencia,
  type GrillaAtletaDto,
} from '../api/competencia'
import { fetchTorneo, type TorneoDto } from '../api/torneo'
import useAuthStore from '../stores/useAuthStore'
import { formatAp, formatFecha, formatHora } from './atleta/portalData'
import type { EstadoPerformance } from '../types/auth'

const ESTADOS_NO_DISPONIBLE: TorneoDto['estado'][] = ['CREADO', 'INSCRIPCION_ABIERTA', 'CANCELADO']

async function loadDetalle(torneoId: string) {
  const [torneo, competencias] = await Promise.all([
    fetchTorneo(torneoId),
    fetchCompetenciasPorTorneo(torneoId),
  ])
  const grillas = await Promise.all(
    competencias.map(async (comp) => ({
      competenciaId: comp.competencia_id,
      disciplina: comp.disciplina,
      atletas: await fetchGrillaCompetencia(comp.competencia_id, comp.disciplina).catch(
        () => [] as GrillaAtletaDto[],
      ),
    })),
  )
  return { torneo, grillas }
}

function estadoVisual(estado: EstadoPerformance): { label: string; clases: string } {
  if (estado === 'Llamada') return { label: 'En curso', clases: 'text-emerald-400 font-semibold' }
  if (estado === 'AnunciadaAP') return { label: 'Pendiente', clases: 'text-slate-500' }
  return { label: 'Realizado', clases: 'text-slate-300' }
}

function tarjetaVisual(tarjeta: string | null): { label: string; clases: string } {
  switch (tarjeta) {
    case 'BLANCA':
      return { label: 'Blanca', clases: 'text-slate-200' }
    case 'BLANCA_CON_PENALIZACION':
      return { label: 'Blanca c/pen.', clases: 'text-yellow-300' }
    case 'AMARILLA':
      return { label: 'En revisión', clases: 'text-yellow-400' }
    case 'ROJA':
      return { label: 'Roja', clases: 'text-red-400' }
    default:
      return { label: '—', clases: 'text-slate-600' }
  }
}

function AtletaRow({ entry }: { entry: GrillaAtletaDto }) {
  const estado = estadoVisual(entry.estado)
  const tarjeta = tarjetaVisual(entry.tarjeta_asignada)
  const enCurso = entry.estado === 'Llamada'

  return (
    <tr
      className={
        enCurso
          ? 'border-b border-emerald-500/20 bg-emerald-500/5'
          : 'border-b border-slate-800/60'
      }
    >
      <td className="py-2 pr-3 text-right text-xs text-slate-500">{entry.posicion}</td>
      <td className="py-2 pr-3 text-sm text-slate-200">{entry.nombre_atleta}</td>
      <td className="py-2 pr-3 text-xs text-slate-400">
        {formatAp(entry.ap_declarado, entry.unidad)}
      </td>
      <td className="py-2 pr-3 text-xs text-slate-400">{formatHora(entry.ot_programado)}</td>
      <td className={`py-2 pr-3 text-xs ${estado.clases}`}>{estado.label}</td>
      <td className={`py-2 text-xs ${tarjeta.clases}`}>{tarjeta.label}</td>
    </tr>
  )
}

interface GrillaDisciplina {
  competenciaId: string
  disciplina: string
  atletas: GrillaAtletaDto[]
}

function SeccionDisciplina({ grilla }: { grilla: GrillaDisciplina }) {
  const sorted = [...grilla.atletas].sort((a, b) => a.posicion - b.posicion)

  return (
    <section className="rounded-[1.75rem] border border-slate-800 bg-slate-900 p-5">
      <p className="mb-4 text-xs font-semibold uppercase tracking-[0.22em] text-sky-400">
        {grilla.disciplina}
      </p>
      {sorted.length === 0 ? (
        <p className="text-sm text-slate-500">Grilla no disponible aún.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[480px] text-left">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="pb-2 pr-3 text-right text-xs text-slate-500">Pos</th>
                <th className="pb-2 pr-3 text-xs text-slate-500">Atleta</th>
                <th className="pb-2 pr-3 text-xs text-slate-500">AP</th>
                <th className="pb-2 pr-3 text-xs text-slate-500">OT</th>
                <th className="pb-2 pr-3 text-xs text-slate-500">Estado</th>
                <th className="pb-2 text-xs text-slate-500">Tarjeta</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((entry) => (
                <AtletaRow key={entry.performance_id} entry={entry} />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}

export function PublicTorneoDetallePage() {
  const { torneoId } = useParams<{ torneoId: string }>()
  const rol = useAuthStore((s) => s.rol)

  const { data, isLoading, isError } = useQuery({
    queryKey: ['torneo-detalle-publico', torneoId],
    queryFn: () => loadDetalle(torneoId ?? ''),
    enabled: Boolean(torneoId),
    refetchInterval: 30_000,
  })

  const portalLink = (() => {
    if (rol === 'juez') return '/juez/disciplinas'
    if (rol === 'organizador') return '/organizador/torneo'
    if (rol === 'atleta') return '/atleta'
    return null
  })()

  const noDisponible =
    data?.torneo && ESTADOS_NO_DISPONIBLE.includes(data.torneo.estado)

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
          ← Volver a torneos
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

        {data ? (
          <div className="space-y-6">
            <div>
              <h1 className="text-2xl font-semibold text-slate-50">{data.torneo.nombre}</h1>
              <p className="mt-1 text-sm text-slate-400">
                {formatFecha(data.torneo.fecha_inicio)}
                {data.torneo.fecha_fin !== data.torneo.fecha_inicio
                  ? ` — ${formatFecha(data.torneo.fecha_fin)}`
                  : null}{' '}
                · {data.torneo.sede.ciudad}, {data.torneo.sede.pais}
              </p>
              <p className="mt-0.5 text-sm text-slate-500">
                Organiza: {data.torneo.entidad_organizadora.nombre}
              </p>
            </div>

            {noDisponible ? (
              <div className="rounded-3xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-400">
                La grilla no está disponible en este momento.
              </div>
            ) : null}

            {!noDisponible && data.grillas.length === 0 ? (
              <div className="rounded-3xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-400">
                No hay disciplinas configuradas aún.
              </div>
            ) : null}

            {!noDisponible
              ? data.grillas.map((grilla) => (
                  <SeccionDisciplina key={grilla.competenciaId} grilla={grilla} />
                ))
              : null}
          </div>
        ) : null}
      </main>
    </div>
  )
}
