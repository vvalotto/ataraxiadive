import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { guardarApInscripcion, listarInscriptosDetalle } from '../../api/registro'
import type { EstadoTorneo } from '../../api/torneo'
import { normalizeApInput } from '../../pages/atleta/portalData'
import { EmptyStateCard } from './EmptyStateCard'
import { InscripcionDetalleDrawer } from './InscripcionDetalleDrawer'
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
      estadoAceptacion: inscripto.estado_aceptacion,
      disciplinas: inscripto.disciplinas.map((item) => item.disciplina),
      estadoApPorDisciplina,
    }
  })

  return { rows, disciplinas }
}

export function InscriptosPanel({ torneoId, torneoEstado }: InscriptosPanelProps) {
  const queryClient = useQueryClient()
  const [selectedInscripcionId, setSelectedInscripcionId] = useState<string | null>(null)

  const query = useQuery({
    queryKey: ['torneo-inscriptos-ap', torneoId, torneoEstado],
    queryFn: () => loadInscriptos(torneoId, torneoEstado),
  })

  const editable = torneoEstado === 'INSCRIPCION_ABIERTA'
  const saveMutation = useMutation({
    mutationFn: async (payload: { inscripcionId: string; disciplina: string; valorAp: string }) => {
      await guardarApInscripcion({
        ...payload,
        valorAp: normalizeApInput(payload.valorAp, payload.disciplina),
      })
      return payload
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['torneo-inscriptos-ap', torneoId] })
    },
  })

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
    <div className="flex gap-4">
      <article
        className={`rounded-[2rem] border border-slate-700 bg-slate-900/85 p-6 shadow-[0_20px_60px_rgba(2,6,23,0.24)] transition-all ${
          selectedInscripcionId ? 'flex-1 min-w-0' : 'w-full'
        }`}
      >
        {saveMutation.isError ? (
          <section className="mb-4 rounded-2xl border border-red-500/40 bg-red-950/40 p-4 text-sm text-red-100">
            No se pudo guardar el AP para la inscripción seleccionada.
          </section>
        ) : null}
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
          <TablaInscriptos
            rows={query.data?.rows ?? []}
            disciplinas={query.data?.disciplinas ?? []}
            editable={editable}
            savingKey={
              saveMutation.isPending && saveMutation.variables
                ? `${saveMutation.variables.inscripcionId}:${saveMutation.variables.disciplina}`
                : null
            }
            onGuardarAp={(payload) => saveMutation.mutate(payload)}
            onRowClick={(id) =>
              setSelectedInscripcionId((prev) => (prev === id ? null : id))
            }
            selectedInscripcionId={selectedInscripcionId}
          />
        </div>
      </article>

      {selectedInscripcionId && (
        <aside className="w-80 shrink-0">
          <InscripcionDetalleDrawer
            inscripcionId={selectedInscripcionId}
            torneoId={torneoId}
            onClose={() => setSelectedInscripcionId(null)}
          />
        </aside>
      )}
    </div>
  )
}
