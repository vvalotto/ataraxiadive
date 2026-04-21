import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { fetchTorneo, type EstadoTorneo, type TorneoDto } from '../../api/torneo'
import { AccionesPanel } from '../../components/organizador/AccionesPanel'
import { EjecucionPanel } from '../../components/organizador/EjecucionPanel'
import { FaseBadge } from '../../components/organizador/FaseBadge'
import { GrillaPanel } from '../../components/organizador/GrillaPanel'
import { InscriptosPanel } from '../../components/organizador/InscriptosPanel'
import { JuecesPanel } from '../../components/organizador/JuecesPanel'
import { OrganizadorLayout } from '../../components/organizador/OrganizadorLayout'

const TABS = ['Detalle', 'Inscriptos', 'Grilla', 'Jueces', 'Ejecucion'] as const
type TabTorneo = (typeof TABS)[number]

const TABS_POR_ESTADO: Record<EstadoTorneo, readonly TabTorneo[]> = {
  CREADO: ['Detalle'],
  INSCRIPCION_ABIERTA: ['Detalle', 'Inscriptos'],
  PREPARACION: ['Detalle', 'Inscriptos', 'Grilla', 'Jueces'],
  EJECUCION: ['Detalle', 'Inscriptos', 'Grilla', 'Jueces', 'Ejecucion'],
  PREMIACION: ['Detalle', 'Inscriptos', 'Grilla', 'Jueces', 'Ejecucion'],
  CERRADO: ['Detalle', 'Inscriptos', 'Grilla', 'Jueces', 'Ejecucion'],
  CANCELADO: [],
}

export function DetalleTorneoPage() {
  const { torneoId } = useParams<{ torneoId: string }>()
  const [transitionError, setTransitionError] = useState('')
  const torneoQuery = useQuery({
    queryKey: ['torneo', torneoId],
    queryFn: () => fetchTorneo(torneoId ?? ''),
    enabled: Boolean(torneoId),
  })
  const isCancelado = torneoQuery.data?.estado === 'CANCELADO'

  return (
    <OrganizadorLayout
      title={torneoQuery.data?.nombre ?? 'Torneo'}
      subtitle="Detalle del torneo y punto de partida del panel organizador"
      actions={
        <Link
          to="/organizador/dashboard"
          className="rounded-lg border border-stone-900 px-4 py-2 text-sm font-semibold text-stone-900"
        >
          Volver
        </Link>
      }
    >
      {torneoQuery.isLoading ? (
        <section className="rounded-lg border border-stone-300 bg-white p-5 text-sm text-stone-600">
          Cargando torneo...
        </section>
      ) : null}

      {torneoQuery.isError ? (
        <section className="rounded-lg border border-red-300 bg-red-50 p-5 text-sm text-red-900">
          No se pudo cargar el torneo.
        </section>
      ) : null}

      {torneoQuery.data ? (
        <>
          {isCancelado ? (
            <section className="rounded-lg border border-red-300 bg-red-50 p-5 shadow-[0_20px_60px_rgba(120,93,54,0.08)]">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <FaseBadge estado={torneoQuery.data.estado} />
                  <h2 className="mt-3 text-2xl font-semibold text-red-950">
                    {torneoQuery.data.nombre}
                  </h2>
                  <p className="mt-2 text-sm font-semibold text-red-900">
                    Torneo cancelado
                  </p>
                  <p className="mt-2 text-sm text-red-800">
                    El torneo quedo en estado terminal. La informacion operativa no se
                    muestra desde el flujo normal de gestion.
                  </p>
                </div>
              </div>

              <dl className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                <div className="rounded-lg border border-red-200 bg-white/70 p-4">
                  <dt className="text-xs font-semibold text-red-700">Fechas</dt>
                  <dd className="mt-1 text-sm text-red-950">
                    {torneoQuery.data.fecha_inicio} a {torneoQuery.data.fecha_fin}
                  </dd>
                </div>
                <div className="rounded-lg border border-red-200 bg-white/70 p-4">
                  <dt className="text-xs font-semibold text-red-700">Sede</dt>
                  <dd className="mt-1 text-sm text-red-950">
                    {torneoQuery.data.sede.nombre}, {torneoQuery.data.sede.ciudad},{' '}
                    {torneoQuery.data.sede.pais}
                  </dd>
                </div>
                <div className="rounded-lg border border-red-200 bg-white/70 p-4">
                  <dt className="text-xs font-semibold text-red-700">Entidad</dt>
                  <dd className="mt-1 text-sm text-red-950">
                    {torneoQuery.data.entidad_organizadora.nombre} ·{' '}
                    {torneoQuery.data.entidad_organizadora.tipo}
                  </dd>
                </div>
              </dl>
            </section>
          ) : (
            <TorneoOperativoPanel key={torneoQuery.data.estado} torneo={torneoQuery.data} />
          )}

          {!isCancelado && transitionError ? (
            <section className="rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-900">
              {transitionError}
            </section>
          ) : null}

          {!isCancelado ? (
            <AccionesPanel
              torneoId={torneoQuery.data.torneo_id}
              torneoNombre={torneoQuery.data.nombre}
              estado={torneoQuery.data.estado}
              onSuccess={async () => {
                setTransitionError('')
                await torneoQuery.refetch()
              }}
              onError={setTransitionError}
            />
          ) : null}
        </>
      ) : null}
    </OrganizadorLayout>
  )
}

interface TorneoOperativoPanelProps {
  torneo: TorneoDto
}

function TorneoOperativoPanel({ torneo }: TorneoOperativoPanelProps) {
  const [activeTab, setActiveTab] = useState<TabTorneo>('Detalle')
  const tabsHabilitadas = TABS_POR_ESTADO[torneo.estado]

  function isTabHabilitada(tab: TabTorneo): boolean {
    return tabsHabilitadas.includes(tab)
  }

  const activeTabActual = isTabHabilitada(activeTab) ? activeTab : 'Detalle'

  return (
    <section className="rounded-lg border border-stone-300 bg-white p-5 shadow-[0_20px_60px_rgba(120,93,54,0.08)]">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <FaseBadge estado={torneo.estado} />
          <h2 className="mt-3 text-2xl font-semibold text-stone-950">{torneo.nombre}</h2>
          <p className="mt-2 text-sm text-stone-600">
            {torneo.fecha_inicio} a {torneo.fecha_fin}
          </p>
        </div>
        <Link
          to={`/organizador/torneos/${torneo.torneo_id}/competencias`}
          className="rounded-lg bg-stone-900 px-4 py-2 text-center text-sm font-semibold text-white"
        >
          Ver competencias
        </Link>
      </div>

      <div className="mt-6 flex gap-2 overflow-x-auto border-b border-stone-200 pb-2">
        {TABS.map((tab) => {
          const habilitada = isTabHabilitada(tab)
          return (
            <button
              key={tab}
              type="button"
              onClick={() => {
                if (habilitada) setActiveTab(tab)
              }}
              disabled={!habilitada}
              aria-disabled={!habilitada}
              className={[
                'min-h-10 rounded-lg px-4 py-2 text-sm font-semibold',
                activeTabActual === tab && habilitada
                  ? 'bg-stone-900 text-white'
                  : 'border border-stone-300 text-stone-800',
                habilitada ? '' : 'cursor-not-allowed bg-stone-100 text-stone-400 opacity-70',
              ].join(' ')}
            >
              {tab}
            </button>
          )
        })}
      </div>

      {activeTabActual === 'Detalle' ? (
        <dl className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div className="rounded-lg border border-stone-200 p-4">
            <dt className="text-xs font-semibold text-stone-500">Sede</dt>
            <dd className="mt-1 text-sm text-stone-900">
              {torneo.sede.nombre}, {torneo.sede.ciudad}, {torneo.sede.pais}
            </dd>
          </div>
          <div className="rounded-lg border border-stone-200 p-4">
            <dt className="text-xs font-semibold text-stone-500">Entidad</dt>
            <dd className="mt-1 text-sm text-stone-900">
              {torneo.entidad_organizadora.nombre} · {torneo.entidad_organizadora.tipo}
            </dd>
          </div>
          <div className="rounded-lg border border-stone-200 p-4">
            <dt className="text-xs font-semibold text-stone-500">Estado</dt>
            <dd className="mt-1 text-sm text-stone-900">
              <FaseBadge estado={torneo.estado} />
            </dd>
          </div>
        </dl>
      ) : null}

      {activeTabActual === 'Inscriptos' && isTabHabilitada('Inscriptos') ? (
        <div className="mt-6">
          <InscriptosPanel torneoId={torneo.torneo_id} />
        </div>
      ) : null}

      {activeTabActual === 'Grilla' && isTabHabilitada('Grilla') ? (
        <div className="mt-6">
          <GrillaPanel torneoId={torneo.torneo_id} />
        </div>
      ) : null}

      {activeTabActual === 'Jueces' && isTabHabilitada('Jueces') ? (
        <div className="mt-6">
          <JuecesPanel torneoId={torneo.torneo_id} />
        </div>
      ) : null}

      {activeTabActual === 'Ejecucion' && isTabHabilitada('Ejecucion') ? (
        <div className="mt-6">
          <EjecucionPanel torneoId={torneo.torneo_id} />
        </div>
      ) : null}
    </section>
  )
}
