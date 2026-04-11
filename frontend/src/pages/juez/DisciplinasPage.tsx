import { useQuery } from '@tanstack/react-query'
import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { fetchCompetenciasPorTorneo, fetchEstadoCompetencia } from '../../api/competencia'
import { fetchDisciplinasDeJuez, fetchTorneos } from '../../api/torneo'
import { DisciplinaCard } from '../../components/juez/DisciplinaCard'
import { JuezLayout } from '../../components/juez/JuezLayout'
import useAuthStore from '../../stores/useAuthStore'
import useCompetenciaStore from '../../stores/useCompetenciaStore'

interface DisciplinaViewModel {
  disciplina: string
  estado: 'ACTIVA' | 'PENDIENTE'
  competenciaId: string
}

function esTorneoActivo(estado: string) {
  return estado === 'EJECUCION' || estado === 'EnEjecucion'
}

export function DisciplinasPage() {
  const navigate = useNavigate()
  const logout = useAuthStore((s) => s.logout)
  const email = useAuthStore((s) => s.email)
  const userId = useAuthStore((s) => s.userId)
  const seleccionarCompetencia = useCompetenciaStore((s) => s.seleccionarCompetencia)

  const torneoActivoQuery = useQuery({
    queryKey: ['torneos'],
    queryFn: fetchTorneos,
    select: (torneos) => torneos.find((torneo) => esTorneoActivo(torneo.estado)) ?? null,
  })

  const disciplinasQuery = useQuery({
    queryKey: ['disciplinas-juez', torneoActivoQuery.data?.torneo_id, userId],
    queryFn: () => fetchDisciplinasDeJuez(torneoActivoQuery.data!.torneo_id, userId!),
    enabled: Boolean(torneoActivoQuery.data?.torneo_id && userId),
  })

  const disciplinasViewQuery = useQuery({
    queryKey: ['mis-disciplinas', torneoActivoQuery.data?.torneo_id, userId],
    enabled: Boolean(torneoActivoQuery.data?.torneo_id && userId && disciplinasQuery.data),
    queryFn: async (): Promise<DisciplinaViewModel[]> => {
      const torneoId = torneoActivoQuery.data!.torneo_id
      const disciplinas = disciplinasQuery.data ?? []
      const competencias = await fetchCompetenciasPorTorneo(torneoId)

      const resultados = await Promise.all(
        disciplinas.map(async (disciplina) => {
          const competencia = competencias.find((item) => item.disciplina === disciplina)

          if (!competencia) {
            return null
          }

          const estado = await fetchEstadoCompetencia(competencia.competencia_id, disciplina)

          return {
            disciplina,
            competenciaId: competencia.competencia_id,
            estado: estado.estado === 'EnEjecucion' ? 'ACTIVA' : 'PENDIENTE',
          } satisfies DisciplinaViewModel
        }),
      )

      return resultados.filter((item): item is DisciplinaViewModel => item !== null)
    },
  })

  const subtitle = useMemo(() => {
    if (!torneoActivoQuery.data) {
      return email ?? 'Juez'
    }
    return `${email ?? 'Juez'} · ${torneoActivoQuery.data.nombre}`
  }, [email, torneoActivoQuery.data])

  const isLoading =
    torneoActivoQuery.isLoading || disciplinasQuery.isLoading || disciplinasViewQuery.isLoading
  const hasError =
    torneoActivoQuery.isError || disciplinasQuery.isError || disciplinasViewQuery.isError
  const disciplinas = disciplinasViewQuery.data ?? []

  return (
    <JuezLayout
      title="Mis disciplinas"
      subtitle={subtitle}
      actions={
        <button
          type="button"
          onClick={logout}
          className="rounded-full border border-slate-700 px-3 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate-200"
        >
          Salir
        </button>
      }
    >
      {isLoading ? (
        <section className="rounded-3xl border border-slate-800 bg-slate-900/70 p-5 text-sm text-slate-300">
          Cargando disciplinas asignadas...
        </section>
      ) : null}

      {!isLoading && hasError ? (
        <section className="rounded-3xl border border-red-500/30 bg-red-500/10 p-5 text-sm text-red-100">
          No se pudo cargar la informacion del juez.
        </section>
      ) : null}

      {!isLoading && !hasError && !torneoActivoQuery.data ? (
        <section className="rounded-3xl border border-slate-800 bg-slate-900/70 p-5 text-sm text-slate-300">
          No hay torneo en curso
        </section>
      ) : null}

      {!isLoading && !hasError && torneoActivoQuery.data && disciplinas.length === 0 ? (
        <section className="rounded-3xl border border-slate-800 bg-slate-900/70 p-5 text-sm text-slate-300">
          Sin disciplinas asignadas
        </section>
      ) : null}

      {!isLoading && !hasError && disciplinas.length > 0 ? (
        <>
          <section className="rounded-3xl border border-slate-800 bg-slate-900/70 p-5">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
              Torneo activo
            </p>
            <h2 className="mt-2 text-lg font-semibold text-slate-50">{torneoActivoQuery.data?.nombre}</h2>
            <p className="mt-2 text-sm text-slate-400">
              {torneoActivoQuery.data?.sede.nombre}, {torneoActivoQuery.data?.sede.ciudad}
            </p>
          </section>

          {disciplinas.map((item) => (
            <DisciplinaCard
              key={item.competenciaId}
              disciplina={item.disciplina}
              estado={item.estado}
              onSelect={() => {
                seleccionarCompetencia({
                  torneoId: torneoActivoQuery.data!.torneo_id,
                  competenciaId: item.competenciaId,
                  disciplinaActiva: item.disciplina,
                })
                void navigate('/juez/grilla')
              }}
            />
          ))}
        </>
      ) : null}
    </JuezLayout>
  )
}
