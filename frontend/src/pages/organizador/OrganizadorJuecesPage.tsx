import { useQuery } from '@tanstack/react-query'
import { Link, useSearchParams } from 'react-router-dom'
import { fetchTorneos } from '../../api/torneo'
import { JuecesPanel } from '../../components/organizador/JuecesPanel'
import { OrganizadorLayout } from '../../components/organizador/OrganizadorLayout'
import { TorneoRouteSelector } from '../../components/organizador/TorneoRouteSelector'

export function OrganizadorJuecesPage() {
  const [searchParams] = useSearchParams()
  const torneoId = searchParams.get('torneo_id')

  if (!torneoId) {
    return (
      <OrganizadorLayout
        title="Jueces"
        subtitle="Seleccionar torneo para asignar jueces por disciplina"
      >
        <TorneoRouteSelector
          description="La asignación de jueces ya cuelga de una ruta primaria propia. Seleccioná un torneo para operar esta sección sin pasar por tabs internas."
          ctaLabel="Abrir jueces"
          buildHref={(nextTorneoId) => `/organizador/jueces?torneo_id=${nextTorneoId}`}
        />
      </OrganizadorLayout>
    )
  }

  return <JuecesTorneoPage torneoId={torneoId} />
}

interface JuecesTorneoPageProps {
  torneoId: string
}

function JuecesTorneoPage({ torneoId }: JuecesTorneoPageProps) {
  const torneosQuery = useQuery({
    queryKey: ['torneos-organizador'],
    queryFn: fetchTorneos,
  })
  const torneo = torneosQuery.data?.find((item) => item.torneo_id === torneoId) ?? null

  return (
    <OrganizadorLayout
      title="Jueces"
      subtitle={torneo ? `${torneo.nombre} · ${torneo.sede.ciudad}` : 'Asignación de jueces'}
      actions={
        <>
          <Link
            to="/organizador/jueces"
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
      <section className="rounded-[2rem] border border-slate-700 bg-slate-900/75 p-5 text-sm text-slate-300">
        Esta sección mantiene visible la navegación primaria mientras se opera la asignación de jueces por disciplina.
      </section>
      <section className="rounded-[2rem] border border-slate-700 bg-white/95 p-5 shadow-[0_20px_60px_rgba(2,6,23,0.24)]">
        <JuecesPanel torneoId={torneoId} />
      </section>
    </OrganizadorLayout>
  )
}
