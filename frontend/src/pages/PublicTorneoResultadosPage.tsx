import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { fetchCompetenciasPorTorneo, fetchGrillaCompetencia, type GrillaAtletaDto } from '../api/competencia'
import { fetchTorneo } from '../api/torneo'
import { DQ_REASON_LABELS, PENALTY_LABELS, TARJETA_LABELS } from '../constants/tarjeta'
import { formatMarca } from '../utils/marca'
import useAuthStore from '../stores/useAuthStore'
import { formatAp, formatFecha, formatHora } from './atleta/portalData'

// ── Helpers ────────────────────────────────────────────────────────────────────

function tarjetaClases(tarjeta: string | null): string {
  switch (tarjeta) {
    case 'Blanca': return 'text-slate-200'
    case 'BlancaConPenalizaciones': return 'text-yellow-300'
    case 'Amarilla': return 'text-yellow-400'
    case 'Roja': return 'text-red-400'
    default: return 'text-slate-600'
  }
}

function formatRp(performance: string | null | undefined, unidad: string): string {
  if (!performance) return '—'
  return formatMarca(performance, unidad)
}

// ── Componentes ────────────────────────────────────────────────────────────────

function AtletaRow({ entry }: { entry: GrillaAtletaDto }) {
  const enCurso = entry.estado === 'Llamada'
  return (
    <tr
      className={
        enCurso
          ? 'border-b border-emerald-500/20 bg-emerald-500/5'
          : 'border-b border-slate-800/60'
      }
    >
      <td className="py-2 pr-3 text-center text-xs text-slate-500">{entry.posicion}</td>
      <td className="py-2 pr-3 text-sm text-slate-200">{entry.nombre_atleta}</td>
      <td className="py-2 pr-3 text-center text-xs text-slate-400">
        {formatAp(entry.ap_declarado, entry.unidad)}
      </td>
      <td className="py-2 pr-3 text-center text-xs text-slate-400">
        {formatHora(entry.ot_programado)}
      </td>
      <td className="py-2 pr-3 text-center text-xs font-medium text-slate-300">
        {formatRp(entry.performance, entry.unidad)}
      </td>
      <td className="py-2 text-center text-xs">
        <span
          className={entry.estado === 'DNS' ? 'text-slate-500' : tarjetaClases(entry.tarjeta_asignada)}
        >
          {entry.estado === 'DNS'
            ? 'DNS'
            : entry.tarjeta_asignada
            ? (TARJETA_LABELS[entry.tarjeta_asignada] ?? entry.tarjeta_asignada)
            : '—'}
        </span>
        {entry.motivo_dq ? (
          <p className="mt-0.5 text-red-400">
            {DQ_REASON_LABELS[entry.motivo_dq] ?? entry.motivo_dq}
          </p>
        ) : null}
        {entry.penalizaciones?.length > 0 ? (
          <ul className="mt-0.5 space-y-0.5">
            {entry.penalizaciones.map((p: string) => (
              <li key={p} className="text-amber-300">
                {PENALTY_LABELS[p] ?? p}
              </li>
            ))}
          </ul>
        ) : null}
      </td>
    </tr>
  )
}

// ── Página ─────────────────────────────────────────────────────────────────────

export function PublicTorneoResultadosPage() {
  const { torneoId } = useParams<{ torneoId: string }>()
  const rol = useAuthStore((s) => s.rol)
  const [tabActiva, setTabActiva] = useState<string | null>(null)

  const torneoQuery = useQuery({
    queryKey: ['torneo', torneoId],
    queryFn: () => fetchTorneo(torneoId ?? ''),
    enabled: Boolean(torneoId),
  })

  const competenciasQuery = useQuery({
    queryKey: ['competencias-torneo', torneoId],
    queryFn: () => fetchCompetenciasPorTorneo(torneoId ?? ''),
    enabled: Boolean(torneoId),
  })

  const competencias = competenciasQuery.data ?? []
  const tab = tabActiva ?? competencias[0]?.disciplina ?? null

  const competenciaActiva = competencias.find((c) => c.disciplina === tab) ?? null

  const grillaQuery = useQuery({
    queryKey: ['grilla-publica', competenciaActiva?.competencia_id, competenciaActiva?.disciplina],
    queryFn: () =>
      fetchGrillaCompetencia(
        competenciaActiva!.competencia_id,
        competenciaActiva!.disciplina,
      ),
    enabled: Boolean(competenciaActiva),
    refetchInterval: 30_000,
  })

  const atletas = [...(grillaQuery.data ?? [])].sort((a, b) => a.posicion - b.posicion)

  const portalLink =
    rol === 'juez' ? '/juez/disciplinas'
    : rol === 'organizador' ? '/organizador/torneo'
    : rol === 'atleta' ? '/atleta'
    : null

  const torneo = torneoQuery.data

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 bg-slate-900/80 px-4 py-3">
        <div className="mx-auto flex max-w-3xl items-center justify-between">
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

      <main className="mx-auto max-w-3xl px-4 py-6">
        <Link
          to={`/portalapnea/${torneoId}`}
          className="mb-4 flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200"
        >
          ← {torneo?.nombre ?? 'Torneo'}
        </Link>

        <div className="rounded-[1.75rem] border border-slate-800 bg-slate-900">
          <div className="border-b border-slate-800 p-5">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
              Resultados
            </p>
            <h1 className="mt-1 text-xl font-semibold text-white">
              {torneo
                ? `${torneo.nombre} · ${formatFecha(torneo.fecha_inicio)}`
                : 'Cargando...'}
            </h1>
          </div>

          <div className="p-5">
            {competenciasQuery.isLoading ? (
              <p className="text-sm text-slate-400">Cargando disciplinas...</p>
            ) : competencias.length === 0 ? (
              <p className="text-sm text-slate-400">Sin disciplinas configuradas.</p>
            ) : (
              <>
                <div className="flex gap-1 border-b border-slate-800 pb-0 mb-0">
                  {competencias.map((c) => (
                    <button
                      key={c.disciplina}
                      onClick={() => setTabActiva(c.disciplina)}
                      className={`rounded-t-xl px-4 py-2 text-xs font-semibold transition-colors ${
                        tab === c.disciplina
                          ? 'bg-slate-800 text-sky-400'
                          : 'text-slate-500 hover:text-slate-300'
                      }`}
                    >
                      {c.disciplina}
                    </button>
                  ))}
                </div>

                <div className="h-[32rem] overflow-y-auto pt-4">
                  {grillaQuery.isLoading ? (
                    <p className="text-sm text-slate-400">Cargando grilla...</p>
                  ) : atletas.length === 0 ? (
                    <p className="text-sm text-slate-500">Grilla no disponible aún.</p>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full min-w-[520px] text-left">
                        <thead>
                          <tr className="border-b border-slate-700">
                            <th className="pb-2 pr-3 text-center text-xs text-slate-500">Pos</th>
                            <th className="pb-2 pr-3 text-xs text-slate-500">Atleta</th>
                            <th className="pb-2 pr-3 text-center text-xs text-slate-500">Anuncio</th>
                            <th className="pb-2 pr-3 text-center text-xs text-slate-500">OT</th>
                            <th className="pb-2 pr-3 text-center text-xs text-slate-500">Performance</th>
                            <th className="pb-2 text-center text-xs text-slate-500">Tarjeta</th>
                          </tr>
                        </thead>
                        <tbody>
                          {atletas.map((e) => (
                            <AtletaRow key={e.performance_id} entry={e} />
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
