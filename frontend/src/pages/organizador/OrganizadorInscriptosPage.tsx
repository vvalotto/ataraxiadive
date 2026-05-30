import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import { fetchTorneos } from '../../api/torneo'
import { InscriptosPanel } from '../../components/organizador/InscriptosPanel'
import { OrganizadorLayout } from '../../components/organizador/OrganizadorLayout'
import { TorneoRouteSelector } from '../../components/organizador/TorneoRouteSelector'

export function OrganizadorInscriptosPage() {
  const [searchParams] = useSearchParams()
  const torneoId = searchParams.get('torneo_id')

  if (!torneoId) {
    return (
      <OrganizadorLayout
        title="Inscriptos"
        subtitle="Gestión de inscripciones y anuncios de performance"
        showTournamentNavigation={false}
        simpleHeader
      >
        <TorneoRouteSelector
          description="La gestión de inscriptos es una sección primaria del shell durante la inscripción abierta. Seleccioná un torneo para revisar atletas, disciplinas y AP declaradas."
          ctaLabel="Abrir inscriptos"
          buildHref={(nextTorneoId) => `/organizador/inscriptos?torneo_id=${nextTorneoId}`}
        />
      </OrganizadorLayout>
    )
  }

  return <InscriptosTorneoPage torneoId={torneoId} />
}

interface InscriptosTorneoPageProps {
  torneoId: string
}

function InscriptosTorneoPage({ torneoId }: InscriptosTorneoPageProps) {
  const torneosQuery = useQuery({
    queryKey: ['torneos-organizador'],
    queryFn: fetchTorneos,
  })
  const torneo = torneosQuery.data?.find((item) => item.torneo_id === torneoId) ?? null

  return (
    <OrganizadorLayout
      title="Inscriptos"
      activeTournamentId={torneoId}
      activeTournamentState={torneo?.estado}
      subtitle="Gestión de inscripciones y anuncios de performance"
    >
      {torneo ? (
        <InscriptosPanel torneoId={torneoId} torneoEstado={torneo.estado} />
      ) : (
        <section className="rounded-[2rem] border border-slate-700 bg-slate-900/70 p-5 text-sm text-slate-300">
          Cargando torneo...
        </section>
      )}
    </OrganizadorLayout>
  )
}
