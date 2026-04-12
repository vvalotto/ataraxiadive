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
  distanciaBlackout: string
  needsBlackoutDistance: boolean
  canSubmitRedCard: boolean
  isPending: boolean
  penalizaciones: PenalizacionesConfig
  onSelectCard: (card: TarjetaSeleccionada) => void
  onMotivoDqChange: (value: string) => void
  onDistanciaChange: (value: string) => void
  onConfirm: () => void
}

export function StepTarjeta({
  selectedCard,
  motivoDq,
  distanciaBlackout,
  needsBlackoutDistance,
  canSubmitRedCard,
  isPending,
  penalizaciones,
  onSelectCard,
  onMotivoDqChange,
  onDistanciaChange,
  onConfirm,
}: StepTarjetaProps) {
  function handleCardClick(card: 'Blanca' | 'Roja' | 'Amarilla') {
    onSelectCard(card)
    if (card === 'Blanca' || card === 'Amarilla') {
      onMotivoDqChange('')
      onDistanciaChange('')
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
                ? 'border-white bg-white/20 ring-2 ring-white/40'
                : 'border-white/30 bg-white/5'
              : card === 'Roja'
                ? isSelected
                  ? 'border-red-300 bg-red-500/25 ring-2 ring-red-300/40'
                  : 'border-red-300/40 bg-red-500/8'
                : isSelected
                  ? 'border-amber-300 bg-amber-400/25 ring-2 ring-amber-300/40'
                  : 'border-amber-300/40 bg-amber-400/8'
          return (
            <button
              key={card}
              type="button"
              aria-label={`Tarjeta ${card}`}
              onClick={() => handleCardClick(card)}
              className={`h-20 rounded-2xl border transition ${colorClasses}`}
            />
          )
        })}
      </div>

      {selectedCard === 'Roja' ? (
        <>
          <MotivoDqSelector value={motivoDq} options={DQ_REASONS} onChange={onMotivoDqChange} />
          {needsBlackoutDistance ? (
            <input
              value={distanciaBlackout}
              onChange={(event) => onDistanciaChange(event.target.value)}
              placeholder="Distancia blackout"
              className="w-full rounded-2xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-white"
            />
          ) : null}
        </>
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
