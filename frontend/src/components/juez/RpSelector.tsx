interface RpSelectorProps {
  metros: number
  centimetros: string
  onMetrosChange: (value: number) => void
  onCentimetrosChange: (value: string) => void
}

const presets = [25, 50, 75, 100, 125]
const keypad = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

export function RpSelector({
  metros,
  centimetros,
  onMetrosChange,
  onCentimetrosChange,
}: RpSelectorProps) {
  function pushDigit(digit: string) {
    const next = `${centimetros}${digit}`.slice(-2)
    onCentimetrosChange(next)
  }

  return (
    <section className="space-y-5 rounded-[2rem] border border-slate-800 bg-slate-900/80 p-5">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Marca</p>
        <p className="mt-2 text-4xl font-semibold text-white">
          {metros}
          <span className="text-slate-500">.</span>
          {centimetros.padEnd(2, '0')} m
        </p>
      </div>

      <div className="grid grid-cols-5 gap-2">
        {presets.map((preset) => (
          <button
            key={preset}
            type="button"
            onClick={() => onMetrosChange(preset)}
            className={[
              'rounded-2xl border px-3 py-3 text-sm font-semibold transition',
              metros === preset
                ? 'border-cyan-300 bg-cyan-400/20 text-cyan-100'
                : 'border-slate-700 bg-slate-950/70 text-slate-200',
            ].join(' ')}
          >
            {preset}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-4 gap-2 text-sm font-semibold">
        {[
          ['-1', -1],
          ['+1', 1],
          ['+5', 5],
          ['+10', 10],
        ].map(([label, delta]) => (
          <button
            key={label}
            type="button"
            onClick={() => onMetrosChange(Math.max(0, metros + Number(delta)))}
            className="rounded-2xl border border-slate-700 bg-slate-950/70 px-3 py-3 text-slate-100"
          >
            {label}
          </button>
        ))}
      </div>

      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
          Centimetros
        </p>
        <div className="mt-3 grid grid-cols-3 gap-2">
          {keypad.slice(0, 9).map((digit) => (
            <button
              key={digit}
              type="button"
              onClick={() => pushDigit(digit)}
              className="rounded-2xl border border-slate-700 bg-slate-950/70 px-3 py-4 text-lg font-semibold text-white"
            >
              {digit}
            </button>
          ))}
          <button
            type="button"
            onClick={() => onCentimetrosChange('')}
            className="rounded-2xl border border-slate-700 bg-slate-950/70 px-3 py-4 text-sm font-semibold text-slate-200"
          >
            CLR
          </button>
          <button
            type="button"
            onClick={() => pushDigit('0')}
            className="rounded-2xl border border-slate-700 bg-slate-950/70 px-3 py-4 text-lg font-semibold text-white"
          >
            0
          </button>
          <button
            type="button"
            onClick={() => onCentimetrosChange(centimetros.slice(0, -1))}
            className="rounded-2xl border border-slate-700 bg-slate-950/70 px-3 py-4 text-sm font-semibold text-slate-200"
          >
            DEL
          </button>
        </div>
      </div>
    </section>
  )
}
