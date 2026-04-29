import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
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
        showTournamentNavigation={false}
        simpleHeader
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
      activeTournamentId={torneoId}
      activeTournamentState={torneo?.estado}
      subtitle={torneo ? `${torneo.nombre} · ${torneo.sede.ciudad}` : 'Configuración de grilla'}
    >
      <GrillaPanel torneoId={torneoId} />
    </OrganizadorLayout>
  )
}
