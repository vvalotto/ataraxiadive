import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  cambiarAceptacionInscripcion,
  fetchInscripcionDetalle,
  type InscripcionDetalleDto,
} from '../../api/registro'

interface Props {
  inscripcionId: string
  torneoId: string
  onClose: () => void
}

function Campo({ label, valor }: { label: string; valor: string | null | undefined }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
        {label}
      </span>
      <span className="text-sm text-slate-200">{valor || '—'}</span>
    </div>
  )
}

function AdjuntoLink({ label, url }: { label: string; url: string | null | undefined }) {
  if (!url) return null
  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-center gap-1.5 rounded-xl border border-slate-700 bg-slate-800/60 px-3 py-2 text-xs font-semibold text-sky-400 hover:border-sky-500/50 hover:text-sky-300 transition-colors"
    >
      <svg className="h-3.5 w-3.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
      </svg>
      {label}
    </a>
  )
}

function AceptacionControls({
  detalle,
  onCambiar,
  isPending,
}: {
  detalle: InscripcionDetalleDto
  onCambiar: (estado: 'ACEPTADO' | 'RECHAZADO') => void
  isPending: boolean
}) {
  const esAceptado = detalle.estado_aceptacion === 'ACEPTADO'
  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-2">
        <span className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
          Estado de inscripción
        </span>
        {esAceptado ? (
          <span className="rounded-full bg-emerald-500/20 px-2 py-0.5 text-xs font-semibold text-emerald-400">
            ACEPTADO
          </span>
        ) : (
          <span className="rounded-full bg-red-500/20 px-2 py-0.5 text-xs font-semibold text-red-400">
            RECHAZADO
          </span>
        )}
      </div>
      <div className="flex gap-2">
        {!esAceptado && (
          <button
            type="button"
            disabled={isPending}
            onClick={() => onCambiar('ACEPTADO')}
            className="rounded-xl bg-emerald-600 px-4 py-2 text-xs font-semibold uppercase tracking-[0.14em] text-white hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
          >
            {isPending ? 'Guardando...' : 'Aceptar'}
          </button>
        )}
        {esAceptado && (
          <button
            type="button"
            disabled={isPending}
            onClick={() => onCambiar('RECHAZADO')}
            className="rounded-xl bg-red-700 px-4 py-2 text-xs font-semibold uppercase tracking-[0.14em] text-white hover:bg-red-600 disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
          >
            {isPending ? 'Guardando...' : 'Rechazar'}
          </button>
        )}
      </div>
    </div>
  )
}

export function InscripcionDetalleDrawer({ inscripcionId, torneoId, onClose }: Props) {
  const queryClient = useQueryClient()

  const query = useQuery({
    queryKey: ['inscripcion-detalle', inscripcionId],
    queryFn: () => fetchInscripcionDetalle(inscripcionId),
  })

  const mutation = useMutation({
    mutationFn: (estado: 'ACEPTADO' | 'RECHAZADO') =>
      cambiarAceptacionInscripcion(inscripcionId, estado),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['inscripcion-detalle', inscripcionId] })
      await queryClient.invalidateQueries({ queryKey: ['torneo-inscriptos-ap', torneoId] })
    },
  })

  const detalle = query.data

  return (
    <aside className="flex h-full w-full flex-col rounded-[2rem] border border-slate-700 bg-slate-900/95 shadow-[0_20px_60px_rgba(2,6,23,0.4)]">
      <div className="flex items-center justify-between border-b border-slate-800 px-5 py-4">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
          Detalle de inscripción
        </p>
        <button
          type="button"
          onClick={onClose}
          aria-label="Cerrar panel"
          className="rounded-xl p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white transition-colors"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-5">
        {query.isLoading && (
          <p className="text-sm text-slate-400">Cargando datos del atleta...</p>
        )}

        {query.isError && (
          <p className="text-sm text-red-400">No se pudo cargar el detalle de la inscripción.</p>
        )}

        {detalle && (
          <div className="flex flex-col gap-6">
            <div>
              <h3 className="mb-4 text-lg font-semibold text-white">
                {detalle.nombre} {detalle.apellido}
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <Campo label="Categoría" valor={detalle.categoria} />
                <Campo label="Club" valor={detalle.club} />
                <Campo label="Brevet" valor={detalle.brevet} />
                <Campo label="DNI" valor={detalle.dni} />
                <Campo label="Teléfono" valor={detalle.telefono} />
              </div>
            </div>

            {(detalle.apto_medico_url || detalle.constancia_pago_url) && (
              <div className="flex flex-col gap-2">
                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                  Adjuntos
                </p>
                <AdjuntoLink label="Ver apto médico" url={detalle.apto_medico_url} />
                <AdjuntoLink label="Ver constancia de pago" url={detalle.constancia_pago_url} />
              </div>
            )}

            {mutation.isError && (
              <p className="rounded-xl border border-red-500/40 bg-red-950/40 p-3 text-xs text-red-300">
                No se pudo actualizar el estado de aceptación.
              </p>
            )}

            <AceptacionControls
              detalle={detalle}
              onCambiar={(estado) => mutation.mutate(estado)}
              isPending={mutation.isPending}
            />
          </div>
        )}
      </div>
    </aside>
  )
}
