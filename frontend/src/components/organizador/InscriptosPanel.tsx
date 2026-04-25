import { useQuery } from '@tanstack/react-query'
import {
  fetchCompetenciasPorTorneo,
  fetchGrillaCompetencia,
  type GrillaAtletaDto,
} from '../../api/competencia'
import { fetchAtleta, listarInscriptos } from '../../api/registro'
import { TablaInscriptos, type InscriptoRow } from './TablaInscriptos'

interface InscriptosPanelProps {
  torneoId: string
}

function buildApMap(grillas: Array<{ disciplina: string; entradas: GrillaAtletaDto[] }>) {
  const map = new Map<string, { ap: string | null; unidad: string | null }>()
  for (const grilla of grillas) {
    for (const entrada of grilla.entradas) {
      map.set(`${entrada.atleta_id}:${grilla.disciplina}`, {
        ap: entrada.ap_declarado,
        unidad: entrada.unidad,
      })
    }
  }
  return map
}

async function loadInscriptos(torneoId: string) {
  const [inscriptos, competencias] = await Promise.all([
    listarInscriptos(torneoId),
    fetchCompetenciasPorTorneo(torneoId),
  ])
  const atletas = await Promise.all(inscriptos.map((inscripto) => fetchAtleta(inscripto.atleta_id)))
  const atletaPorId = new Map(atletas.map((atleta) => [atleta.atleta_id, atleta]))
  const disciplinas = Array.from(
    new Set(inscriptos.flatMap((inscripto) => inscripto.disciplinas)),
  ).sort()
  const competenciasPorDisciplina = new Map(
    competencias.map((competencia) => [competencia.disciplina, competencia]),
  )
  const grillas = await Promise.all(
    disciplinas.map(async (disciplina) => {
      const competencia = competenciasPorDisciplina.get(disciplina)
      if (!competencia) {
        return { disciplina, entradas: [] }
      }
      try {
        const entradas = await fetchGrillaCompetencia(competencia.competencia_id, disciplina)
        return { disciplina, entradas }
      } catch {
        return { disciplina, entradas: [] }
      }
    }),
  )
  const apMap = buildApMap(grillas)
  const rows: InscriptoRow[] = inscriptos.map((inscripto) => {
    const atleta = atletaPorId.get(inscripto.atleta_id)
    const estadoApPorDisciplina = Object.fromEntries(
      inscripto.disciplinas.map((disciplina) => [
        disciplina,
        apMap.get(`${inscripto.atleta_id}:${disciplina}`) ?? { ap: null, unidad: null },
      ]),
    )

    return {
      inscripcionId: inscripto.inscripcion_id,
      atletaId: inscripto.atleta_id,
      nombre: atleta ? `${atleta.apellido}, ${atleta.nombre}` : 'Atleta sin datos',
      club: atleta?.club ?? 'Sin dato',
      categoria: atleta?.categoria ?? 'Sin dato',
      genero: 'Sin dato',
      disciplinas: inscripto.disciplinas,
      estadoApPorDisciplina,
    }
  })

  return { rows, disciplinas }
}

export function InscriptosPanel({ torneoId }: InscriptosPanelProps) {
  const query = useQuery({
    queryKey: ['torneo-inscriptos-ap', torneoId],
    queryFn: () => loadInscriptos(torneoId),
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
