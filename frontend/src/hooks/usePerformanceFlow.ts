import { useMemo, useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  ApiError,
  asignarTarjeta,
  llamarAtleta,
  registrarDns,
  registrarResultado,
  resolverRevision,
  type PenalizacionPayload,
} from '../api/competencia'
import { admitePenalizaciones } from '../utils/disciplina'
import useCompetenciaStore from '../stores/useCompetenciaStore'

export type TarjetaSeleccionada = 'Blanca' | 'Roja' | 'BlancaConPenalizaciones' | 'Amarilla' | null
export type ResultadoFinal = 'BLANCA' | 'BLANCA_CON_PENALIZACIONES' | 'ROJA' | 'AMARILLA' | 'DNS' | null

function buildRpValue(metros: number, centimetros: string) {
  return `${metros}.${centimetros.padEnd(2, '0')}`
}

export function buildResultadoValue(metros: number, centimetros: string, unidad: string) {
  if (unidad === 'Segundos') {
    return String(metros * 60 + Number(centimetros || '0'))
  }
  return buildRpValue(metros, centimetros)
}

export function formatMarca(value: string, unidad: string) {
  if (unidad === 'Segundos') {
    const totalSeconds = Number(value || '0')
    const minutos = Math.floor(totalSeconds / 60)
    const segundos = totalSeconds % 60
    return `${minutos}:${String(segundos).padStart(2, '0')} min`
  }
  return `${value} m`
}

export function usePerformanceFlow() {
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
  const [penalizaciones, setPenalizaciones] = useState<PenalizacionPayload[]>([])
  const [isBkoMode, setIsBkoMode] = useState(false)
  const [completed, setCompleted] = useState(false)
  const [resultKind, setResultKind] = useState<ResultadoFinal>(null)

  // ── Derived ────────────────────────────────────────────────────────────────

  const rpConfirmDisabled = metros === 0 && centimetros.length === 0
  const needsBlackoutDistance = motivoDq === 'BKO_SUPERFICIE' || motivoDq === 'BKO_SUBACUATICO'
  const isSTA = atletaActivo?.unidad === 'Segundos'
  const disciplinaPermitePenalizaciones = disciplinaActiva
    ? admitePenalizaciones(disciplinaActiva)
    : false

  const canSubmitRedCard = useMemo(() => {
    if (selectedCard !== 'Roja') return true
    if (!motivoDq) return false
    return true
  }, [selectedCard, motivoDq])

  const canSubmitBko = isSTA
    ? motivoDq.length > 0
    : !rpConfirmDisabled && motivoDq.length > 0

  const completionTitle = useMemo(() => {
    if (resultKind === 'DNS') return 'DNS REGISTRADO'
    if (resultKind === 'AMARILLA') return 'TARJETA AMARILLA'
    if (resultKind === 'ROJA') return 'TARJETA ROJA'
    if (resultKind === 'BLANCA_CON_PENALIZACIONES') return 'TARJETA BLANCA CON PENALIZACIONES'
    return 'TARJETA BLANCA'
  }, [resultKind])

  const completionSubtitle = useMemo(() => {
    if (resultKind === 'DNS') return 'No se presentó'
    if (resultKind === 'AMARILLA') return 'La performance queda en revision hasta definir tarjeta final'
    const marca = formatMarca(
      buildResultadoValue(metros, centimetros, atletaActivo?.unidad ?? 'Metros'),
      atletaActivo?.unidad ?? 'Metros',
    )
    if (resultKind === 'BLANCA_CON_PENALIZACIONES') return `${marca} · ${penalizaciones.length} penalizaciones`
    return marca
  }, [resultKind, metros, centimetros, atletaActivo?.unidad, penalizaciones.length])

  // ── Helpers ────────────────────────────────────────────────────────────────

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

  const goToNextAtleta = () => {
    limpiarAtleta()
    void navigate('/juez/grilla')
  }

  // ── Mutations ──────────────────────────────────────────────────────────────

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
    onSuccess: async () => finalizeResult('DNS', 'DNS'),
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
      await asignarTarjeta({
        competenciaId: competenciaId!,
        participanteId: atletaActivo!.atletaId,
        disciplina: disciplinaActiva!,
        tarjeta: selectedCard!,
        motivoTexto: selectedCard === 'Amarilla' ? 'Revision pendiente del juez' : undefined,
        motivoDq: selectedCard === 'Roja' ? motivoDq : undefined,
        distanciaBlackout:
          selectedCard === 'Roja' && needsBlackoutDistance
            ? buildRpValue(metros, centimetros)
            : undefined,
        penalizaciones: selectedCard === 'BlancaConPenalizaciones' ? penalizaciones : [],
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
        distanciaBlackout: isSTA ? undefined : buildRpValue(metros, centimetros),
      })
    },
    onSuccess: async () => finalizeResult('ROJA', 'Ejecutada'),
    onError: (error) => {
      setInlineError(error instanceof Error ? error.message : 'No se pudo registrar BKO')
    },
  })

  return {
    // store
    competenciaId,
    disciplinaActiva,
    atletaActivo,
    // state
    step, setStep,
    inlineError,
    metros, setMetros,
    centimetros, setCentimetros,
    otWindowActive, setOtWindowActive,
    chronoStarted, setChronoStarted,
    selectedCard, setSelectedCard,
    motivoDq, setMotivoDq,
    distanciaBlackout, setDistanciaBlackout,
    penalizaciones, setPenalizaciones,
    isBkoMode, setIsBkoMode,
    completed,
    resultKind,
    // derived
    rpConfirmDisabled,
    needsBlackoutDistance,
    isSTA,
    disciplinaPermitePenalizaciones,
    canSubmitRedCard,
    canSubmitBko,
    completionTitle,
    completionSubtitle,
    // actions
    goToNextAtleta,
    // mutations
    llamarMutation,
    dnsMutation,
    resultadoMutation,
    tarjetaMutation,
    resolverRevisionMutation,
    bkoMutation,
  }
}
