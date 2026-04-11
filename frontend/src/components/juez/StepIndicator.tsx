interface StepIndicatorProps {
  currentStep: number
  totalSteps?: number
}

export function StepIndicator({ currentStep, totalSteps = 6 }: StepIndicatorProps) {
  return (
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
  )
}
