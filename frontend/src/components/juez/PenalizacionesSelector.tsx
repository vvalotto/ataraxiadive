import type { PenalizacionPayload } from '../../api/competencia'
import { PENALTY_LABELS, PENALTY_TYPES } from '../../constants/tarjeta'
import { admitePenalizaciones } from '../../utils/disciplina'

interface PenalizacionesSelectorProps {
  disciplina: string
  penalizaciones: PenalizacionPayload[]
  onChange: (next: PenalizacionPayload[]) => void
}

export function PenalizacionesSelector({
  disciplina,
  penalizaciones,
  onChange,
}: PenalizacionesSelectorProps) {
  const enabled = admitePenalizaciones(disciplina)

  function countForType(tipo: string) {
    return penalizaciones.filter((p) => p.tipo === tipo).length
  }

  function addType(tipo: string) {
    onChange([...penalizaciones, { tipo, deduccion: '3' }])
  }

  function removeType(tipo: string) {
    const idx = penalizaciones.findLastIndex((p) => p.tipo === tipo)
    if (idx === -1) return
    onChange([...penalizaciones.slice(0, idx), ...penalizaciones.slice(idx + 1)])
  }

  return (
    <div className="space-y-3 rounded-2xl bg-slate-950/70 p-4">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
        Penalizaciones
      </p>
      {!enabled ? (
        <p className="text-sm text-slate-300">{disciplina} no admite penalizaciones</p>
      ) : (
        <>
          {PENALTY_TYPES.map((tipo) => {
            const count = countForType(tipo)
            return (
              <div key={tipo} className="flex items-center justify-between gap-3">
                <p className="flex-1 text-sm text-slate-300">{PENALTY_LABELS[tipo]}</p>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    disabled={count === 0}
                    onClick={() => removeType(tipo)}
                    className="rounded-xl border border-slate-700 bg-slate-900 px-3 py-1.5 text-sm font-semibold text-white disabled:opacity-40"
                  >
                    −
                  </button>
                  <span className="w-5 text-center text-sm font-semibold text-white">{count}</span>
                  <button
                    type="button"
                    onClick={() => addType(tipo)}
                    className="rounded-xl border border-slate-700 bg-slate-900 px-3 py-1.5 text-sm font-semibold text-white"
                  >
                    +
                  </button>
                </div>
              </div>
            )
          })}
          {penalizaciones.length > 0 ? (
            <p className="text-xs text-slate-400">
              {penalizaciones.length} penalización{penalizaciones.length > 1 ? 'es' : ''} ·{' '}
              −{penalizaciones.length * 3}m
            </p>
          ) : null}
        </>
      )}
    </div>
  )
}
