import { useQuery } from '@tanstack/react-query'
import { Link, useSearchParams } from 'react-router-dom'
import { fetchTorneos } from '../../api/torneo'
import { GrillaPanel } from '../../components/organizador/GrillaPanel'
import { OrganizadorLayout } from '../../components/organizador/OrganizadorLayout'
import { TorneoRouteSelector } from '../../components/organizador/TorneoRouteSelector'

export function OrganizadorGrillaPage() {
  const [searchParams] = useSearchParams()
  const torneoId = searchParams.get('torneo_id')

  if (!torneoId) {
    return (
      <OrganizadorLayout
        title="Grilla"
        subtitle="Seleccionar torneo para generar, ajustar o confirmar la grilla"
      >
        <TorneoRouteSelector
          description="La grilla es una sección primaria del shell. Seleccioná un torneo para operar la disciplina desde esta vista."
          ctaLabel="Abrir grilla"
          buildHref={(nextTorneoId) => `/organizador/grilla?torneo_id=${nextTorneoId}`}
        />
      </OrganizadorLayout>
    )
  }

  return <GrillaTorneoPage torneoId={torneoId} />
}

interface GrillaTorneoPageProps {
  torneoId: string
}

function GrillaTorneoPage({ torneoId }: GrillaTorneoPageProps) {
  const torneosQuery = useQuery({
    queryKey: ['torneos-organizador'],
    queryFn: fetchTorneos,
  })
  const torneo = torneosQuery.data?.find((item) => item.torneo_id === torneoId) ?? null

  return (
    <OrganizadorLayout
      title="Grilla"
      subtitle={torneo ? `${torneo.nombre} · ${torneo.sede.ciudad}` : 'Configuración de grilla'}
      actions={
        <>
          <Link
            to="/organizador/grilla"
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
        La navegación primaria se mantiene fija. Los cambios de grilla ya no dependen del detalle de torneo como tab local.
      </section>
      <section className="rounded-[2rem] border border-slate-700 bg-white/95 p-5 shadow-[0_20px_60px_rgba(2,6,23,0.24)]">
        <GrillaPanel torneoId={torneoId} />
      </section>
    </OrganizadorLayout>
  )
}
