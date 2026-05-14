import { useQuery } from '@tanstack/react-query'
import { Link, useParams, useSearchParams } from 'react-router-dom'
import {
  fetchEstadoCompetencia,
  fetchGrillaCompetencia,
  type EstadoCompetenciaDto,
  type GrillaAtletaDto,
} from '../../api/competencia'
import { fetchAtletaMe } from '../../api/registro'
import { fetchTorneo } from '../../api/torneo'
import { GrillaRow } from '../../components/atleta/GrillaRow'
import { AtletaShell } from '../../components/atleta/AtletaShell'
import { OtHero } from '../../components/atleta/OtHero'
import { formatAp, formatDisciplina, formatHora } from './portalData'

interface MiGrillaData {
  atletaId: string
  grilla: GrillaAtletaDto[]
  estado: EstadoCompetenciaDto | null
  torneoNombre: string
}

async function loadMiGrilla(
  competenciaId: string,
  disciplina: string,
): Promise<MiGrillaData> {
  const [atleta, grilla, estadoResult] = await Promise.all([
    fetchAtletaMe(),
    fetchGrillaCompetencia(competenciaId, disciplina),
    fetchEstadoCompetencia(competenciaId, disciplina).catch(() => null),
  ])

  const torneo = estadoResult?.torneo_id
    ? await fetchTorneo(estadoResult.torneo_id).catch(() => null)
    : null

  return {
    atletaId: atleta.atleta_id,
    grilla: [...grilla].sort((left, right) => left.posicion - right.posicion),
    estado: estadoResult,
    torneoNombre: torneo?.nombre ?? 'Competencia',
  }
}

export function AtletaMiGrillaPage() {
  const { competenciaId } = useParams<{ competenciaId: string }>()
  const [searchParams] = useSearchParams()
  const disciplina = searchParams.get('disciplina') ?? ''

  const query = useQuery({
    queryKey: ['atleta-mi-grilla', competenciaId, disciplina],
    queryFn: () => loadMiGrilla(competenciaId ?? '', disciplina),
    enabled: Boolean(competenciaId && disciplina),
  })

  const miEntrada = query.data?.grilla.find((entry) => entry.atleta_id === query.data?.atletaId) ?? null
  const hasDatosIncompletos = !competenciaId || !disciplina

  return (
    <AtletaShell
      title={`Mi grilla${disciplina ? ` · ${formatDisciplina(disciplina)}` : ''}`}
      subtitle="Tu OT, andarivel y orden completo de salida."
      showBack
    >
      {hasDatosIncompletos ? (
        <div className="rounded-3xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-100">
          Faltan datos para cargar la grilla.
        </div>
      ) : null}

      {query.isLoading ? (
        <div className="rounded-3xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-300">
          Cargando grilla...
        </div>
      ) : null}

      {query.isError ? (
        <div className="rounded-3xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-100">
          No se pudo cargar la grilla de esta disciplina.
        </div>
      ) : null}

      {query.data ? (
        <div className="space-y-4">
          {query.data.estado?.grilla_confirmada === false ? (
            <div className="rounded-3xl border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-amber-100">
              Grilla provisional - puede cambiar antes del inicio
            </div>
          ) : null}

          {!miEntrada ? (
            <div className="rounded-3xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-400">
              La grilla aún no está disponible para esta disciplina.
            </div>
          ) : null}

          {miEntrada ? (
            <OtHero
              ot={formatHora(miEntrada.ot_programado)}
              andarivel={miEntrada.andarivel}
              posicion={miEntrada.posicion}
              ap={formatAp(miEntrada.ap_declarado, miEntrada.unidad)}
              torneo={query.data.torneoNombre}
              disciplina={formatDisciplina(disciplina)}
            />
          ) : null}

          {query.data.grilla.length > 0 ? (
            <section className="rounded-[1.75rem] border border-slate-800 bg-slate-900 overflow-hidden">
              <p className="px-4 pt-4 text-xs font-semibold uppercase tracking-[0.22em] text-sky-400">
                Orden de salida
              </p>
              <div className="mt-3 overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-slate-800">
                      <th className="px-4 pb-2 text-center text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Pos</th>
                      <th className="px-0 pb-2 text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Atleta</th>
                      <th className="px-4 pb-2 text-center text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">OT</th>
                      <th className="px-4 pb-2 text-center text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">And.</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 px-4">
                    {query.data.grilla.map((entry) => (
                      <GrillaRow
                        key={entry.performance_id}
                        posicion={entry.posicion}
                        nombre={entry.nombre_atleta}
                        ot={formatHora(entry.ot_programado)}
                        andarivel={entry.andarivel}
                        isSelf={entry.atleta_id === query.data.atletaId}
                      />
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          ) : null}

          {miEntrada ? (
            <Link
              to={`/atleta/resultados?competenciaId=${encodeURIComponent(competenciaId ?? '')}&disciplina=${encodeURIComponent(disciplina)}`}
              className="flex min-h-11 items-center justify-center rounded-2xl bg-sky-500 px-4 py-3 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950"
            >
              Ver mis resultados
            </Link>
          ) : null}
        </div>
      ) : null}
    </AtletaShell>
  )
}
