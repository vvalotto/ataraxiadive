export function admitePenalizaciones(disciplina: string): boolean {
  return disciplina === 'DNF' || disciplina === 'DYN' || disciplina === 'DBF'
}
