import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { fetchTorneo } from '../../api/torneo'
import { AccionesPanel } from '../../components/organizador/AccionesPanel'
import { FaseBadge } from '../../components/organizador/FaseBadge'
import { GrillaPanel } from '../../components/organizador/GrillaPanel'
import { InscriptosPanel } from '../../components/organizador/InscriptosPanel'
import { OrganizadorLayout } from '../../components/organizador/OrganizadorLayout'

const TABS = ['Detalle', 'Inscriptos', 'Grilla', 'Jueces', 'Ejecucion'] as const

export function DetalleTorneoPage() {
  const { torneoId } = useParams<{ torneoId: string }>()
  const [activeTab, setActiveTab] = useState<(typeof TABS)[number]>('Detalle')
  const [transitionError, setTransitionError] = useState('')
  const torneoQuery = useQuery({
    queryKey: ['torneo', torneoId],
    queryFn: () => fetchTorneo(torneoId ?? ''),
    enabled: Boolean(torneoId),
  })

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
          <section className="rounded-lg border border-stone-300 bg-white p-5 shadow-[0_20px_60px_rgba(120,93,54,0.08)]">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <FaseBadge estado={torneoQuery.data.estado} />
                <h2 className="mt-3 text-2xl font-semibold text-stone-950">
                  {torneoQuery.data.nombre}
                </h2>
                <p className="mt-2 text-sm text-stone-600">
                  {torneoQuery.data.fecha_inicio} a {torneoQuery.data.fecha_fin}
                </p>
              </div>
              <Link
                to={`/organizador/torneos/${torneoQuery.data.torneo_id}/competencias`}
                className="rounded-lg bg-stone-900 px-4 py-2 text-center text-sm font-semibold text-white"
              >
                Ver competencias
              </Link>
            </div>

            <div className="mt-6 flex gap-2 overflow-x-auto border-b border-stone-200 pb-2">
              {TABS.map((tab) => (
                <button
                  key={tab}
                  type="button"
                  onClick={() => setActiveTab(tab)}
                  className={[
                    'min-h-10 rounded-lg px-4 py-2 text-sm font-semibold',
                    activeTab === tab
                      ? 'bg-stone-900 text-white'
                      : 'border border-stone-300 text-stone-800',
                  ].join(' ')}
                >
                  {tab}
                </button>
              ))}
            </div>

            {activeTab === 'Detalle' ? (
              <dl className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                <div className="rounded-lg border border-stone-200 p-4">
                  <dt className="text-xs font-semibold text-stone-500">Sede</dt>
                  <dd className="mt-1 text-sm text-stone-900">
                    {torneoQuery.data.sede.nombre}, {torneoQuery.data.sede.ciudad},{' '}
                    {torneoQuery.data.sede.pais}
                  </dd>
                </div>
                <div className="rounded-lg border border-stone-200 p-4">
                  <dt className="text-xs font-semibold text-stone-500">Entidad</dt>
                  <dd className="mt-1 text-sm text-stone-900">
                    {torneoQuery.data.entidad_organizadora.nombre} ·{' '}
                    {torneoQuery.data.entidad_organizadora.tipo}
                  </dd>
                </div>
                <div className="rounded-lg border border-stone-200 p-4">
                  <dt className="text-xs font-semibold text-stone-500">Estado</dt>
                  <dd className="mt-1 text-sm text-stone-900">
                    <FaseBadge estado={torneoQuery.data.estado} />
                  </dd>
                </div>
              </dl>
            ) : null}

            {activeTab === 'Inscriptos' ? (
              <div className="mt-6">
                <InscriptosPanel torneoId={torneoQuery.data.torneo_id} />
              </div>
            ) : null}

            {activeTab === 'Grilla' ? (
              <div className="mt-6">
                <GrillaPanel torneoId={torneoQuery.data.torneo_id} />
              </div>
            ) : null}

            {activeTab !== 'Detalle' && activeTab !== 'Inscriptos' && activeTab !== 'Grilla' ? (
              <div className="mt-6 rounded-lg border border-stone-200 bg-stone-50 p-4 text-sm text-stone-600">
                {activeTab} quedara disponible en las siguientes US de INC-5.1.
              </div>
            ) : null}
          </section>

          {transitionError ? (
            <section className="rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-900">
              {transitionError}
            </section>
          ) : null}

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
        </>
      ) : null}
    </OrganizadorLayout>
  )
}
