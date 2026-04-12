import { DQ_REASONS } from '../../constants/tarjeta'
import type { TarjetaSeleccionada } from '../../hooks/usePerformanceFlow'
import { MotivoDqSelector } from './MotivoDqSelector'

interface StepRevisionProps {
  nombreAtleta: string
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
  nombreAtleta,
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
      <span className="inline-block rounded-full bg-amber-400/20 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-amber-200">
        EN REVISIÓN
      </span>
      <p className="text-xl font-semibold text-white">{nombreAtleta}</p>

      <div className="grid grid-cols-2 gap-3">
        {(['Blanca', 'Roja'] as const).map((card) => {
          const isSelected = selectedCard === card
          const colorClasses =
            card === 'Blanca'
              ? isSelected
                ? 'border-white bg-white ring-4 ring-white/50'
                : 'border-white bg-white opacity-60'
              : isSelected
                ? 'border-red-500 bg-red-500 ring-4 ring-red-400/50'
                : 'border-red-500 bg-red-500 opacity-60'
          return (
            <button
              key={card}
              type="button"
              aria-label={`Resolver como ${card}`}
              onClick={() => {
                onSelectCard(card)
                if (card === 'Blanca') onMotivoDqChange('')
              }}
              className={`h-40 w-full rounded-2xl border transition ${colorClasses}`}
            />
          )
        })}
      </div>

      {selectedCard === 'Roja' ? (
        <MotivoDqSelector value={motivoDq} options={DQ_REASONS} onChange={onMotivoDqChange} />
      ) : null}

      <div className="grid grid-cols-2 gap-3">
        <button
          type="button"
          onClick={onVolver}
          className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-100"
        >
          VOLVER
        </button>
        <button
          type="button"
          disabled={!selectedCard || !canSubmitRedCard || isPending}
          onClick={onConfirm}
          className="w-full rounded-2xl bg-amber-300 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950 disabled:opacity-50"
        >
          CONFIRMAR
        </button>
      </div>
    </section>
  )
}
