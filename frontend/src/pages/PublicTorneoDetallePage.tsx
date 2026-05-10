import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import {
  fetchCompetenciasPorTorneo,
  fetchGrillaCompetencia,
  type GrillaAtletaDto,
} from '../api/competencia'
import { fetchTorneo, type TorneoDto } from '../api/torneo'
import {
  fetchRankingCompetencia,
  type RankingEntradaDto,
} from '../api/resultados'
import useAuthStore from '../stores/useAuthStore'
import { formatAp, formatFecha, formatHora } from './atleta/portalData'

const ESTADOS_NO_DISPONIBLE: TorneoDto['estado'][] = ['CREADO', 'INSCRIPCION_ABIERTA', 'CANCELADO']

// ── Tipos internos ─────────────────────────────────────────────────────────────

interface GrillaDisciplina {
  competenciaId: string
  disciplina: string
  atletas: GrillaAtletaDto[]
}

interface RankingDisciplina {
  disciplina: string
  categorias: { categoria: string; entradas: RankingEntradaDto[] }[]
}

// ── Carga de datos ─────────────────────────────────────────────────────────────

async function loadDetalle(torneoId: string) {
  const [torneo, competencias] = await Promise.all([
    fetchTorneo(torneoId),
    fetchCompetenciasPorTorneo(torneoId),
  ])

  const [grillas, rankings] = await Promise.all([
    Promise.all(
      competencias.map(async (comp) => ({
        competenciaId: comp.competencia_id,
        disciplina: comp.disciplina,
        atletas: await fetchGrillaCompetencia(comp.competencia_id, comp.disciplina).catch(
          () => [] as GrillaAtletaDto[],
        ),
      })),
    ),
    Promise.all(
      competencias.map(async (comp) => ({
        disciplina: comp.disciplina,
        datos: await fetchRankingCompetencia(comp.competencia_id, comp.disciplina).catch(
          () => null,
        ),
      })),
    ),
  ])

  return { torneo, grillas, rankings }
}

// ── Helpers visuales ───────────────────────────────────────────────────────────

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
  return `${performance} ${unidad}`
}

function formatCategoria(cat: string): string {
  return cat
    .split('_')
    .map((p) => p.charAt(0) + p.slice(1).toLowerCase())
    .join(' ')
}

const MEDALLA = ['🥇', '🥈', '🥉']

// ── Componentes grilla ────────────────────────────────────────────────────────

function AtletaRow({ entry }: { entry: GrillaAtletaDto }) {
  const enCurso = entry.estado === 'Llamada'
  return (
    <tr className={enCurso ? 'border-b border-emerald-500/20 bg-emerald-500/5' : 'border-b border-slate-800/60'}>
      <td className="py-2 pr-3 text-right text-xs text-slate-500">{entry.posicion}</td>
      <td className="py-2 pr-3 text-sm text-slate-200">{entry.nombre_atleta}</td>
      <td className="py-2 pr-3 text-xs text-slate-400">{formatAp(entry.ap_declarado, entry.unidad)}</td>
      <td className="py-2 pr-3 text-xs text-slate-400">{formatHora(entry.ot_programado)}</td>
      <td className="py-2 pr-3 text-xs font-medium text-slate-300">{formatRp(entry.performance, entry.unidad)}</td>
      <td className={`py-2 text-xs ${tarjetaClases(entry.tarjeta_asignada)}`}>
        {entry.tarjeta_asignada ?? '—'}
      </td>
    </tr>
  )
}

function GrillaTabContent({ grilla }: { grilla: GrillaDisciplina }) {
  const sorted = [...grilla.atletas].sort((a, b) => a.posicion - b.posicion)
  if (sorted.length === 0) return <p className="py-4 text-sm text-slate-500">Grilla no disponible aún.</p>
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[520px] text-left">
        <thead>
          <tr className="border-b border-slate-700">
            <th className="pb-2 pr-3 text-right text-xs text-slate-500">Pos</th>
            <th className="pb-2 pr-3 text-xs text-slate-500">Atleta</th>
            <th className="pb-2 pr-3 text-xs text-slate-500">Anuncio</th>
            <th className="pb-2 pr-3 text-xs text-slate-500">OT</th>
            <th className="pb-2 pr-3 text-xs text-slate-500">Performance</th>
            <th className="pb-2 text-xs text-slate-500">Tarjeta</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((e) => <AtletaRow key={e.performance_id} entry={e} />)}
        </tbody>
      </table>
    </div>
  )
}

// ── Componentes podios ────────────────────────────────────────────────────────

function PodioTabContent({
  entradas,
  nombrePorId,
}: {
  entradas: RankingEntradaDto[]
  nombrePorId: Map<string, string>
}) {
  const podio = entradas.filter((e) => !e.es_dns).slice(0, 3)
  if (podio.length === 0) return <p className="py-3 text-sm text-slate-500">Sin resultados aún.</p>
  return (
    <div className="space-y-2 pt-1">
      {podio.map((e, i) => (
        <div key={e.atleta_id} className="flex items-center gap-3">
          <span className="text-lg w-6 text-center">{MEDALLA[i]}</span>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-slate-200 truncate">
              {nombrePorId.get(e.atleta_id) ?? e.atleta_id}
            </p>
          </div>
          <div className="text-right shrink-0">
            <p className="text-sm font-semibold text-slate-100">
              {e.rp && e.unidad ? `${e.rp} ${e.unidad}` : '—'}
            </p>
            <p className={`text-xs ${tarjetaClases(e.tarjeta)}`}>{e.tarjeta ?? '—'}</p>
          </div>
        </div>
      ))}
    </div>
  )
}

function CategoriaCard({
  categoria,
  rankingsPorDisciplina,
  nombrePorId,
}: {
  categoria: string
  rankingsPorDisciplina: { disciplina: string; entradas: RankingEntradaDto[] }[]
  nombrePorId: Map<string, string>
}) {
  const [tab, setTab] = useState(rankingsPorDisciplina[0]?.disciplina ?? '')
  const activo = rankingsPorDisciplina.find((r) => r.disciplina === tab)

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60">
      <div className="border-b border-slate-800 px-4 pt-3 pb-0">
        <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
          {formatCategoria(categoria)}
        </p>
        <div className="flex gap-1">
          {rankingsPorDisciplina.map((r) => (
            <button
              key={r.disciplina}
              onClick={() => setTab(r.disciplina)}
              className={`rounded-t-lg px-3 py-1.5 text-xs font-semibold transition-colors ${
                tab === r.disciplina
                  ? 'bg-slate-800 text-sky-400'
                  : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              {r.disciplina}
            </button>
          ))}
        </div>
      </div>
      <div className="px-4 py-3">
        {activo ? (
          <PodioTabContent entradas={activo.entradas} nombrePorId={nombrePorId} />
        ) : null}
      </div>
    </div>
  )
}

function PodiosSection({
  rankings,
  nombrePorId,
}: {
  rankings: RankingDisciplina[]
  nombrePorId: Map<string, string>
}) {
  // Recopilar todas las categorías únicas en orden de aparición
  const todasCats = Array.from(
    new Set(rankings.flatMap((r) => r.categorias.map((c) => c.categoria))),
  )

  if (todasCats.length === 0) return null

  // Para cada categoría, armar la lista de {disciplina, entradas}
  const porCategoria = todasCats.map((cat) => ({
    categoria: cat,
    rankingsPorDisciplina: rankings
      .map((r) => ({
        disciplina: r.disciplina,
        entradas: r.categorias.find((c) => c.categoria === cat)?.entradas ?? [],
      }))
      .filter((r) => r.entradas.length > 0),
  })).filter((c) => c.rankingsPorDisciplina.length > 0)

  if (porCategoria.length === 0) return null

  return (
    <div className="mt-4">
      <p className="mb-3 text-xs font-semibold uppercase tracking-[0.22em] text-slate-500">
        Podios
      </p>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {porCategoria.map((c) => (
          <CategoriaCard
            key={c.categoria}
            categoria={c.categoria}
            rankingsPorDisciplina={c.rankingsPorDisciplina}
            nombrePorId={nombrePorId}
          />
        ))}
      </div>
    </div>
  )
}

// ── Card principal del torneo ─────────────────────────────────────────────────

interface TorneoDetalleCardProps {
  torneo: TorneoDto
  grillas: GrillaDisciplina[]
  rankings: RankingDisciplina[]
  noDisponible: boolean
}

function TorneoDetalleCard({ torneo, grillas, rankings, noDisponible }: TorneoDetalleCardProps) {
  const [tabGrilla, setTabGrilla] = useState(grillas[0]?.disciplina ?? '')

  const grillaActiva = grillas.find((g) => g.disciplina === tabGrilla) ?? null

  const nombrePorId = new Map<string, string>()
  grillas.forEach((g) => g.atletas.forEach((a) => nombrePorId.set(a.atleta_id, a.nombre_atleta)))

  return (
    <div className="rounded-[1.75rem] border border-slate-800 bg-slate-900">
      {/* Info del torneo */}
      <div className="border-b border-slate-800 p-5">
        <h1 className="text-xl font-semibold text-slate-50">{torneo.nombre}</h1>
        <p className="mt-1 text-sm text-slate-400">
          {formatFecha(torneo.fecha_inicio)}
          {torneo.fecha_fin !== torneo.fecha_inicio ? ` — ${formatFecha(torneo.fecha_fin)}` : null}{' '}
          · {torneo.sede.ciudad}, {torneo.sede.pais}
        </p>
        <p className="mt-0.5 text-sm text-slate-500">
          Organiza: {torneo.entidad_organizadora.nombre}
        </p>
      </div>

      {/* Contenido */}
      <div className="p-5">
        {noDisponible ? (
          <p className="text-sm text-slate-400">La grilla no está disponible en este momento.</p>
        ) : grillas.length === 0 ? (
          <p className="text-sm text-slate-400">No hay disciplinas configuradas aún.</p>
        ) : (
          <>
            {/* Tabs de grilla */}
            <div className="flex gap-1 border-b border-slate-800 pb-0 mb-0">
              {grillas.map((g) => (
                <button
                  key={g.disciplina}
                  onClick={() => setTabGrilla(g.disciplina)}
                  className={`rounded-t-xl px-4 py-2 text-xs font-semibold transition-colors ${
                    tabGrilla === g.disciplina
                      ? 'bg-slate-800 text-sky-400'
                      : 'text-slate-500 hover:text-slate-300'
                  }`}
                >
                  {g.disciplina}
                </button>
              ))}
            </div>

            {/* Grilla con altura fija y scroll */}
            <div className="h-96 overflow-y-auto pt-4">
              {grillaActiva ? <GrillaTabContent grilla={grillaActiva} /> : null}
            </div>

            {/* Podios */}
            <PodiosSection rankings={rankings} nombrePorId={nombrePorId} />
          </>
        )}
      </div>
    </div>
  )
}

// ── Página principal ──────────────────────────────────────────────────────────

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

  const noDisponible = Boolean(data?.torneo && ESTADOS_NO_DISPONIBLE.includes(data.torneo.estado))

  // Transformar rankings al formato interno
  const rankingsDisciplina: RankingDisciplina[] = (data?.rankings ?? [])
    .filter((r) => r.datos !== null)
    .map((r) => ({
      disciplina: r.disciplina,
      categorias: r.datos!.rankings,
    }))

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
          <TorneoDetalleCard
            torneo={data.torneo}
            grillas={data.grillas}
            rankings={rankingsDisciplina}
            noDisponible={noDisponible}
          />
        ) : null}
      </main>
    </div>
  )
}
