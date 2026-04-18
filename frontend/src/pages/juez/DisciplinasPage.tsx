import { useNavigate } from 'react-router-dom'
import { DisciplinaCard } from '../../components/juez/DisciplinaCard'
import { JuezLayout } from '../../components/juez/JuezLayout'
import { useDisciplinasJuez } from '../../hooks/useDisciplinasJuez'
import useAuthStore from '../../stores/useAuthStore'
import useCompetenciaStore from '../../stores/useCompetenciaStore'

export function DisciplinasPage() {
  const navigate = useNavigate()
  const logout = useAuthStore((s) => s.logout)
  const seleccionarCompetencia = useCompetenciaStore((s) => s.seleccionarCompetencia)
  const { torneoActivo, disciplinas, subtitle, isLoading, hasError } = useDisciplinasJuez()

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

      {!isLoading && !hasError && !torneoActivo ? (
        <section className="rounded-3xl border border-slate-800 bg-slate-900/70 p-5 text-sm text-slate-300">
          No hay torneo en curso
        </section>
      ) : null}

      {!isLoading && !hasError && torneoActivo && disciplinas.length === 0 ? (
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
            <h2 className="mt-2 text-lg font-semibold text-slate-50">{torneoActivo?.nombre}</h2>
            <p className="mt-2 text-sm text-slate-400">
              {torneoActivo?.sede.nombre}, {torneoActivo?.sede.ciudad}
            </p>
          </section>

          {disciplinas.map((item) => (
            <DisciplinaCard
              key={item.competenciaId}
              disciplina={item.disciplina}
              estado={item.estado}
              onSelect={() => {
                seleccionarCompetencia({
                  torneoId: torneoActivo!.torneo_id,
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
