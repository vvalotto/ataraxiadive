import { useQuery } from '@tanstack/react-query'
import { listarInscriptosDetalle } from '../../api/registro'
import type { EstadoTorneo } from '../../api/torneo'
import { TablaInscriptos, type InscriptoRow } from './TablaInscriptos'

interface InscriptosPanelProps {
  torneoId: string
  torneoEstado: EstadoTorneo
}

function buildEstadoAp(
  torneoEstado: EstadoTorneo,
  ap: string | null,
): 'pendiente' | 'declarado' | 'cerrado' {
  if (torneoEstado !== 'INSCRIPCION_ABIERTA') {
    return 'cerrado'
  }
  return ap?.trim() ? 'declarado' : 'pendiente'
}

async function loadInscriptos(torneoId: string, torneoEstado: EstadoTorneo) {
  const inscriptos = await listarInscriptosDetalle(torneoId)
  const disciplinas = Array.from(
    new Set(inscriptos.flatMap((inscripto) => inscripto.disciplinas.map((item) => item.disciplina))),
  ).sort()
  const rows: InscriptoRow[] = inscriptos.map((inscripto) => {
    const estadoApPorDisciplina = Object.fromEntries(
      inscripto.disciplinas.map((disciplina) => [
        disciplina.disciplina,
        {
          estado: buildEstadoAp(torneoEstado, disciplina.ap),
          ap: disciplina.ap,
          unidad: disciplina.unidad,
        },
      ]),
    )

    return {
      inscripcionId: inscripto.inscripcion_id,
      atletaId: inscripto.atleta_id,
      nombre: `${inscripto.apellido}, ${inscripto.nombre}`.trim(),
      club: inscripto.club || 'Sin dato',
      categoria: inscripto.categoria || 'Sin dato',
      estadoInscripcion: inscripto.estado,
      disciplinas: inscripto.disciplinas.map((item) => item.disciplina),
      estadoApPorDisciplina,
    }
  })

  return { rows, disciplinas }
}

export function InscriptosPanel({ torneoId, torneoEstado }: InscriptosPanelProps) {
  const query = useQuery({
    queryKey: ['torneo-inscriptos-ap', torneoId, torneoEstado],
    queryFn: () => loadInscriptos(torneoId, torneoEstado),
  })

  if (query.isLoading) {
    return (
      <div className="rounded-lg border border-stone-200 bg-stone-50 p-4 text-sm text-stone-600">
        Cargando inscriptos...
      </div>
    )
  }

  if (query.isError) {
    return (
      <div className="rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-900">
        No se pudieron cargar los inscriptos del torneo.
      </div>
    )
  }

  return <TablaInscriptos rows={query.data?.rows ?? []} disciplinas={query.data?.disciplinas ?? []} />
}
