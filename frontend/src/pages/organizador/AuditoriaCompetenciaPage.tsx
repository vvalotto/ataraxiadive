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
        actions={
          <Link
            to="/organizador/dashboard"
            className="rounded-full border border-stone-300 bg-white px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-stone-700"
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
      subtitle={`Disciplina ${disciplina}`}
      actions={
        <>
          <Link
            to={torneoId ? `/organizador/torneos/${torneoId}/competencias` : '/organizador/dashboard'}
            className="rounded-full border border-stone-300 bg-white px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-stone-700"
          >
            Volver
          </Link>
          <Link
            to="/organizador/dashboard"
            className="rounded-full bg-stone-900 px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-stone-50"
          >
            Dashboard
          </Link>
        </>
      }
    >
      {isLoading ? (
        <section className="rounded-[2rem] border border-stone-300/80 bg-white/80 p-5 text-sm text-stone-600">
          Cargando auditoria de competencia...
        </section>
      ) : null}

      {hasError ? (
        <section className="rounded-[2rem] border border-red-300/60 bg-red-50 p-5 text-sm text-red-900">
          No se pudo cargar la auditoria de la competencia.
        </section>
      ) : null}

      {!isLoading && !hasError && estado ? (
        <section className="rounded-[2rem] border border-stone-300/80 bg-white/85 p-5 shadow-[0_20px_60px_rgba(120,93,54,0.08)]">
          <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
                Estado de disciplina
              </p>
              <h2 className="mt-2 text-2xl font-semibold text-stone-900">
                {formatEstado(estado.estado)}
              </h2>
            </div>

            {estado.estado === 'Finalizada' && estado.hash_sha256 ? (
              <div className="rounded-[1.5rem] border border-emerald-200 bg-emerald-50 px-4 py-3">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-emerald-800">
                  Hash SHA-256
                </p>
                <div className="mt-2 flex flex-wrap items-center gap-3">
                  <code
                    title={estado.hash_sha256}
                    className="rounded-full bg-white px-3 py-2 text-sm text-emerald-950"
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
        <section className="rounded-[2rem] border border-stone-300/80 bg-white/80 p-5 text-sm text-stone-600">
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
