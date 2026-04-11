import { create } from 'zustand'

interface CompetenciaState {
  torneoId: string | null
  competenciaId: string | null
  disciplinaActiva: string | null
  seleccionarCompetencia: (payload: {
    torneoId: string
    competenciaId: string
    disciplinaActiva: string
  }) => void
  limpiarCompetencia: () => void
}

const useCompetenciaStore = create<CompetenciaState>((set) => ({
  torneoId: null,
  competenciaId: null,
  disciplinaActiva: null,
  seleccionarCompetencia: ({ torneoId, competenciaId, disciplinaActiva }) =>
    set({ torneoId, competenciaId, disciplinaActiva }),
  limpiarCompetencia: () => set({ torneoId: null, competenciaId: null, disciplinaActiva: null }),
}))

export default useCompetenciaStore
