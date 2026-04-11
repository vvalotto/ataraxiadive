import { Link } from 'react-router-dom'
import { JuezLayout } from '../../components/juez/JuezLayout'
import useCompetenciaStore from '../../stores/useCompetenciaStore'

export function GrillaPage() {
  const disciplinaActiva = useCompetenciaStore((s) => s.disciplinaActiva)
  const competenciaId = useCompetenciaStore((s) => s.competenciaId)

  return (
    <JuezLayout
      title="Grilla"
      subtitle={disciplinaActiva ? `${disciplinaActiva} · ${competenciaId}` : 'Sin competencia seleccionada'}
      actions={
        <Link
          to="/juez/disciplinas"
          className="rounded-full border border-slate-700 px-3 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate-200"
        >
          Volver
        </Link>
      }
    >
      <section className="rounded-3xl border border-slate-800 bg-slate-900/70 p-5 text-sm text-slate-300">
        Stub de grilla para US-4.3.1. La selección de disciplina y competencia activa ya quedó persistida en
        el store.
      </section>
    </JuezLayout>
  )
}
