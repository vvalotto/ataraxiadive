import { create } from 'zustand'

export interface AtletaActivo {
  performanceId: string
  atletaId: string
  nombreAtleta: string
  posicion: number
  andarivel: number
  otProgramado: string
  apDeclarado: string
  unidad: string
  estado: string
}

interface CompetenciaState {
  torneoId: string | null
  competenciaId: string | null
  disciplinaActiva: string | null
  atletaActivo: AtletaActivo | null
  seleccionarCompetencia: (payload: {
    torneoId: string
    competenciaId: string
    disciplinaActiva: string
  }) => void
  seleccionarAtleta: (atleta: AtletaActivo) => void
  limpiarAtleta: () => void
  limpiarCompetencia: () => void
}

const useCompetenciaStore = create<CompetenciaState>((set) => ({
  torneoId: null,
  competenciaId: null,
  disciplinaActiva: null,
  atletaActivo: null,
  seleccionarCompetencia: ({ torneoId, competenciaId, disciplinaActiva }) =>
    set({ torneoId, competenciaId, disciplinaActiva, atletaActivo: null }),
  seleccionarAtleta: (atletaActivo) => set({ atletaActivo }),
  limpiarAtleta: () => set({ atletaActivo: null }),
  limpiarCompetencia: () =>
    set({ torneoId: null, competenciaId: null, disciplinaActiva: null, atletaActivo: null }),
}))

export default useCompetenciaStore
