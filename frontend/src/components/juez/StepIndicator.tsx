const STEP_NAMES: Record<number, string> = {
  1: 'Llamada',
  2: 'Presencia',
  3: 'OT',
  4: 'Performance',
  5: 'Tarjeta',
  6: 'Marca',
}

interface StepIndicatorProps {
  currentStep: number
  totalSteps?: number
}

export function StepIndicator({ currentStep, totalSteps = 6 }: StepIndicatorProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-center gap-2">
        {Array.from({ length: totalSteps }, (_, index) => {
          const step = index + 1
          const isActive = step === currentStep
          const isComplete = step < currentStep

          return (
            <span
              key={step}
              className={[
                'h-2.5 w-8 rounded-full transition',
                isActive ? 'bg-cyan-400' : '',
                isComplete ? 'bg-emerald-400/80' : '',
                !isActive && !isComplete ? 'bg-slate-700' : '',
              ].join(' ')}
            />
          )
        })}
      </div>
      {STEP_NAMES[currentStep] ? (
        <p className="text-center text-[11px] font-semibold uppercase tracking-[0.18em] text-cyan-400">
          {STEP_NAMES[currentStep]}
        </p>
      ) : null}
    </div>
  )
}
