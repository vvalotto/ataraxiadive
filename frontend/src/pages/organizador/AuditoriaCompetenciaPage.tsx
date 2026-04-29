import { useMemo, useState } from 'react'
import { Link, useParams, useSearchParams } from 'react-router-dom'
import type { GrillaAtletaDto } from '../../api/competencia'
import { OrganizadorLayout } from '../../components/organizador/OrganizadorLayout'
import { useAuditoriaCompetencia } from '../../hooks/useAuditoriaCompetencia'

const ESTADO_LABELS: Record<string, string> = {
  // Estado de competencia
  EnEjecucion: 'En ejecución',
  Finalizada: 'Finalizada',
  Confirmada: 'Grilla confirmada',
  // Estado de atleta en grilla
  AnunciadaAP: 'AP declarado',
  Llamada: 'En llamada',
  ResultadoRegistrado: 'Resultado registrado',
  Ejecutada: 'Ejecutada',
  EnRevision: 'En revisión',
  DNS: 'DNS',
}

function formatEstado(estado: string) {
  return ESTADO_LABELS[estado] ?? estado
}

function formatResultadoFinal(
  atleta: GrillaAtletaDto,
  rankingMap: Map<string, string>,
) {
  const ranking = rankingMap.get(atleta.atleta_id)
  if (ranking) return ranking
  return formatEstado(atleta.estado) || 'Pendiente'
}

function borderClasePorResultado(atleta: GrillaAtletaDto): string {
  switch (atleta.tarjeta_asignada) {
    case 'Blanca':
      return 'border-emerald-300 bg-emerald-50/70'
    case 'BlancaConPenalizaciones':
      return 'border-amber-300 bg-amber-50/75'
    case 'Roja':
      return 'border-red-300 bg-red-50/70'
    default:
      break
  }
  if (atleta.estado === 'DNS') return 'border-violet-400 bg-violet-50/60'
  return 'border-stone-300/80 bg-white/85'
}

function truncateHash(value: string) {
  if (value.length <= 16) return value
  return `${value.slice(0, 16)}...`
}

export function AuditoriaCompetenciaPage() {
  const { competenciaId } = useParams()
  const [searchParams] = useSearchParams()
  const [copyFeedback, setCopyFeedback] = useState<string | null>(null)
  const disciplina = searchParams.get('disciplina') ?? undefined
  const torneoId = searchParams.get('torneo_id') ?? undefined

  const { estado, grilla, ranking, isLoading, hasError } = useAuditoriaCompetencia({
    competenciaId,
    disciplina,
  })

  const rankingMap = useMemo(() => {
    const entries = ranking?.rankings.flatMap((grupo) => grupo.entradas) ?? []
    return new Map(
      entries.map((entry) => [
        entry.atleta_id,
        entry.es_dns ? 'DNS' : (entry.tarjeta ?? (entry.rp ? `RP ${entry.rp}` : 'Pendiente')),
      ]),
    )
  }, [ranking])

  async function handleCopyHash() {
    if (!estado?.hash_sha256) return
    await navigator.clipboard.writeText(estado.hash_sha256)
    setCopyFeedback('Copiado')
    window.setTimeout(() => setCopyFeedback(null), 1600)
  }

  if (!competenciaId || !disciplina) {
    return (
      <OrganizadorLayout
        title="Auditoria"
        subtitle="Faltan parametros de navegacion"
        activeTournamentId={torneoId}
        actions={
          <Link
            to="/organizador/audit-log"
            className="rounded-full border border-slate-600 bg-slate-800 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-slate-100"
          >
            Volver
          </Link>
        }
      >
        <section className="rounded-[2rem] border border-red-300/60 bg-red-50 p-5 text-sm text-red-900">
          No se pudo determinar la disciplina de la competencia.
        </section>
      </OrganizadorLayout>
    )
  }

  return (
    <OrganizadorLayout
      title={`Auditoria - ${disciplina}`}
      activeTournamentId={torneoId}
      subtitle={`Disciplina ${disciplina}`}
      actions={
        <Link
          to={torneoId ? `/organizador/audit-log?torneo_id=${torneoId}` : '/organizador/audit-log'}
          className="rounded-full border border-slate-600 bg-slate-800 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-slate-100"
        >
          Volver a Audit Log
        </Link>
      }
    >
      <section className="rounded-[2rem] border border-slate-700 bg-slate-900/75 p-5 text-sm text-slate-300">
        Vista contextual de auditoria por disciplina. La navegacion principal del organizador se mantiene disponible en el shell superior.
      </section>

      {isLoading ? (
        <section className="rounded-[2rem] border border-slate-700 bg-slate-900/70 p-5 text-sm text-slate-300">
          Cargando auditoria de competencia...
        </section>
      ) : null}

      {hasError ? (
        <section className="rounded-[2rem] border border-red-500/40 bg-red-950/40 p-5 text-sm text-red-100">
          No se pudo cargar la auditoria de la competencia.
        </section>
      ) : null}

      {!isLoading && !hasError && estado ? (
        <section className="rounded-[2rem] border border-slate-700 bg-slate-900/85 p-5 shadow-[0_20px_60px_rgba(2,6,23,0.24)]">
          <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                Estado de disciplina
              </p>
              <h2 className="mt-2 text-2xl font-semibold text-white">
                {formatEstado(estado.estado)}
              </h2>
            </div>

            {estado.estado === 'Finalizada' && estado.hash_sha256 ? (
              <div className="rounded-[1.5rem] border border-emerald-500/40 bg-emerald-500/10 px-4 py-3">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-emerald-800">
                  Hash SHA-256
                </p>
                <div className="mt-2 flex flex-wrap items-center gap-3">
                  <code
                    title={estado.hash_sha256}
                    className="rounded-full bg-slate-950 px-3 py-2 text-sm text-emerald-200"
                  >
                    {truncateHash(estado.hash_sha256)}
                  </code>
                  <button
                    type="button"
                    onClick={() => void handleCopyHash()}
                    className="rounded-full bg-emerald-900 px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-white"
                  >
                    Copiar
                  </button>
                  {copyFeedback ? (
                    <span className="text-xs font-semibold uppercase tracking-[0.14em] text-emerald-900">
                      {copyFeedback}
                    </span>
                  ) : null}
                </div>
              </div>
            ) : null}
          </div>
        </section>
      ) : null}

      {!isLoading && !hasError && (grilla?.length ?? 0) === 0 ? (
        <section className="rounded-[2rem] border border-slate-700 bg-slate-900/70 p-5 text-sm text-slate-300">
          No hay atletas registrados para esta competencia.
        </section>
      ) : null}

      {!isLoading && !hasError
        ? grilla?.map((atleta) => (
            <Link
              key={atleta.performance_id}
              to={`/organizador/competencias/${competenciaId}/auditoria/${atleta.atleta_id}?disciplina=${encodeURIComponent(disciplina)}&torneo_id=${encodeURIComponent(torneoId ?? '')}`}
              className={`block rounded-[2rem] border p-5 shadow-[0_20px_60px_rgba(120,93,54,0.08)] transition hover:-translate-y-0.5 ${borderClasePorResultado(atleta)}`}
            >
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
                    Atleta
                  </p>
                  <h3 className="mt-2 text-xl font-semibold text-stone-900">
                    {atleta.nombre_atleta}
                  </h3>
                  <p className="mt-2 text-sm text-stone-600">
                    Posicion {atleta.posicion} · Andarivel {atleta.andarivel}
                  </p>
                </div>

                <div className="text-left sm:text-right">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
                    Resultado final
                  </p>
                  <p className="mt-2 text-lg font-semibold text-stone-900">
                    {formatResultadoFinal(atleta, rankingMap)}
                  </p>
                  <p className="mt-2 text-sm text-stone-600">{formatEstado(atleta.estado)}</p>
                </div>
              </div>
            </Link>
          ))
        : null}
    </OrganizadorLayout>
  )
}
