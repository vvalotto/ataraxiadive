function buildRpValue(metros: number, centimetros: string): string {
  return `${metros}.${centimetros.padEnd(2, '0')}`
}

function esUnidadSegundos(unidad: string): boolean {
  return unidad.toLowerCase() === 'segundos'
}

export function buildResultadoValue(metros: number, centimetros: string, unidad: string): string {
  if (esUnidadSegundos(unidad)) {
    return String(metros * 60 + Number(centimetros || '0'))
  }
  return buildRpValue(metros, centimetros)
}

export function formatMarca(value: string, unidad: string): string {
  if (esUnidadSegundos(unidad)) {
    const parsedSeconds = Number(value || '0')
    const totalSeconds = Number.isFinite(parsedSeconds) ? Math.max(0, Math.round(parsedSeconds)) : 0
    const minutos = Math.floor(totalSeconds / 60)
    const segundos = totalSeconds % 60
    return `${minutos}:${String(segundos).padStart(2, '0')} min`
  }
  return `${String(value).replace('.', ',')} m`
}
