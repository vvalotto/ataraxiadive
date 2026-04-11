import { useMemo, useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import {
  ApiError,
  asignarTarjeta,
  llamarAtleta,
  registrarResultado,
} from '../../api/competencia'
import { AtletaCard } from '../../components/juez/AtletaCard'
import { JuezLayout } from '../../components/juez/JuezLayout'
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

function buildRpValue(metros: number, centimetros: string) {
  return `${metros}.${centimetros.padEnd(2, '0')}`
}

export function PerformanceFlowPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const competenciaId = useCompetenciaStore((s) => s.competenciaId)
  const disciplinaActiva = useCompetenciaStore((s) => s.disciplinaActiva)
  const atletaActivo = useCompetenciaStore((s) => s.atletaActivo)
  const seleccionarAtleta = useCompetenciaStore((s) => s.seleccionarAtleta)
  const limpiarAtleta = useCompetenciaStore((s) => s.limpiarAtleta)

  const [step, setStep] = useState(1)
  const [inlineError, setInlineError] = useState<string | null>(null)
  const [metros, setMetros] = useState(0)
  const [centimetros, setCentimetros] = useState('')
  const [chronoStarted, setChronoStarted] = useState(false)
  const [selectedCard, setSelectedCard] = useState<'Blanca' | 'Roja' | null>(null)
  const [motivoDq, setMotivoDq] = useState<(typeof dqReasons)[number] | ''>('')
  const [distanciaBlackout, setDistanciaBlackout] = useState('')
  const [completed, setCompleted] = useState(false)

  const rpConfirmDisabled = metros === 0 && centimetros.length === 0
  const needsBlackoutDistance = motivoDq === 'BKO_SUPERFICIE' || motivoDq === 'BKO_SUBACUATICO'

  const refreshCompetencia = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['grilla', competenciaId, disciplinaActiva] }),
      queryClient.invalidateQueries({ queryKey: ['performance-actual', competenciaId] }),
    ])
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

  const resultadoMutation = useMutation({
    mutationFn: async () => {
      await registrarResultado({
        competenciaId: competenciaId!,
        participanteId: atletaActivo!.atletaId,
        disciplina: disciplinaActiva!,
        valorRp: buildRpValue(metros, centimetros),
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
      await asignarTarjeta({
        competenciaId: competenciaId!,
        participanteId: atletaActivo!.atletaId,
        disciplina: disciplinaActiva!,
        tarjeta: selectedCard!,
        motivoDq: selectedCard === 'Roja' ? motivoDq : undefined,
        distanciaBlackout:
          selectedCard === 'Roja' && needsBlackoutDistance ? distanciaBlackout : undefined,
      })
    },
    onSuccess: async () => {
      setInlineError(null)
      await refreshCompetencia()
      seleccionarAtleta({ ...atletaActivo!, estado: 'Ejecutada' })
      setCompleted(true)
    },
    onError: (error) => {
      setInlineError(error instanceof Error ? error.message : 'No se pudo asignar la tarjeta')
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

  if (!competenciaId || !disciplinaActiva || !atletaActivo) {
    return <Navigate to="/juez/grilla" replace />
  }

  return (
    <JuezLayout
      title="Performance"
      subtitle={`${disciplinaActiva} · ${atletaActivo.nombreAtleta}`}
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
          <p className="text-sm text-slate-300">Confirma la llamada del atleta para habilitar la performance.</p>
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
          <p className="text-sm text-slate-300">Confirmado que el atleta está en cámara y listo para iniciar.</p>
          <button
            type="button"
            onClick={() => setStep(3)}
            className="w-full rounded-2xl bg-emerald-400 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950"
          >
            CONTINUAR
          </button>
        </section>
      ) : null}

      {!completed && step === 3 ? (
        <section className="space-y-4 rounded-[2rem] border border-slate-800 bg-slate-900/80 p-5">
          <h3 className="text-xl font-semibold text-white">Paso 3 · OT</h3>
          <p className="text-sm text-slate-300">OT programado: {new Date(atletaActivo.otProgramado).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
          <button
            type="button"
            onClick={() => setStep(4)}
            className="w-full rounded-2xl bg-amber-300 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950"
          >
            INICIAR VENTANA OT
          </button>
        </section>
      ) : null}

      {!completed && step === 4 ? (
        <section className="space-y-4 rounded-[2rem] border border-slate-800 bg-slate-900/80 p-5">
          <h3 className="text-xl font-semibold text-white">Paso 4 · Performance</h3>
          <p className="text-sm text-slate-300">
            {chronoStarted
              ? 'La performance está en curso. Finaliza cuando el atleta complete su intento.'
              : 'Inicia el cronómetro local cuando comience la performance.'}
          </p>
          {!chronoStarted ? (
            <button
              type="button"
              onClick={() => setChronoStarted(true)}
              className="w-full rounded-2xl bg-fuchsia-300 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950"
            >
              INICIAR CRONO
            </button>
          ) : (
            <button
              type="button"
              onClick={() => setStep(5)}
              className="w-full rounded-2xl bg-orange-300 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950"
            >
              FINALIZAR PERFORMANCE
            </button>
          )}
        </section>
      ) : null}

      {!completed && step === 5 ? (
        <section className="space-y-4">
          <RpSelector
            metros={metros}
            centimetros={centimetros}
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
          <div className="grid grid-cols-2 gap-3">
            {(['Blanca', 'Roja'] as const).map((card) => (
              <button
                key={card}
                type="button"
                onClick={() => setSelectedCard(card)}
                className={[
                  'rounded-2xl border px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] transition',
                  selectedCard === card
                    ? 'border-cyan-300 bg-cyan-400/15 text-cyan-100'
                    : 'border-slate-700 bg-slate-950/70 text-slate-200',
                ].join(' ')}
              >
                Tarjeta {card}
              </button>
            ))}
          </div>

          {selectedCard === 'Roja' ? (
            <div className="space-y-3 rounded-2xl bg-slate-950/70 p-4">
              <label className="block text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
                Motivo DQ
              </label>
              <select
                value={motivoDq}
                onChange={(event) => setMotivoDq(event.target.value as (typeof dqReasons)[number] | '')}
                className="w-full rounded-2xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-white"
              >
                <option value="">Seleccionar</option>
                {dqReasons.map((reason) => (
                  <option key={reason} value={reason}>
                    {reason}
                  </option>
                ))}
              </select>

              {needsBlackoutDistance ? (
                <input
                  value={distanciaBlackout}
                  onChange={(event) => setDistanciaBlackout(event.target.value)}
                  placeholder="Distancia blackout"
                  className="w-full rounded-2xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-white"
                />
              ) : null}
            </div>
          ) : null}

          <button
            type="button"
            disabled={!selectedCard || !canSubmitRedCard || tarjetaMutation.isPending}
            onClick={() => tarjetaMutation.mutate()}
            className="w-full rounded-2xl bg-cyan-400 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950 disabled:opacity-50"
          >
            CONFIRMAR TARJETA
          </button>
        </section>
      ) : null}

      {completed ? (
        <section className="space-y-4 rounded-[2rem] border border-emerald-300/30 bg-emerald-400/10 p-5">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-300">
            Performance completada
          </p>
          <h3 className="text-2xl font-semibold text-white">
            TARJETA {selectedCard?.toUpperCase()} · {buildRpValue(metros, centimetros)} m
          </h3>
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
