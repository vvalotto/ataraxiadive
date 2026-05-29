import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useParams, useSearchParams } from 'react-router-dom'
import {
  fetchCompetenciasPorTorneo,
  type CompetenciaResumenDto,
} from '../../api/competencia'
import {
  fetchTorneos,
  listarDisciplinasTorneo,
  type DisciplinaTorneoDto,
} from '../../api/torneo'
import { OrganizadorLayout } from '../../components/organizador/OrganizadorLayout'
import { TorneoRouteSelector } from '../../components/organizador/TorneoRouteSelector'

interface DisciplinaCompetenciaCard {
  disciplina: string
  competencia: CompetenciaResumenDto | null
}

export function TorneoCompetenciasPage() {
  const { torneoId: torneoIdParam } = useParams()
  const [searchParams] = useSearchParams()
  const torneoId = torneoIdParam ?? searchParams.get('torneo_id') ?? undefined

  if (!torneoId) {
    return (
      <OrganizadorLayout
        title="Audit Log"
        subtitle="Historial de performances y trazabilidad por disciplina"
        showTournamentNavigation={false}
        simpleHeader
      >
        <TorneoRouteSelector
          description="El audit log ahora es una sección primaria. Seleccioná un torneo para revisar las competencias y abrir la trazabilidad por atleta."
          ctaLabel="Abrir audit log"
          buildHref={(nextTorneoId) => `/organizador/audit-log?torneo_id=${nextTorneoId}`}
        />
      </OrganizadorLayout>
    )
  }

  return <TorneoCompetenciasContent torneoId={torneoId} />
}

interface TorneoCompetenciasContentProps {
  torneoId: string
}

function TorneoCompetenciasContent({ torneoId }: TorneoCompetenciasContentProps) {
  const torneosQuery = useQuery({
    queryKey: ['torneos-organizador'],
    queryFn: fetchTorneos,
  })
  const competenciasQuery = useQuery({
    queryKey: ['competencias-torneo', torneoId],
    queryFn: () => fetchCompetenciasPorTorneo(torneoId!),
    enabled: Boolean(torneoId),
  })
  const disciplinasQuery = useQuery({
    queryKey: ['torneo-disciplinas', torneoId],
    queryFn: () => listarDisciplinasTorneo(torneoId!),
    enabled: Boolean(torneoId),
  })

  const torneo = useMemo(
    () => torneosQuery.data?.find((item) => item.torneo_id === torneoId) ?? null,
    [torneoId, torneosQuery.data],
  )
  const disciplinasCompetencias = useMemo(
    () => componerDisciplinasCompetencias(disciplinasQuery.data ?? [], competenciasQuery.data ?? []),
    [competenciasQuery.data, disciplinasQuery.data],
  )
  const isLoading = disciplinasQuery.isLoading || competenciasQuery.isLoading
  const isError = disciplinasQuery.isError || competenciasQuery.isError

  return (
    <OrganizadorLayout
      title="Audit Log"
      activeTournamentId={torneoId}
      activeTournamentState={torneo?.estado}
      subtitle="Historial de performances y trazabilidad por disciplina"
    >
      {isLoading ? (
        <section className="rounded-[2rem] border border-slate-700 bg-slate-900/70 p-5 text-sm text-slate-300">
          Cargando competencias...
        </section>
      ) : null}

      {isError ? (
        <section className="rounded-[2rem] border border-red-500/40 bg-red-950/40 p-5 text-sm text-red-100">
          No se pudieron cargar las disciplinas o competencias del torneo.
        </section>
      ) : null}

      {!isLoading && !isError && disciplinasCompetencias.length === 0 ? (
        <section className="rounded-[2rem] border border-slate-700 bg-slate-900/70 p-5 text-sm text-slate-300">
          Este torneo no tiene disciplinas configuradas.
        </section>
      ) : null}

      {!isLoading && !isError
        ? disciplinasCompetencias.map((item) => (
            <article
              key={item.disciplina}
              className="rounded-[2rem] border border-slate-700 bg-slate-900/85 p-5 shadow-[0_20px_60px_rgba(2,6,23,0.24)]"
            >
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                    Disciplina
                  </p>
                  <h2 className="mt-2 text-xl font-semibold text-white">
                    {item.disciplina}
                  </h2>
                  <p className="mt-2 text-sm text-slate-300">
                    {item.competencia
                      ? `Competencia ${item.competencia.competencia_id}`
                      : 'Competencia pendiente: generar grilla desde la sección Grilla'}
                  </p>
                </div>
                {item.competencia ? (
                  <Link
                    to={`/organizador/competencias/${item.competencia.competencia_id}/auditoria?disciplina=${encodeURIComponent(item.disciplina)}&torneo_id=${encodeURIComponent(item.competencia.torneo_id)}`}
                    className="rounded-full border border-sky-400 bg-sky-400/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-sky-300"
                  >
                    Ver auditoria
                  </Link>
                ) : (
                  <button
                    type="button"
                    disabled
                    className="cursor-not-allowed rounded-full border border-slate-700 bg-slate-950 px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate-500"
                  >
                    Ver auditoria
                  </button>
                )}
              </div>
            </article>
          ))
        : null}
    </OrganizadorLayout>
  )
}

function componerDisciplinasCompetencias(
  disciplinas: DisciplinaTorneoDto[],
  competencias: CompetenciaResumenDto[],
): DisciplinaCompetenciaCard[] {
  const competenciasPorDisciplina = new Map(
    competencias.map((competencia) => [competencia.disciplina, competencia]),
  )

  return disciplinas.map((disciplina) => ({
    disciplina: disciplina.disciplina,
    competencia: competenciasPorDisciplina.get(disciplina.disciplina) ?? null,
  }))
}
