import { useQuery } from '@tanstack/react-query'
import { listarInscriptosDetalle } from '../../api/registro'
import type { EstadoTorneo } from '../../api/torneo'
import { EmptyStateCard } from './EmptyStateCard'
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
    enabled: torneoEstado === 'INSCRIPCION_ABIERTA',
  })

  if (torneoEstado !== 'INSCRIPCION_ABIERTA') {
    return <EmptyStateCard message="La inscripción todavía no está habilitada para este torneo." />
  }

  if (query.isLoading) {
    return (
      <section className="rounded-[2rem] border border-slate-700 bg-slate-900/70 p-5 text-sm text-slate-300">
        Cargando inscriptos...
      </section>
    )
  }

  if (query.isError) {
    return (
      <section className="rounded-[2rem] border border-red-500/40 bg-red-950/40 p-5 text-sm text-red-100">
        No se pudieron cargar los inscriptos del torneo.
      </section>
    )
  }

  if ((query.data?.rows ?? []).length === 0) {
    return <EmptyStateCard message="Todavía no hay inscriptos para este torneo." />
  }

  return (
    <article className="rounded-[2rem] border border-slate-700 bg-slate-900/85 p-6 shadow-[0_20px_60px_rgba(2,6,23,0.24)]">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
            Gestión de inscriptos
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-white">Atletas del torneo</h2>
          <p className="mt-2 text-sm text-slate-300">
            Revisa inscripciones, disciplinas activas y el estado de AP por atleta.
          </p>
        </div>
      </div>

      <div className="rounded-[1.5rem] border border-slate-700 bg-slate-950/70 p-4">
        <TablaInscriptos rows={query.data?.rows ?? []} disciplinas={query.data?.disciplinas ?? []} />
      </div>
    </article>
  )
}
