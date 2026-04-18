import type { PenalizacionPayload } from '../../api/competencia'
import { DQ_REASONS } from '../../constants/tarjeta'
import type { TarjetaSeleccionada } from '../../hooks/usePerformanceFlow'
import { MotivoDqSelector } from './MotivoDqSelector'
import { PenalizacionesSelector } from './PenalizacionesSelector'

interface PenalizacionesConfig {
  items: PenalizacionPayload[]
  disciplina: string
  admite: boolean
  onChange: (next: PenalizacionPayload[]) => void
}

interface StepTarjetaProps {
  selectedCard: TarjetaSeleccionada
  motivoDq: string
  canSubmitRedCard: boolean
  isPending: boolean
  penalizaciones: PenalizacionesConfig
  onSelectCard: (card: TarjetaSeleccionada) => void
  onMotivoDqChange: (value: string) => void
  onConfirm: () => void
}

export function StepTarjeta({
  selectedCard,
  motivoDq,
  canSubmitRedCard,
  isPending,
  penalizaciones,
  onSelectCard,
  onMotivoDqChange,
  onConfirm,
}: StepTarjetaProps) {
  function handleCardClick(card: 'Blanca' | 'Roja' | 'Amarilla') {
    onSelectCard(card)
    if (card === 'Blanca' || card === 'Amarilla') {
      onMotivoDqChange('')
    }
    if (card === 'Amarilla') {
      penalizaciones.onChange([])
    }
  }

  const confirmDisabled =
    !selectedCard ||
    !canSubmitRedCard ||
    (selectedCard === 'BlancaConPenalizaciones' &&
      (!penalizaciones.admite || penalizaciones.items.length === 0)) ||
    isPending

  return (
    <section className="space-y-4 rounded-[2rem] border border-slate-800 bg-slate-900/80 p-5">
      <h3 className="text-xl font-semibold text-white">Paso 6 · Tarjeta</h3>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        {(['Blanca', 'Roja', 'Amarilla'] as const).map((card) => {
          const isSelected =
            selectedCard === card ||
            (card === 'Blanca' && selectedCard === 'BlancaConPenalizaciones')
          const colorClasses =
            card === 'Blanca'
              ? isSelected
                ? 'border-white bg-white ring-4 ring-white/50'
                : 'border-white bg-white opacity-60'
              : card === 'Roja'
                ? isSelected
                  ? 'border-red-500 bg-red-500 ring-4 ring-red-400/50'
                  : 'border-red-500 bg-red-500 opacity-60'
                : isSelected
                  ? 'border-amber-400 bg-amber-400 ring-4 ring-amber-300/50'
                  : 'border-amber-400 bg-amber-400 opacity-60'
          return (
            <button
              key={card}
              type="button"
              aria-label={`Tarjeta ${card}`}
              onClick={() => handleCardClick(card)}
              className={`h-40 rounded-2xl border transition ${colorClasses}`}
            />
          )
        })}
      </div>

      {selectedCard === 'Roja' ? (
        <MotivoDqSelector value={motivoDq} options={DQ_REASONS} onChange={onMotivoDqChange} />
      ) : null}

      {selectedCard === 'Blanca' || selectedCard === 'BlancaConPenalizaciones' ? (
        <PenalizacionesSelector
          disciplina={penalizaciones.disciplina}
          penalizaciones={penalizaciones.items}
          onChange={(next) => {
            penalizaciones.onChange(next)
            onSelectCard(next.length > 0 ? 'BlancaConPenalizaciones' : 'Blanca')
          }}
        />
      ) : null}

      <button
        type="button"
        disabled={confirmDisabled}
        onClick={onConfirm}
        className="w-full rounded-2xl bg-cyan-400 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950 disabled:opacity-50"
      >
        CONFIRMAR TARJETA
      </button>
    </section>
  )
}
