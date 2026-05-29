import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
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
        subtitle="Asignación de jueces por disciplina y andarivel"
        showTournamentNavigation={false}
        simpleHeader
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
      activeTournamentId={torneoId}
      activeTournamentState={torneo?.estado}
      subtitle="Asignación de jueces por disciplina y andarivel"
    >
      <JuecesPanel torneoId={torneoId} />
    </OrganizadorLayout>
  )
}
