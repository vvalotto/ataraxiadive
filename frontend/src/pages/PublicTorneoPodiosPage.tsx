import { useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useQueries, useQuery } from '@tanstack/react-query'
import { fetchCompetenciasPorTorneo, fetchGrillaCompetencia } from '../api/competencia'
import { fetchTorneo } from '../api/torneo'
import {
  fetchOverall,
  fetchRankingCompetencia,
  type OverallEntradaDto,
  type RankingEntradaDto,
} from '../api/resultados'
import useAuthStore from '../stores/useAuthStore'
import { formatFecha } from './atleta/portalData'

// ── Helpers ────────────────────────────────────────────────────────────────────

function formatCategoria(cat: string): string {
  return cat
    .split('_')
    .map((p) => p.charAt(0) + p.slice(1).toLowerCase())
    .join(' ')
}

const MEDALLA = ['🥇', '🥈', '🥉']

// ── Componentes ────────────────────────────────────────────────────────────────

function FilaPodio({
  posicion,
  atletaId,
  nombrePorId,
  rp,
  unidad,
  puntos,
}: {
  posicion: number
  atletaId: string
  nombrePorId: Map<string, string>
  rp?: string | null
  unidad?: string | null
  puntos?: string | null
}) {
  return (
    <div className="flex items-center gap-3">
      <span className="w-6 text-center text-lg">{MEDALLA[posicion - 1] ?? `${posicion}º`}</span>
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-slate-200">
          {nombrePorId.get(atletaId) ?? atletaId}
        </p>
      </div>
      <div className="shrink-0 text-right">
        {rp && unidad ? (
          <p className="text-sm font-semibold text-slate-100">{`${rp} ${unidad}`}</p>
        ) : null}
        {puntos ? (
          <p className="font-mono text-xs text-sky-400">{puntos} pts</p>
        ) : null}
      </div>
    </div>
  )
}

function OverallCategoriaCard({
  categoria,
  entradas,
  nombrePorId,
}: {
  categoria: string
  entradas: OverallEntradaDto[]
  nombrePorId: Map<string, string>
}) {
  const podio = entradas.filter((e) => e.en_podio).slice(0, 3)
  if (podio.length === 0) return null
  return (
    <div className="rounded-2xl border border-amber-500/20 bg-amber-500/5 p-4">
      <p className="mb-3 text-xs font-semibold uppercase tracking-[0.2em] text-amber-400">
        {formatCategoria(categoria)}
      </p>
      <div className="space-y-2">
        {podio.map((e) => (
          <FilaPodio
            key={e.atleta_id}
            posicion={e.posicion}
            atletaId={e.atleta_id}
            nombrePorId={nombrePorId}
            puntos={e.puntos_overall}
          />
        ))}
      </div>
    </div>
  )
}

function DisciplinaCategoriaCard({
  categoria,
  disciplinas,
  nombrePorId,
}: {
  categoria: string
  disciplinas: { disciplina: string; entradas: RankingEntradaDto[] }[]
  nombrePorId: Map<string, string>
}) {
  const [tab, setTab] = useState(disciplinas[0]?.disciplina ?? '')
  const activo = disciplinas.find((d) => d.disciplina === tab)
  const podio = (activo?.entradas ?? []).filter((e) => e.en_podio).slice(0, 3)

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60">
      <div className="border-b border-slate-800 px-4 pb-0 pt-3">
        <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
          {formatCategoria(categoria)}
        </p>
        <div className="flex gap-1">
          {disciplinas.map((d) => (
            <button
              key={d.disciplina}
              onClick={() => setTab(d.disciplina)}
              className={`rounded-t-lg px-3 py-1.5 text-xs font-semibold transition-colors ${
                tab === d.disciplina
                  ? 'bg-slate-800 text-sky-400'
                  : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              {d.disciplina}
            </button>
          ))}
        </div>
      </div>
      <div className="space-y-2 px-4 py-3">
        {podio.length === 0 ? (
          <p className="py-1 text-sm text-slate-500">Sin resultados aún.</p>
        ) : (
          podio.map((e) => (
            <FilaPodio
              key={e.atleta_id}
              posicion={e.posicion}
              atletaId={e.atleta_id}
              nombrePorId={nombrePorId}
              rp={e.rp}
              unidad={e.unidad}
              puntos={e.puntos}
            />
          ))
        )}
      </div>
    </div>
  )
}

// ── Página ─────────────────────────────────────────────────────────────────────

export function PublicTorneoPodiosPage() {
  const { torneoId } = useParams<{ torneoId: string }>()
  const rol = useAuthStore((s) => s.rol)

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

  const grillaQueries = useQueries({
    queries: competencias.map((comp) => ({
      queryKey: ['grilla-publica', comp.competencia_id, comp.disciplina],
      queryFn: () => fetchGrillaCompetencia(comp.competencia_id, comp.disciplina),
      enabled: Boolean(comp.competencia_id),
    })),
  })

  const nombrePorId = useMemo(() => {
    const map = new Map<string, string>()
    grillaQueries.forEach((q) => {
      ;(q.data ?? []).forEach((a) => map.set(a.atleta_id, a.nombre_atleta))
    })
    return map
  }, [grillaQueries])

  const rankingQueries = useQueries({
    queries: competencias.map((comp) => ({
      queryKey: ['ranking', comp.competencia_id, comp.disciplina],
      queryFn: () => fetchRankingCompetencia(comp.competencia_id, comp.disciplina),
      enabled: Boolean(comp.competencia_id && comp.disciplina),
      refetchInterval: 30_000,
    })),
  })

  const overallQuery = useQuery({
    queryKey: ['overall', torneoId],
    queryFn: () => fetchOverall(torneoId ?? ''),
    enabled: competencias.length > 0,
    refetchInterval: 30_000,
    retry: false,
  })

  // { categoria → [{ disciplina, entradas }] }
  const porCategoria = useMemo(() => {
    const map = new Map<string, { disciplina: string; entradas: RankingEntradaDto[] }[]>()
    competencias.forEach((comp, idx) => {
      const data = rankingQueries[idx]?.data
      if (!data) return
      data.rankings.forEach((cat) => {
        if (!map.has(cat.categoria)) map.set(cat.categoria, [])
        if (cat.entradas.some((e) => e.en_podio)) {
          map.get(cat.categoria)!.push({ disciplina: comp.disciplina, entradas: cat.entradas })
        }
      })
    })
    return Array.from(map.entries()).filter(([, d]) => d.length > 0)
  }, [competencias, rankingQueries])

  const overallCategorias = useMemo(
    () => (overallQuery.data?.rankings ?? []).filter((c) => c.entradas.some((e) => e.en_podio)),
    [overallQuery.data],
  )

  const portalLink =
    rol === 'juez'
      ? '/juez/disciplinas'
      : rol === 'organizador'
        ? '/organizador/torneo'
        : rol === 'atleta'
          ? '/atleta'
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
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-amber-400">
              Podios
            </p>
            <h1 className="mt-1 text-xl font-semibold text-white">
              {torneo ? `${torneo.nombre} · ${formatFecha(torneo.fecha_inicio)}` : 'Cargando...'}
            </h1>
          </div>

          <div className="flex flex-col gap-6 p-5">
            {competenciasQuery.isLoading ? (
              <p className="text-sm text-slate-400">Cargando...</p>
            ) : null}

            {/* Overall */}
            {overallCategorias.length > 0 ? (
              <section>
                <p className="mb-3 text-xs font-semibold uppercase tracking-[0.18em] text-amber-300">
                  Overall
                </p>
                <div className="flex flex-col gap-3">
                  {overallCategorias.map((cat) => (
                    <OverallCategoriaCard
                      key={cat.categoria}
                      categoria={cat.categoria}
                      entradas={cat.entradas}
                      nombrePorId={nombrePorId}
                    />
                  ))}
                </div>
              </section>
            ) : null}

            {/* Por disciplina */}
            {porCategoria.length > 0 ? (
              <section>
                <p className="mb-3 text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                  Por disciplina
                </p>
                <div className="flex flex-col gap-3">
                  {porCategoria.map(([categoria, disciplinas]) => (
                    <DisciplinaCategoriaCard
                      key={categoria}
                      categoria={categoria}
                      disciplinas={disciplinas}
                      nombrePorId={nombrePorId}
                    />
                  ))}
                </div>
              </section>
            ) : null}

            {!competenciasQuery.isLoading &&
            overallCategorias.length === 0 &&
            porCategoria.length === 0 ? (
              <p className="text-sm text-slate-500">Sin podios disponibles aún.</p>
            ) : null}
          </div>
        </div>
      </main>
    </div>
  )
}
