interface ProgressBarProps {
  completed: number
  total: number
}

export function ProgressBar({ completed, total }: ProgressBarProps) {
  const safeTotal = Math.max(total, 0)
  const safeCompleted = Math.min(Math.max(completed, 0), safeTotal)
  const percent = safeTotal === 0 ? 0 : Math.round((safeCompleted / safeTotal) * 100)

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between gap-3 text-sm">
        <span className="font-semibold text-stone-900">
          {safeCompleted} / {safeTotal}
        </span>
        <span className="text-stone-600">{percent}%</span>
      </div>
      <div className="h-3 overflow-hidden rounded-lg bg-stone-200" aria-hidden="true">
        <div
          className="h-full rounded-lg bg-emerald-700 transition-[width]"
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  )
}
