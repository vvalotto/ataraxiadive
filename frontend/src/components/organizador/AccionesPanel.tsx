import { useState } from 'react'
import {
  abrirInscripcion,
  cancelarTorneo,
  cerrarInscripcion,
  cerrarTorneo,
  iniciarEjecucion,
  iniciarPremiacion,
  type EstadoTorneo,
} from '../../api/torneo'

interface AccionFase {
  label: string
  run: (torneoId: string) => Promise<void>
  variant?: 'primary' | 'secondary'
}

const ACCIONES_POR_ESTADO: Partial<Record<EstadoTorneo, AccionFase[]>> = {
  CREADO: [{ label: 'Abrir inscripcion', run: abrirInscripcion, variant: 'primary' }],
  INSCRIPCION_ABIERTA: [
    { label: 'Cerrar inscripcion', run: cerrarInscripcion, variant: 'primary' },
  ],
  PREPARACION: [{ label: 'Iniciar ejecucion', run: iniciarEjecucion, variant: 'primary' }],
  EJECUCION: [{ label: 'Premiación', run: iniciarPremiacion, variant: 'primary' }],
  PREMIACION: [{ label: 'Cerrar torneo', run: cerrarTorneo, variant: 'primary' }],
}

const ESTADOS_TERMINALES = new Set<EstadoTorneo>(['CERRADO', 'CANCELADO'])

interface AccionesPanelProps {
  torneoId: string
  torneoNombre: string
  estado: EstadoTorneo
  premiacionPendientes?: string[] | null
  isPremiacionStatusLoading?: boolean
  onSuccess: () => Promise<void>
  onError: (message: string) => void
  showPhaseActions?: boolean
}

function buttonClass(variant: 'primary' | 'secondary' | 'danger'): string {
  if (variant === 'danger') {
    return 'rounded-xl border border-red-500/70 bg-red-950 px-4 py-2 text-sm font-semibold text-red-100 shadow-[0_0_0_1px_rgba(239,68,68,0.18)] disabled:cursor-not-allowed disabled:opacity-60'
  }
  if (variant === 'secondary') {
    return 'rounded-lg border border-stone-700 px-4 py-2 text-sm font-semibold text-stone-900 disabled:cursor-not-allowed disabled:opacity-60'
  }
  return 'rounded-lg bg-stone-900 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-stone-500'
}

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) return error.message
  return 'No se pudo transicionar el torneo'
}

export function AccionesPanel({
  torneoId,
  torneoNombre,
  estado,
  premiacionPendientes,
  isPremiacionStatusLoading = false,
  onSuccess,
  onError,
  showPhaseActions = true,
}: AccionesPanelProps) {
  const [runningAction, setRunningAction] = useState<string | null>(null)
  const [showCancelDialog, setShowCancelDialog] = useState(false)
  const [cancelConfirmation, setCancelConfirmation] = useState('')
  const puedeCancelar = !ESTADOS_TERMINALES.has(estado)
  const canConfirmCancel = cancelConfirmation === torneoNombre
  const bloqueoPremiacion =
    estado === 'EJECUCION' &&
    (isPremiacionStatusLoading || (premiacionPendientes?.length ?? 0) > 0)
  const acciones = ACCIONES_POR_ESTADO[estado] ?? []

  async function runAction(action: AccionFase) {
    if (action.label === 'Premiación' && bloqueoPremiacion) {
      return
    }
    setRunningAction(action.label)
    onError('')
    try {
      await action.run(torneoId)
      await onSuccess()
    } catch (error) {
      onError(getErrorMessage(error))
    } finally {
      setRunningAction(null)
    }
  }

  async function confirmCancel() {
    if (!canConfirmCancel) return
    setRunningAction('Cancelar torneo')
    onError('')
    try {
      await cancelarTorneo(torneoId)
      setShowCancelDialog(false)
      await onSuccess()
    } catch (error) {
      onError(getErrorMessage(error))
    } finally {
      setRunningAction(null)
    }
  }

  function openCancelDialog() {
    setCancelConfirmation('')
    setShowCancelDialog(true)
  }

  function closeCancelDialog() {
    if (runningAction !== null) return
    setCancelConfirmation('')
    setShowCancelDialog(false)
  }

  if ((showPhaseActions ? acciones.length === 0 : true) && !puedeCancelar) {
    return null
  }

  return (
    <section className="rounded-[1.75rem] border border-red-500/50 bg-slate-950 p-5 shadow-[0_20px_60px_rgba(127,29,29,0.32)]">
      {showPhaseActions ? (
        <>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h3 className="text-lg font-semibold text-white">Acciones de fase</h3>
              <p className="mt-1 text-sm text-slate-300">
                Ejecuta transiciones permitidas por el ciclo de vida del torneo.
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              {acciones.map((action) => (
                <button
                  key={action.label}
                  type="button"
                  onClick={() => void runAction(action)}
                  disabled={
                    runningAction !== null ||
                    (action.label === 'Premiación' && bloqueoPremiacion)
                  }
                  className={buttonClass(action.variant ?? 'primary')}
                >
                  {runningAction === action.label ? 'Procesando...' : action.label}
                </button>
              ))}
            </div>
          </div>

          {estado === 'EJECUCION' && isPremiacionStatusLoading ? (
            <p className="mt-3 text-sm font-semibold text-slate-300">
              Verificando cierre de disciplinas antes de pasar a premiacion...
            </p>
          ) : null}

          {estado === 'EJECUCION' && premiacionPendientes && premiacionPendientes.length > 0 ? (
            <p className="mt-3 text-sm font-semibold text-amber-300">
              Falta cerrar {premiacionPendientes.length}{' '}
              {premiacionPendientes.length === 1 ? 'disciplina' : 'disciplinas'}:{' '}
              {premiacionPendientes.join(', ')}.
            </p>
          ) : null}
        </>
      ) : null}

      {puedeCancelar ? (
        <div className={`${showPhaseActions ? 'mt-5 border-t border-red-500/35 pt-4' : ''}`}>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.14em] text-red-200">
                Zona de peligro
              </p>
              <p className="mt-1 text-sm text-red-100/80">
                Cancelar el torneo detiene el flujo operativo.
              </p>
            </div>
            <button
              type="button"
              onClick={openCancelDialog}
              disabled={runningAction !== null}
              className={buttonClass('danger')}
            >
              Cancelar torneo
            </button>
          </div>
        </div>
      ) : null}

      {showCancelDialog ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 px-4">
          <form
            role="dialog"
            aria-modal="true"
            aria-labelledby="cancelar-torneo-title"
            onSubmit={(event) => {
              event.preventDefault()
              void confirmCancel()
            }}
            className="w-full max-w-md rounded-[1.5rem] border border-red-500/40 bg-slate-950 p-5 shadow-2xl"
          >
            <h3 id="cancelar-torneo-title" className="text-lg font-semibold text-white">
              Cancelar torneo {torneoNombre}
            </h3>
            <p className="mt-2 text-sm text-red-100/80">
              Esta accion no se puede deshacer. Escribi el nombre exacto del torneo para
              confirmar.
            </p>
            <label className="mt-5 block text-sm font-semibold text-slate-200">
              Nombre del torneo
              <input
                value={cancelConfirmation}
                onChange={(event) => setCancelConfirmation(event.target.value)}
                disabled={runningAction !== null}
                autoFocus
                className="mt-2 min-h-10 w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white"
                placeholder={torneoNombre}
              />
            </label>
            <div className="mt-5 flex flex-col gap-2 sm:flex-row sm:justify-end">
              <button
                type="button"
                onClick={closeCancelDialog}
                disabled={runningAction !== null}
                className="rounded-xl border border-slate-700 px-4 py-2 text-sm font-semibold text-slate-200"
              >
                Mantener torneo
              </button>
              <button
                type="submit"
                disabled={runningAction !== null || !canConfirmCancel}
                className="rounded-xl bg-red-600 px-4 py-2 text-sm font-semibold text-white disabled:bg-red-900/60"
              >
                {runningAction === 'Cancelar torneo' ? 'Cancelando...' : 'Confirmar cancelacion'}
              </button>
            </div>
          </form>
        </div>
      ) : null}
    </section>
  )
}
