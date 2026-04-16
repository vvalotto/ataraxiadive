import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { fetchCompetenciasPorTorneo } from '../../api/competencia'
import { fetchTorneos } from '../../api/torneo'
import { OrganizadorLayout } from '../../components/organizador/OrganizadorLayout'

export function TorneoCompetenciasPage() {
  const { torneoId } = useParams()

  const torneosQuery = useQuery({
    queryKey: ['torneos-organizador'],
    queryFn: fetchTorneos,
  })
  const competenciasQuery = useQuery({
    queryKey: ['competencias-torneo', torneoId],
    queryFn: () => fetchCompetenciasPorTorneo(torneoId!),
    enabled: Boolean(torneoId),
  })

  const torneo = useMemo(
    () => torneosQuery.data?.find((item) => item.torneo_id === torneoId) ?? null,
    [torneoId, torneosQuery.data],
  )

  return (
    <OrganizadorLayout
      title="Competencias del torneo"
      subtitle={torneo ? `${torneo.nombre} · ${torneo.sede.ciudad}` : 'Seleccion de competencias'}
      actions={
        <Link
          to="/organizador/dashboard"
          className="rounded-full border border-stone-300 bg-white px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-stone-700"
        >
          Volver
        </Link>
      }
    >
      {competenciasQuery.isLoading ? (
        <section className="rounded-[2rem] border border-stone-300/80 bg-white/80 p-5 text-sm text-stone-600">
          Cargando competencias...
        </section>
      ) : null}

      {competenciasQuery.isError ? (
        <section className="rounded-[2rem] border border-red-300/60 bg-red-50 p-5 text-sm text-red-900">
          No se pudieron cargar las competencias del torneo.
        </section>
      ) : null}

      {!competenciasQuery.isLoading &&
      !competenciasQuery.isError &&
      (competenciasQuery.data?.length ?? 0) === 0 ? (
        <section className="rounded-[2rem] border border-stone-300/80 bg-white/80 p-5 text-sm text-stone-600">
          Este torneo no tiene competencias configuradas.
        </section>
      ) : null}

      {!competenciasQuery.isLoading && !competenciasQuery.isError
        ? competenciasQuery.data?.map((competencia) => (
            <article
              key={competencia.competencia_id}
              className="rounded-[2rem] border border-stone-300/80 bg-white/85 p-5 shadow-[0_20px_60px_rgba(120,93,54,0.08)]"
            >
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
                    Competencia
                  </p>
                  <h2 className="mt-2 text-xl font-semibold text-stone-900">
                    {competencia.disciplina}
                  </h2>
                  <p className="mt-2 text-sm text-stone-600">
                    ID {competencia.competencia_id}
                  </p>
                </div>
                <Link
                  to={`/organizador/competencias/${competencia.competencia_id}/auditoria?disciplina=${encodeURIComponent(competencia.disciplina)}&torneo_id=${encodeURIComponent(competencia.torneo_id)}`}
                  className="rounded-full bg-stone-900 px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-stone-50"
                >
                  Ver auditoria
                </Link>
              </div>
            </article>
          ))
        : null}
    </OrganizadorLayout>
  )
}
