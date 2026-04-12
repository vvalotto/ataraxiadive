import { BKO_REASONS } from '../../constants/tarjeta'
import { MotivoDqSelector } from './MotivoDqSelector'
import { RpSelector } from './RpSelector'

interface StepBKOProps {
  isSTA: boolean
  metros: number
  centimetros: string
  unidad: string
  distanciaBlackout: string
  motivoDq: string
  canSubmitBko: boolean
  isPending: boolean
  onMetrosChange: (value: number) => void
  onCentimetrosChange: (value: string) => void
  onDistanciaChange: (value: string) => void
  onMotivoDqChange: (value: string) => void
  onConfirm: () => void
  onCancel: () => void
}

export function StepBKO({
  isSTA,
  metros,
  centimetros,
  unidad,
  distanciaBlackout,
  motivoDq,
  canSubmitBko,
  isPending,
  onMetrosChange,
  onCentimetrosChange,
  onDistanciaChange,
  onMotivoDqChange,
  onConfirm,
  onCancel,
}: StepBKOProps) {
  return (
    <section className="space-y-4 rounded-[2rem] border border-red-300/20 bg-red-500/8 p-5">
      <h3 className="text-xl font-semibold text-white">BKO</h3>
      <p className="text-sm text-slate-300">
        Registra la distancia alcanzada y el motivo de descalificación.
      </p>
      {!isSTA ? (
        <>
          <RpSelector
            metros={metros}
            centimetros={centimetros}
            unidad={unidad}
            onMetrosChange={onMetrosChange}
            onCentimetrosChange={onCentimetrosChange}
          />
          <input
            value={distanciaBlackout}
            onChange={(event) => onDistanciaChange(event.target.value)}
            placeholder="Distancia blackout"
            className="w-full rounded-2xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-white"
          />
        </>
      ) : null}
      <MotivoDqSelector value={motivoDq} options={BKO_REASONS} onChange={onMotivoDqChange} />
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <button
          type="button"
          onClick={onCancel}
          className="w-full rounded-2xl border border-slate-700 bg-slate-900 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-100"
        >
          CANCELAR
        </button>
        <button
          type="button"
          disabled={!canSubmitBko || isPending}
          onClick={onConfirm}
          className="w-full rounded-2xl bg-red-300 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950 disabled:opacity-50"
        >
          CONFIRMAR BKO — TARJETA ROJA
        </button>
      </div>
    </section>
  )
}
