import { useMemo, useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import {
  ApiError,
  asignarTarjeta,
  llamarAtleta,
  registrarDns,
  registrarResultado,
  resolverRevision,
  type PenalizacionPayload,
} from '../../api/competencia'
import { AtletaCard } from '../../components/juez/AtletaCard'
import { JuezLayout } from '../../components/juez/JuezLayout'
import { MotivoDqSelector } from '../../components/juez/MotivoDqSelector'
import { PenalizacionesSelector } from '../../components/juez/PenalizacionesSelector'
import { RpSelector } from '../../components/juez/RpSelector'
import { StepIndicator } from '../../components/juez/StepIndicator'
import useCompetenciaStore from '../../stores/useCompetenciaStore'

const dqReasons = [
  'BKO_SUPERFICIE',
  'BKO_SUBACUATICO',
  'PROTOCOLO_SUPERFICIE',
  'INFRACCION_TECNICA_DQ',
  'NO_INICIO_EN_VENTANA',
  'SALIDA_EN_FALSO',
] as const

const bkoReasons = ['BKO_SUPERFICIE', 'BKO_SUBACUATICO'] as const
const penaltyTypes = [
  'SIN_CONTACTO_PARED',
  'FUERA_DE_CARRIL',
  'ASISTENTE_EN_ZONA',
  'PATADA_DELFIN_BIALETAS',
] as const

type TarjetaSeleccionada = 'Blanca' | 'Roja' | 'BlancaConPenalizaciones' | 'Amarilla' | null
type ResultadoFinal =
  | 'BLANCA'
  | 'BLANCA_CON_PENALIZACIONES'
  | 'ROJA'
  | 'AMARILLA'
  | 'DNS'
  | null

function buildRpValue(metros: number, centimetros: string) {
  return `${metros}.${centimetros.padEnd(2, '0')}`
}

function buildResultadoValue(metros: number, centimetros: string, unidad: string) {
  if (unidad === 'Segundos') {
    return String(metros * 60 + Number(centimetros || '0'))
  }
  return buildRpValue(metros, centimetros)
}

function formatMarca(value: string, unidad: string) {
  if (unidad === 'Segundos') {
    const totalSeconds = Number(value || '0')
    const minutos = Math.floor(totalSeconds / 60)
    const segundos = totalSeconds % 60
    return `${minutos}:${String(segundos).padStart(2, '0')} min`
  }
  return `${value} m`
}

function admitePenalizaciones(disciplina: string) {
  return disciplina === 'DNF' || disciplina === 'DYN' || disciplina === 'DBF'
}

function buildPenalizaciones(count: number): PenalizacionPayload[] {
  return Array.from({ length: count }, (_, index) => ({
    tipo: penaltyTypes[index % penaltyTypes.length],
    deduccion: '3',
  }))
}

export function PerformanceFlowPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const competenciaId = useCompetenciaStore((s) => s.competenciaId)
  const disciplinaActiva = useCompetenciaStore((s) => s.disciplinaActiva)
  const atletaActivo = useCompetenciaStore((s) => s.atletaActivo)
  const seleccionarAtleta = useCompetenciaStore((s) => s.seleccionarAtleta)
  const limpiarAtleta = useCompetenciaStore((s) => s.limpiarAtleta)

  const [step, setStep] = useState(() => {
    const estado = atletaActivo?.estado
    if (estado === 'Llamada') return 2
    if (estado === 'ResultadoRegistrado') return 6
    if (estado === 'EnRevision') return 7
    return 1
  })
  const [inlineError, setInlineError] = useState<string | null>(null)
  const [metros, setMetros] = useState(0)
  const [centimetros, setCentimetros] = useState('')
  const [otWindowActive, setOtWindowActive] = useState(false)
  const [chronoStarted, setChronoStarted] = useState(false)
  const [selectedCard, setSelectedCard] = useState<TarjetaSeleccionada>(null)
  const [motivoDq, setMotivoDq] = useState('')
  const [distanciaBlackout, setDistanciaBlackout] = useState('')
  const [penaltyCount, setPenaltyCount] = useState(0)
  const [isBkoMode, setIsBkoMode] = useState(false)
  const [completed, setCompleted] = useState(false)
  const [resultKind, setResultKind] = useState<ResultadoFinal>(null)

  const rpConfirmDisabled = metros === 0 && centimetros.length === 0
  const needsBlackoutDistance = motivoDq === 'BKO_SUPERFICIE' || motivoDq === 'BKO_SUBACUATICO'
  const isSTA = atletaActivo?.unidad === 'Segundos'
  const disciplinaPermitePenalizaciones = disciplinaActiva
    ? admitePenalizaciones(disciplinaActiva)
    : false

  const refreshCompetencia = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['grilla', competenciaId, disciplinaActiva] }),
      queryClient.invalidateQueries({ queryKey: ['performance-actual', competenciaId] }),
    ])
  }

  const finalizeResult = async (
    kind: ResultadoFinal,
    nextState: 'Ejecutada' | 'DNS' | 'EnRevision',
  ) => {
    setInlineError(null)
    await refreshCompetencia()
    seleccionarAtleta({ ...atletaActivo!, estado: nextState })
    setResultKind(kind)
    setCompleted(nextState !== 'EnRevision')
  }

  const llamarMutation = useMutation({
    mutationFn: async () => {
      await llamarAtleta({
        competenciaId: competenciaId!,
        participanteId: atletaActivo!.atletaId,
        disciplina: disciplinaActiva!,
        otProgramado: atletaActivo!.otProgramado,
        posicionGrilla: atletaActivo!.posicion,
        andarivel: atletaActivo!.andarivel,
      })
    },
    onSuccess: async () => {
      setInlineError(null)
      await refreshCompetencia()
      seleccionarAtleta({ ...atletaActivo!, estado: 'Llamada' })
      setStep(2)
    },
    onError: (error) => {
      setInlineError(
        error instanceof ApiError && error.status === 409
          ? 'No se puede ejecutar esta accion en el estado actual'
          : 'No se pudo llamar al atleta',
      )
    },
  })

  const dnsMutation = useMutation({
    mutationFn: async () => {
      await registrarDns({
        competenciaId: competenciaId!,
        participanteId: atletaActivo!.atletaId,
        disciplina: disciplinaActiva!,
      })
    },
    onSuccess: async () => {
      await finalizeResult('DNS', 'DNS')
    },
    onError: (error) => {
      setInlineError(error instanceof Error ? error.message : 'No se pudo registrar DNS')
    },
  })

  const resultadoMutation = useMutation({
    mutationFn: async () => {
      await registrarResultado({
        competenciaId: competenciaId!,
        participanteId: atletaActivo!.atletaId,
        disciplina: disciplinaActiva!,
        valorRp: buildResultadoValue(metros, centimetros, atletaActivo!.unidad || 'Metros'),
        unidad: atletaActivo!.unidad || 'Metros',
      })
    },
    onSuccess: async () => {
      setInlineError(null)
      await refreshCompetencia()
      seleccionarAtleta({ ...atletaActivo!, estado: 'ResultadoRegistrado' })
      setStep(6)
    },
    onError: (error) => {
      setInlineError(error instanceof Error ? error.message : 'No se pudo registrar la marca')
    },
  })

  const tarjetaMutation = useMutation({
    mutationFn: async () => {
      const penalizaciones =
        selectedCard === 'BlancaConPenalizaciones' ? buildPenalizaciones(penaltyCount) : []
      await asignarTarjeta({
        competenciaId: competenciaId!,
        participanteId: atletaActivo!.atletaId,
        disciplina: disciplinaActiva!,
        tarjeta: selectedCard!,
        motivoTexto: selectedCard === 'Amarilla' ? 'Revision pendiente del juez' : undefined,
        motivoDq: selectedCard === 'Roja' ? motivoDq : undefined,
        distanciaBlackout:
          selectedCard === 'Roja' && needsBlackoutDistance ? distanciaBlackout : undefined,
        penalizaciones,
      })
    },
    onSuccess: async () => {
      if (selectedCard === 'Amarilla') {
        await finalizeResult('AMARILLA', 'EnRevision')
        setStep(7)
        return
      }
      const kind =
        selectedCard === 'Roja'
          ? 'ROJA'
          : selectedCard === 'BlancaConPenalizaciones'
            ? 'BLANCA_CON_PENALIZACIONES'
            : 'BLANCA'
      await finalizeResult(kind, 'Ejecutada')
    },
    onError: (error) => {
      setInlineError(error instanceof Error ? error.message : 'No se pudo asignar la tarjeta')
    },
  })

  const resolverRevisionMutation = useMutation({
    mutationFn: async () => {
      await resolverRevision({
        competenciaId: competenciaId!,
        participanteId: atletaActivo!.atletaId,
        disciplina: disciplinaActiva!,
        resolucion: selectedCard === 'Roja' ? 'Roja' : 'Blanca',
        motivoDq: selectedCard === 'Roja' ? motivoDq : undefined,
      })
    },
    onSuccess: async () => {
      const kind = selectedCard === 'Roja' ? 'ROJA' : 'BLANCA'
      await finalizeResult(kind, 'Ejecutada')
    },
    onError: (error) => {
      setInlineError(error instanceof Error ? error.message : 'No se pudo resolver la revision')
    },
  })

  const bkoMutation = useMutation({
    mutationFn: async () => {
      const valorRp = isSTA ? '0' : buildRpValue(metros, centimetros)
      await registrarResultado({
        competenciaId: competenciaId!,
        participanteId: atletaActivo!.atletaId,
        disciplina: disciplinaActiva!,
        valorRp,
        unidad: atletaActivo!.unidad || 'Metros',
      })
      await asignarTarjeta({
        competenciaId: competenciaId!,
        participanteId: atletaActivo!.atletaId,
        disciplina: disciplinaActiva!,
        tarjeta: 'Roja',
        motivoDq,
        distanciaBlackout: isSTA ? undefined : distanciaBlackout,
      })
    },
    onSuccess: async () => {
      await finalizeResult('ROJA', 'Ejecutada')
    },
    onError: (error) => {
      setInlineError(error instanceof Error ? error.message : 'No se pudo registrar BKO')
    },
  })

  const canSubmitRedCard = useMemo(() => {
    if (selectedCard !== 'Roja') {
      return true
    }
    if (!motivoDq) {
      return false
    }
    if (needsBlackoutDistance && !distanciaBlackout.trim()) {
      return false
    }
    return true
  }, [selectedCard, motivoDq, needsBlackoutDistance, distanciaBlackout])

  const canSubmitBko = isSTA
    ? motivoDq.length > 0
    : !rpConfirmDisabled && motivoDq.length > 0 && !needsBlackoutDistance
      ? true
      : !rpConfirmDisabled && motivoDq.length > 0 && distanciaBlackout.trim().length > 0

  const completionTitle = useMemo(() => {
    if (resultKind === 'DNS') {
      return 'DNS REGISTRADO'
    }
    if (resultKind === 'AMARILLA') {
      return 'TARJETA AMARILLA'
    }
    if (resultKind === 'ROJA') {
      return 'TARJETA ROJA'
    }
    if (resultKind === 'BLANCA_CON_PENALIZACIONES') {
      return 'TARJETA BLANCA CON PENALIZACIONES'
    }
    return 'TARJETA BLANCA'
  }, [resultKind])

  const completionSubtitle = useMemo(() => {
    if (resultKind === 'DNS') {
      return 'No se presentó'
    }
    if (resultKind === 'AMARILLA') {
      return 'La performance queda en revision hasta definir tarjeta final'
    }
    const marca = formatMarca(
      buildResultadoValue(metros, centimetros, atletaActivo?.unidad ?? 'Metros'),
      atletaActivo?.unidad ?? 'Metros',
    )
    if (resultKind === 'BLANCA_CON_PENALIZACIONES') {
      return `${marca} · ${penaltyCount} penalizaciones`
    }
    return marca
  }, [resultKind, metros, centimetros, atletaActivo?.unidad, penaltyCount])

  if (!competenciaId || !disciplinaActiva || !atletaActivo) {
    return <Navigate to="/juez/grilla" replace />
  }

  return (
    <JuezLayout
      title={disciplinaActiva}
      actions={
        <Link
          to="/juez/grilla"
          className="rounded-full border border-slate-700 px-3 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate-200"
        >
          Volver
        </Link>
      }
    >
      <section className="rounded-[2rem] border border-slate-800 bg-slate-950/60 p-4">
        <StepIndicator currentStep={completed ? 6 : step} />
      </section>

      <AtletaCard
        nombreAtleta={atletaActivo.nombreAtleta}
        apDeclarado={atletaActivo.apDeclarado}
        unidad={atletaActivo.unidad}
        andarivel={atletaActivo.andarivel}
        otProgramado={atletaActivo.otProgramado}
        estado={completed ? 'COMPLETADA' : atletaActivo.estado}
      />

      {inlineError ? (
        <section className="rounded-3xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-100">
          {inlineError}
        </section>
      ) : null}

      {!completed && step === 1 ? (
        <section className="space-y-4 rounded-[2rem] border border-slate-800 bg-slate-900/80 p-5">
          <h3 className="text-xl font-semibold text-white">Paso 1 · Llamada</h3>
          <p className="text-sm text-slate-300">
            Confirma la llamada del atleta para habilitar la performance.
          </p>
          <button
            type="button"
            onClick={() => llamarMutation.mutate()}
            disabled={llamarMutation.isPending}
            className="w-full rounded-2xl bg-cyan-400 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950 disabled:opacity-60"
          >
            LLAMAR ATLETA
          </button>
        </section>
      ) : null}

      {!completed && step === 2 ? (
        <section className="space-y-4 rounded-[2rem] border border-slate-800 bg-slate-900/80 p-5">
          <h3 className="text-xl font-semibold text-white">Paso 2 · Confirmar presencia</h3>
          <p className="text-sm text-slate-300">
            Confirmado que el atleta está en cámara y listo para iniciar.
          </p>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <button
              type="button"
              onClick={() => {
                setOtWindowActive(false)
                setStep(3)
              }}
              className="w-full rounded-2xl bg-emerald-400 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950"
            >
              CONTINUAR
            </button>
            <button
              type="button"
              onClick={() => dnsMutation.mutate()}
              disabled={dnsMutation.isPending}
              className="w-full rounded-2xl border border-red-300/30 bg-red-500/10 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-red-100 disabled:opacity-60"
            >
              DNS — NO SE PRESENTA
            </button>
          </div>
        </section>
      ) : null}

      {!completed && step === 3 ? (
        <section className="space-y-4 rounded-[2rem] border border-slate-800 bg-slate-900/80 p-5">
          <h3 className="text-xl font-semibold text-white">Paso 3 · OT</h3>
          <p className="text-sm text-slate-300">
            OT programado:{' '}
            {new Date(atletaActivo.otProgramado).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </p>
          {!otWindowActive ? (
            <button
              type="button"
              onClick={() => setOtWindowActive(true)}
              className="w-full rounded-2xl bg-amber-300 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950"
            >
              INICIAR VENTANA OT
            </button>
          ) : (
            <>
              <div className="rounded-3xl border border-cyan-400/20 bg-cyan-400/10 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-200">
                  Ventana OT activa
                </p>
                <p className="mt-2 text-sm text-slate-100">
                  {isSTA
                    ? 'Las vias respiratorias del atleta entran en contacto con el agua.'
                    : 'El atleta comienza su performance dentro de la ventana oficial.'}
                </p>
              </div>
              <button
                type="button"
                onClick={() => {
                  setChronoStarted(true)
                  setStep(4)
                }}
                className="w-full rounded-2xl bg-emerald-400 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950"
              >
                {isSTA ? 'VIAS RESPIRATORIAS EN AGUA' : 'ATLETA INICIA'}
              </button>
            </>
          )}
        </section>
      ) : null}

      {!completed && step === 4 && !isBkoMode ? (
        <section className="space-y-4 rounded-[2rem] border border-slate-800 bg-slate-900/80 p-5">
          <h3 className="text-xl font-semibold text-white">Paso 4 · Performance</h3>
          <p className="text-sm text-slate-300">
            {chronoStarted
              ? 'La performance esta en curso. Finaliza cuando el atleta complete su intento.'
              : 'La performance ya fue iniciada desde la ventana OT.'}
          </p>
          <button
            type="button"
            onClick={() => setStep(5)}
            className="w-full rounded-2xl bg-orange-300 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950"
          >
            FINALIZAR PERFORMANCE
          </button>
          <button
            type="button"
            onClick={() => {
              setIsBkoMode(true)
              setSelectedCard('Roja')
              setMotivoDq('BKO_SUBACUATICO')
            }}
            className="w-full rounded-2xl border border-red-300/30 bg-red-500/10 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-red-100"
          >
            BKO — BLACK-OUT
          </button>
        </section>
      ) : null}

      {!completed && step === 4 && isBkoMode ? (
        <section className="space-y-4 rounded-[2rem] border border-red-300/20 bg-red-500/8 p-5">
          <h3 className="text-xl font-semibold text-white">BKO</h3>
          <p className="text-sm text-slate-300">
            Registra la distancia alcanzada y el motivo de descalificación.
          </p>
          {!isSTA ? (
            <>
              <RpSelector
                metros={metros}
                centimetros={centimetros}
                unidad={atletaActivo.unidad}
                onMetrosChange={setMetros}
                onCentimetrosChange={setCentimetros}
              />
              <input
                value={distanciaBlackout}
                onChange={(event) => setDistanciaBlackout(event.target.value)}
                placeholder="Distancia blackout"
                className="w-full rounded-2xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-white"
              />
            </>
          ) : null}
          <MotivoDqSelector value={motivoDq} options={bkoReasons} onChange={setMotivoDq} />
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <button
              type="button"
              onClick={() => {
                setIsBkoMode(false)
                setMotivoDq('')
                setDistanciaBlackout('')
              }}
              className="w-full rounded-2xl border border-slate-700 bg-slate-900 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-100"
            >
              CANCELAR
            </button>
            <button
              type="button"
              disabled={!canSubmitBko || bkoMutation.isPending}
              onClick={() => bkoMutation.mutate()}
              className="w-full rounded-2xl bg-red-300 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950 disabled:opacity-50"
            >
              CONFIRMAR BKO — TARJETA ROJA
            </button>
          </div>
        </section>
      ) : null}

      {!completed && step === 5 ? (
        <section className="space-y-4">
          <RpSelector
            metros={metros}
            centimetros={centimetros}
            unidad={atletaActivo.unidad}
            onMetrosChange={setMetros}
            onCentimetrosChange={setCentimetros}
          />
          <button
            type="button"
            disabled={rpConfirmDisabled || resultadoMutation.isPending}
            onClick={() => resultadoMutation.mutate()}
            className="w-full rounded-2xl bg-white px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950 disabled:opacity-50"
          >
            CONFIRMAR MARCA
          </button>
        </section>
      ) : null}

      {!completed && step === 6 ? (
        <section className="space-y-4 rounded-[2rem] border border-slate-800 bg-slate-900/80 p-5">
          <h3 className="text-xl font-semibold text-white">Paso 6 · Tarjeta</h3>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            {(['Blanca', 'Roja', 'Amarilla'] as const).map((card) => (
              <button
                key={card}
                type="button"
                aria-label={`Tarjeta ${card}`}
                onClick={() => {
                  setSelectedCard(card)
                  if (card === 'Blanca') {
                    setMotivoDq('')
                    setDistanciaBlackout('')
                  }
                  if (card === 'Amarilla') {
                    setMotivoDq('')
                    setDistanciaBlackout('')
                    setPenaltyCount(0)
                  }
                }}
                className={[
                  'h-20 rounded-2xl border transition',
                  (selectedCard === card ||
                    (card === 'Blanca' && selectedCard === 'BlancaConPenalizaciones'))
                    ? card === 'Blanca'
                      ? 'border-emerald-300 bg-emerald-400/15 text-emerald-100'
                      : card === 'Roja'
                        ? 'border-red-300 bg-red-400/15 text-red-100'
                        : 'border-amber-300 bg-amber-400/15 text-amber-100'
                    : 'border-slate-700 bg-slate-950/70 text-slate-200',
                ].join(' ')}
              />
            ))}
          </div>

          {selectedCard === 'Roja' ? (
            <>
              <MotivoDqSelector value={motivoDq} options={dqReasons} onChange={setMotivoDq} />
              {needsBlackoutDistance ? (
                <input
                  value={distanciaBlackout}
                  onChange={(event) => setDistanciaBlackout(event.target.value)}
                  placeholder="Distancia blackout"
                  className="w-full rounded-2xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-white"
                />
              ) : null}
            </>
          ) : null}

          {(selectedCard === 'Blanca' || selectedCard === 'BlancaConPenalizaciones') ? (
            <PenalizacionesSelector
              disciplina={disciplinaActiva}
              count={penaltyCount}
              onChange={(next) => {
                setPenaltyCount(next)
                setSelectedCard(next > 0 ? 'BlancaConPenalizaciones' : 'Blanca')
              }}
            />
          ) : null}

          <button
            type="button"
            disabled={
              !selectedCard ||
              !canSubmitRedCard ||
              (selectedCard === 'BlancaConPenalizaciones' &&
                (!disciplinaPermitePenalizaciones || penaltyCount === 0)) ||
              tarjetaMutation.isPending
            }
            onClick={() => tarjetaMutation.mutate()}
            className="w-full rounded-2xl bg-cyan-400 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950 disabled:opacity-50"
          >
            CONFIRMAR TARJETA
          </button>
        </section>
      ) : null}

      {!completed && step === 7 ? (
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
                setSelectedCard('Blanca')
                setMotivoDq('')
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
              onClick={() => setSelectedCard('Roja')}
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
            <MotivoDqSelector value={motivoDq} options={dqReasons} onChange={setMotivoDq} />
          ) : null}
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <button
              type="button"
              onClick={() => {
                limpiarAtleta()
                void navigate('/juez/grilla')
              }}
              className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-100"
            >
              Volver a la grilla
            </button>
            <button
              type="button"
              disabled={!selectedCard || !canSubmitRedCard || resolverRevisionMutation.isPending}
              onClick={() => resolverRevisionMutation.mutate()}
              className="w-full rounded-2xl bg-amber-300 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950 disabled:opacity-50"
            >
              Confirmar resolucion
            </button>
          </div>
        </section>
      ) : null}

      {completed ? (
        <section className="space-y-4 rounded-[2rem] border border-emerald-300/30 bg-emerald-400/10 p-5">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-300">
            {resultKind === 'DNS' ? 'DNS registrado' : 'Performance completada'}
          </p>
          <h3 className="text-2xl font-semibold text-white">{completionTitle}</h3>
          <p className="text-sm text-slate-200">{completionSubtitle}</p>
          <button
            type="button"
            onClick={() => {
              limpiarAtleta()
              void navigate('/juez/grilla')
            }}
            className="w-full rounded-2xl bg-white px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950"
          >
            SIGUIENTE ATLETA
          </button>
        </section>
      ) : null}
    </JuezLayout>
  )
}
