import { DQ_REASONS } from '../../constants/tarjeta'
import type { TarjetaSeleccionada } from '../../hooks/usePerformanceFlow'
import { MotivoDqSelector } from './MotivoDqSelector'

interface StepRevisionProps {
  selectedCard: TarjetaSeleccionada
  motivoDq: string
  canSubmitRedCard: boolean
  isPending: boolean
  onSelectCard: (card: TarjetaSeleccionada) => void
  onMotivoDqChange: (value: string) => void
  onConfirm: () => void
  onVolver: () => void
}

export function StepRevision({
  selectedCard,
  motivoDq,
  canSubmitRedCard,
  isPending,
  onSelectCard,
  onMotivoDqChange,
  onConfirm,
  onVolver,
}: StepRevisionProps) {
  return (
    <section className="space-y-4 rounded-[2rem] border border-amber-300/30 bg-amber-400/10 p-5">
      <p className="text-xs font-semibold uppercase tracking-[0.24em] text-amber-200">
        Revision pendiente
      </p>
      <h3 className="text-2xl font-semibold text-white">TARJETA AMARILLA</h3>
      <p className="text-sm text-slate-200">
        La performance quedo en revision. Podes resolverla ahora o volver a la grilla.
      </p>
      <div className="rounded-2xl border border-amber-300/20 bg-slate-950/40 p-4 text-sm text-slate-200">
        Timer informativo: hasta 3 minutos de deliberacion.
      </div>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <button
          type="button"
          onClick={() => {
            onSelectCard('Blanca')
            onMotivoDqChange('')
          }}
          className={[
            'rounded-2xl border px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em]',
            selectedCard === 'Blanca'
              ? 'border-cyan-300 bg-cyan-400/15 text-cyan-100'
              : 'border-slate-700 bg-slate-950/70 text-slate-200',
          ].join(' ')}
        >
          RESOLVER -&gt; BLANCA
        </button>
        <button
          type="button"
          onClick={() => onSelectCard('Roja')}
          className={[
            'rounded-2xl border px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em]',
            selectedCard === 'Roja'
              ? 'border-red-300 bg-red-400/15 text-red-100'
              : 'border-slate-700 bg-slate-950/70 text-slate-200',
          ].join(' ')}
        >
          RESOLVER -&gt; ROJA
        </button>
      </div>
      {selectedCard === 'Roja' ? (
        <MotivoDqSelector value={motivoDq} options={DQ_REASONS} onChange={onMotivoDqChange} />
      ) : null}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <button
          type="button"
          onClick={onVolver}
          className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-100"
        >
          Volver a la grilla
        </button>
        <button
          type="button"
          disabled={!selectedCard || !canSubmitRedCard || isPending}
          onClick={onConfirm}
          className="w-full rounded-2xl bg-amber-300 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950 disabled:opacity-50"
        >
          Confirmar resolucion
        </button>
      </div>
    </section>
  )
}
