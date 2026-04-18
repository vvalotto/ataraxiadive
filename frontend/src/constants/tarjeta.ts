export const DQ_REASONS = [
  'BKO_SUPERFICIE',
  'BKO_SUBACUATICO',
  'PROTOCOLO_SUPERFICIE',
  'INFRACCION_TECNICA_DQ',
  'NO_INICIO_EN_VENTANA',
  'SALIDA_EN_FALSO',
] as const

export const BKO_REASONS = ['BKO_SUPERFICIE', 'BKO_SUBACUATICO'] as const

export const PENALTY_TYPES = [
  'SIN_CONTACTO_PARED',
  'FUERA_DE_CARRIL',
  'ASISTENTE_EN_ZONA',
  'PATADA_DELFIN_BIALETAS',
] as const

export const PENALTY_LABELS: Record<string, string> = {
  SIN_CONTACTO_PARED: 'Sin contacto con pared',
  FUERA_DE_CARRIL: 'Fuera de carril',
  ASISTENTE_EN_ZONA: 'Asistente en zona',
  PATADA_DELFIN_BIALETAS: 'Patada delfín con bialetas',
}

export type DqReason = (typeof DQ_REASONS)[number]
export type PenaltyType = (typeof PENALTY_TYPES)[number]
