import { Link, useLocation, useNavigate } from 'react-router-dom'
import { JuezLayout } from '../../components/juez/JuezLayout'
import { useDisciplinasJuez } from '../../hooks/useDisciplinasJuez'
import useAuthStore from '../../stores/useAuthStore'
import useCompetenciaStore from '../../stores/useCompetenciaStore'

export function DisciplinasPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const logout = useAuthStore((s) => s.logout)
  const seleccionarCompetencia = useCompetenciaStore((s) => s.seleccionarCompetencia)
  const { torneoActivo, disciplinas, subtitle, isLoading, hasError } = useDisciplinasJuez()

  return (
    <JuezLayout
      title="Mis asignaciones"
      subtitle={subtitle}
      actions={
        <div className="flex shrink-0 flex-col gap-2">
          <Link
            to="/juez/mis-datos"
            className="rounded-full border border-slate-700 px-3 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate-400 hover:text-slate-200"
          >
            Mis Datos
          </Link>
          <button
            type="button"
            onClick={logout}
            className="rounded-full border border-slate-700 px-3 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate-200"
          >
            Salir
          </button>
        </div>
      }
    >
      {location.state && (location.state as { passwordUpdated?: boolean }).passwordUpdated ? (
        <section className="rounded-3xl border border-emerald-500/30 bg-emerald-500/10 p-5 text-sm text-emerald-100">
          Contrasena actualizada correctamente.
        </section>
      ) : null}

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

          <div className="flex gap-1 rounded-[2rem] border border-slate-700 bg-slate-900/85 overflow-hidden">
            {disciplinas.map((item) => {
              const isActive = item.estado === 'ACTIVA'
              return (
                <button
                  key={item.competenciaId}
                  type="button"
                  disabled={!isActive}
                  onClick={() => {
                    seleccionarCompetencia({
                      torneoId: torneoActivo!.torneo_id,
                      competenciaId: item.competenciaId,
                      disciplinaActiva: item.disciplina,
                    })
                    void navigate('/juez/grilla')
                  }}
                  className={`flex-1 py-3 text-xs font-semibold uppercase tracking-[0.18em] transition-colors ${
                    isActive
                      ? 'text-sky-400 hover:bg-slate-800'
                      : 'cursor-not-allowed text-slate-600'
                  }`}
                >
                  {item.disciplina}
                </button>
              )
            })}
          </div>
        </>
      ) : null}
    </JuezLayout>
  )
}
