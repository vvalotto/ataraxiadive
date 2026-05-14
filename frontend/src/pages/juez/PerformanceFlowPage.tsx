import { Link, Navigate, useNavigate } from 'react-router-dom'
import { AtletaCard } from '../../components/juez/AtletaCard'
import { JuezLayout } from '../../components/juez/JuezLayout'
import { RpSelector } from '../../components/juez/RpSelector'
import { StepBKO } from '../../components/juez/StepBKO'
import { StepIndicator } from '../../components/juez/StepIndicator'
import { StepRevision } from '../../components/juez/StepRevision'
import { StepTarjeta } from '../../components/juez/StepTarjeta'
import { usePerformanceFlow } from '../../hooks/usePerformanceFlow'

export function PerformanceFlowPage() {
  const navigate = useNavigate()
  const flow = usePerformanceFlow()

  if (!flow.competenciaId || !flow.disciplinaActiva || !flow.atletaActivo) {
    return <Navigate to="/juez/grilla" replace />
  }

  return (
    <JuezLayout
      title={flow.disciplinaActiva}
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
        <StepIndicator currentStep={flow.completed ? 6 : flow.step} />
      </section>

      {flow.step !== 4 && flow.step !== 5 && flow.step !== 6 && flow.step !== 7 ? (
        <AtletaCard
          nombreAtleta={flow.atletaActivo.nombreAtleta}
          apDeclarado={flow.atletaActivo.apDeclarado}
          unidad={flow.atletaActivo.unidad}
          andarivel={flow.atletaActivo.andarivel}
          otProgramado={flow.atletaActivo.otProgramado}
          estado={flow.completed ? 'COMPLETADA' : flow.atletaActivo.estado}
        />
      ) : null}

      {flow.inlineError ? (
        <section className="rounded-3xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-100">
          {flow.inlineError}
        </section>
      ) : null}

      {/* Paso 1 — Llamada */}
      {!flow.completed && flow.step === 1 ? (
        <section className="space-y-4 rounded-[2rem] border border-slate-800 bg-slate-900/80 p-5">
          <h3 className="text-xl font-semibold text-white">Paso 1 · Llamada</h3>
          <p className="text-sm text-slate-300">
            Confirma la llamada del atleta para habilitar la performance.
          </p>
          <button
            type="button"
            onClick={() => flow.llamarMutation.mutate()}
            disabled={flow.llamarMutation.isPending}
            className="w-full rounded-2xl bg-cyan-400 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950 disabled:opacity-60"
          >
            LLAMAR ATLETA
          </button>
        </section>
      ) : null}

      {/* Paso 2 — Confirmar presencia */}
      {!flow.completed && flow.step === 2 ? (
        <section className="space-y-4 rounded-[2rem] border border-slate-800 bg-slate-900/80 p-5">
          <h3 className="text-xl font-semibold text-white">Paso 2 · Confirmar presencia</h3>
          <p className="text-sm text-slate-300">
            Confirmado que el atleta está en cámara y listo para iniciar.
          </p>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <button
              type="button"
              onClick={() => {
                flow.setOtWindowActive(false)
                flow.setStep(3)
              }}
              className="w-full rounded-2xl bg-emerald-400 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950"
            >
              CONTINUAR
            </button>
            <button
              type="button"
              onClick={() => flow.dnsMutation.mutate()}
              disabled={flow.dnsMutation.isPending}
              className="w-full rounded-2xl border border-red-300/30 bg-red-500/10 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-red-100 disabled:opacity-60"
            >
              DNS — NO SE PRESENTA
            </button>
          </div>
        </section>
      ) : null}

      {/* Paso 3 — OT */}
      {!flow.completed && flow.step === 3 ? (
        <section className="space-y-4 rounded-[2rem] border border-slate-800 bg-slate-900/80 p-5">
          <h3 className="text-xl font-semibold text-white">Paso 3 · OT</h3>
          <p className="text-sm text-slate-300">
            OT programado:{' '}
            {new Date(flow.atletaActivo.otProgramado).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </p>
          {!flow.otWindowActive ? (
            <button
              type="button"
              onClick={() => flow.setOtWindowActive(true)}
              className="w-full rounded-2xl bg-amber-300 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950"
            >
              INICIAR VENTANA OT
            </button>
          ) : (
            <>
              <button
                type="button"
                onClick={() => {
                  flow.setChronoStarted(true)
                  flow.setStep(4)
                }}
                className="w-full rounded-2xl bg-emerald-400 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950"
              >
                {flow.isSTA ? 'VIAS RESPIRATORIAS EN AGUA' : 'ATLETA INICIA'}
              </button>
            </>
          )}
        </section>
      ) : null}

      {/* Paso 4 — Performance en curso */}
      {!flow.completed && flow.step === 4 && !flow.isBkoMode ? (
        <section className="space-y-4 rounded-[2rem] border border-slate-800 bg-slate-900/80 p-5">
          <div>
            <h3 className="text-xl font-semibold text-white">Paso 4 · Performance</h3>
            <p className="mt-0.5 text-sm font-semibold text-slate-300">{flow.atletaActivo.nombreAtleta}</p>
          </div>
          <p className="text-sm text-slate-300">
            {flow.chronoStarted
              ? 'La performance esta en curso. Finaliza cuando el atleta complete su intento.'
              : 'La performance ya fue iniciada desde la ventana OT.'}
          </p>
          <button
            type="button"
            onClick={() => flow.setStep(5)}
            className="w-full rounded-2xl bg-orange-300 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950"
          >
            FINALIZAR PERFORMANCE
          </button>
          <button
            type="button"
            onClick={() => {
              flow.setIsBkoMode(true)
              flow.setSelectedCard('Roja')
              flow.setMotivoDq('BKO_SUBACUATICO')
            }}
            className="w-full rounded-2xl border border-red-300/30 bg-red-500/10 px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-red-100"
          >
            BKO — BLACK-OUT
          </button>
        </section>
      ) : null}

      {/* Paso 4 — BKO mode */}
      {!flow.completed && flow.step === 4 && flow.isBkoMode ? (
        <p className="px-1 text-sm font-semibold text-slate-300">{flow.atletaActivo.nombreAtleta}</p>
      ) : null}
      {!flow.completed && flow.step === 4 && flow.isBkoMode ? (
        <StepBKO
          isSTA={flow.isSTA}
          metros={flow.metros}
          centimetros={flow.centimetros}
          unidad={flow.atletaActivo.unidad}
          motivoDq={flow.motivoDq}
          canSubmitBko={flow.canSubmitBko}
          isPending={flow.bkoMutation.isPending}
          onMetrosChange={flow.setMetros}
          onCentimetrosChange={flow.setCentimetros}
          onMotivoDqChange={flow.setMotivoDq}
          onConfirm={() => flow.bkoMutation.mutate()}
          onCancel={() => {
            flow.setIsBkoMode(false)
            flow.setMotivoDq('')
          }}
        />
      ) : null}

      {/* Paso 5 — Asignar tarjeta */}
      {!flow.completed && flow.step === 5 ? (
        <p className="px-1 text-sm font-semibold text-slate-300">{flow.atletaActivo.nombreAtleta}</p>
      ) : null}
      {!flow.completed && flow.step === 5 ? (
        <StepTarjeta
          selectedCard={flow.selectedCard}
          motivoDq={flow.motivoDq}
          canSubmitRedCard={flow.canSubmitRedCard}
          isPending={false}
          penalizaciones={{
            items: flow.penalizaciones,
            disciplina: flow.disciplinaActiva ?? '',
            admite: flow.disciplinaPermitePenalizaciones,
            onChange: flow.setPenalizaciones,
          }}
          onSelectCard={flow.setSelectedCard}
          onMotivoDqChange={flow.setMotivoDq}
          onConfirm={() => flow.setStep(6)}
        />
      ) : null}

      {/* Paso 6 — Registrar RP y confirmar marca */}
      {!flow.completed && flow.step === 6 ? (
        <section className="space-y-3">
          <AtletaCard
            variant="compact"
            nombreAtleta={flow.atletaActivo.nombreAtleta}
            apDeclarado={flow.atletaActivo.apDeclarado}
            unidad={flow.atletaActivo.unidad}
            andarivel={flow.atletaActivo.andarivel}
            otProgramado={flow.atletaActivo.otProgramado}
            estado="EN CURSO"
          />
          <RpSelector
            metros={flow.metros}
            centimetros={flow.centimetros}
            unidad={flow.atletaActivo.unidad}
            onMetrosChange={flow.setMetros}
            onCentimetrosChange={flow.setCentimetros}
          />
          <button
            type="button"
            disabled={flow.rpConfirmDisabled || flow.resultadoMutation.isPending}
            onClick={() => flow.resultadoMutation.mutate()}
            className="w-full rounded-2xl bg-white px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950 disabled:opacity-50"
          >
            CONFIRMAR MARCA
          </button>
        </section>
      ) : null}

      {/* Paso 7 — Resolver revisión */}
      {!flow.completed && flow.step === 7 ? (
        <StepRevision
          nombreAtleta={flow.atletaActivo.nombreAtleta}
          selectedCard={flow.selectedCard}
          motivoDq={flow.motivoDq}
          canSubmitRedCard={flow.canSubmitRedCard}
          isPending={flow.resolverRevisionMutation.isPending}
          onSelectCard={flow.setSelectedCard}
          onMotivoDqChange={flow.setMotivoDq}
          onConfirm={() => flow.resolverRevisionMutation.mutate()}
          onVolver={() => {
            flow.goToNextAtleta()
            void navigate('/juez/grilla')
          }}
        />
      ) : null}

      {/* Completada */}
      {flow.completed ? (
        <section
          className={[
            'space-y-4 rounded-[2rem] border p-5',
            flow.resultKind === 'ROJA'
              ? 'border-red-300/30 bg-red-500/10'
              : flow.resultKind === 'DNS'
                ? 'border-slate-600/40 bg-slate-800/40'
                : flow.resultKind === 'AMARILLA'
                  ? 'border-amber-300/30 bg-amber-400/10'
                  : 'border-emerald-300/30 bg-emerald-400/10',
          ].join(' ')}
        >
          <p
            className={[
              'text-xs font-semibold uppercase tracking-[0.24em]',
              flow.resultKind === 'ROJA'
                ? 'text-red-300'
                : flow.resultKind === 'DNS'
                  ? 'text-slate-400'
                  : flow.resultKind === 'AMARILLA'
                    ? 'text-amber-300'
                    : 'text-emerald-300',
            ].join(' ')}
          >
            {flow.resultKind === 'DNS' ? 'DNS registrado' : 'Performance completada'}
          </p>
          <h3 className="text-2xl font-semibold text-white">{flow.completionTitle}</h3>
          <p className="text-sm text-slate-200">{flow.completionSubtitle}</p>
          <button
            type="button"
            onClick={flow.goToNextAtleta}
            className="w-full rounded-2xl bg-white px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950"
          >
            SIGUIENTE ATLETA
          </button>
        </section>
      ) : null}
    </JuezLayout>
  )
}
