interface RpSelectorProps {
  metros: number
  centimetros: string
  unidad?: string
  onMetrosChange: (value: number) => void
  onCentimetrosChange: (value: string) => void
}

const keypad = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

export function RpSelector({
  metros,
  centimetros,
  unidad = 'Metros',
  onMetrosChange,
  onCentimetrosChange,
}: RpSelectorProps) {
  const isSecondsMode = unidad === 'Segundos'
  const displayMinor = centimetros.padStart(2, '0')
  const totalSeconds = metros * 60 + Number(centimetros || '0')
  const presets = isSecondsMode ? [120, 180, 240, 300, 360] : [25, 50, 75, 100, 125]
  const adjustments = isSecondsMode
    ? [
        ['-5s', -5],
        ['+5s', 5],
        ['+30s', 30],
        ['+1m', 60],
      ]
    : [
        ['-1', -1],
        ['+1', 1],
        ['+5', 5],
        ['+10', 10],
      ]

  function setTotalSeconds(next: number) {
    const safeValue = Math.max(0, next)
    onMetrosChange(Math.floor(safeValue / 60))
    onCentimetrosChange(String(safeValue % 60))
  }

  function pushDigit(digit: string) {
    const next = `${centimetros}${digit}`.slice(-2)
    if (isSecondsMode) {
      onCentimetrosChange(String(Math.min(59, Number(next))))
      return
    }
    onCentimetrosChange(next)
  }

  return (
    <section className="space-y-3 rounded-[2rem] border border-slate-800 bg-slate-900/80 p-3">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
          {isSecondsMode ? 'Tiempo' : 'Marca'}
        </p>
        <p className="mt-1 text-3xl font-semibold text-white sm:text-4xl">
          {isSecondsMode ? (
            <>
              {metros}
              <span className="text-slate-500">:</span>
              {displayMinor}
              <span className="ml-2 text-lg text-slate-500">min</span>
            </>
          ) : (
            <>
              {metros}
              <span className="text-slate-500">.</span>
              {centimetros.padEnd(2, '0')} m
            </>
          )}
        </p>
      </div>

      <div className="grid grid-cols-5 gap-1">
        {presets.map((preset) => (
          <button
            key={preset}
            type="button"
            onClick={() => {
              if (isSecondsMode) {
                setTotalSeconds(preset)
                return
              }
              onMetrosChange(preset)
            }}
            className={[
              'rounded-xl border px-2 py-2 text-xs font-semibold transition',
              (isSecondsMode ? totalSeconds === preset : metros === preset)
                ? 'border-cyan-300 bg-cyan-400/20 text-cyan-100'
                : 'border-slate-700 bg-slate-950/70 text-slate-200',
            ].join(' ')}
          >
            {isSecondsMode
              ? `${Math.floor(preset / 60)}:${String(preset % 60).padStart(2, '0')}`
              : preset}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-4 gap-1 text-xs font-semibold">
        {adjustments.map(([label, delta]) => (
          <button
            key={label}
            type="button"
            onClick={() => {
              if (isSecondsMode) {
                setTotalSeconds(totalSeconds + Number(delta))
                return
              }
              onMetrosChange(Math.max(0, metros + Number(delta)))
            }}
            className="rounded-xl border border-slate-700 bg-slate-950/70 px-2 py-2 text-slate-100"
          >
            {label}
          </button>
        ))}
      </div>

      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
          {isSecondsMode ? 'Segundos' : 'Centimetros'}
        </p>
        <div className="mt-2 grid grid-cols-3 gap-1">
          {keypad.slice(0, 9).map((digit) => (
            <button
              key={digit}
              type="button"
              onClick={() => pushDigit(digit)}
              className="rounded-xl border border-slate-700 bg-slate-950/70 px-3 py-2.5 text-base font-semibold text-white"
            >
              {digit}
            </button>
          ))}
          <button
            type="button"
            onClick={() => onCentimetrosChange('')}
            className="rounded-xl border border-slate-700 bg-slate-950/70 px-3 py-2.5 text-xs font-semibold text-slate-200"
          >
            CLR
          </button>
          <button
            type="button"
            onClick={() => pushDigit('0')}
            className="rounded-xl border border-slate-700 bg-slate-950/70 px-3 py-2.5 text-base font-semibold text-white"
          >
            0
          </button>
          <button
            type="button"
            onClick={() => onCentimetrosChange(centimetros.slice(0, -1))}
            className="rounded-xl border border-slate-700 bg-slate-950/70 px-3 py-2.5 text-xs font-semibold text-slate-200"
          >
            DEL
          </button>
        </div>
      </div>
    </section>
  )
}
