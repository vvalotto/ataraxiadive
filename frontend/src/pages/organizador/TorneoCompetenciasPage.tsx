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
        subtitle="Seleccionar torneo para inspeccionar competencias y trazas"
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
      title="Competencias del torneo"
      subtitle={torneo ? `${torneo.nombre} · ${torneo.sede.ciudad}` : 'Seleccion de competencias'}
      actions={
        <>
          <Link
            to="/organizador/audit-log"
            className="rounded-full border border-slate-600 bg-slate-800 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-slate-100"
          >
            Cambiar torneo
          </Link>
          <Link
            to={`/organizador/panel?torneo_id=${torneoId}`}
            className="rounded-full border border-slate-600 bg-slate-900 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-slate-100"
          >
            Panel
          </Link>
        </>
      }
    >
      {isLoading ? (
        <section className="rounded-[2rem] border border-stone-300/80 bg-white/80 p-5 text-sm text-stone-600">
          Cargando competencias...
        </section>
      ) : null}

      {isError ? (
        <section className="rounded-[2rem] border border-red-300/60 bg-red-50 p-5 text-sm text-red-900">
          No se pudieron cargar las disciplinas o competencias del torneo.
        </section>
      ) : null}

      {!isLoading && !isError && disciplinasCompetencias.length === 0 ? (
        <section className="rounded-[2rem] border border-stone-300/80 bg-white/80 p-5 text-sm text-stone-600">
          Este torneo no tiene disciplinas configuradas.
        </section>
      ) : null}

      {!isLoading && !isError
        ? disciplinasCompetencias.map((item) => (
            <article
              key={item.disciplina}
              className="rounded-[2rem] border border-stone-300/80 bg-white/85 p-5 shadow-[0_20px_60px_rgba(120,93,54,0.08)]"
            >
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
                    Disciplina
                  </p>
                  <h2 className="mt-2 text-xl font-semibold text-stone-900">
                    {item.disciplina}
                  </h2>
                  <p className="mt-2 text-sm text-stone-600">
                    {item.competencia
                      ? `Competencia ${item.competencia.competencia_id}`
                      : 'Competencia pendiente: generar grilla desde la sección Grilla'}
                  </p>
                </div>
                {item.competencia ? (
                  <Link
                    to={`/organizador/competencias/${item.competencia.competencia_id}/auditoria?disciplina=${encodeURIComponent(item.disciplina)}&torneo_id=${encodeURIComponent(item.competencia.torneo_id)}`}
                    className="rounded-full bg-stone-900 px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-stone-50"
                  >
                    Ver auditoria
                  </Link>
                ) : (
                  <button
                    type="button"
                    disabled
                    className="cursor-not-allowed rounded-full border border-stone-300 bg-stone-100 px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-stone-400"
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
