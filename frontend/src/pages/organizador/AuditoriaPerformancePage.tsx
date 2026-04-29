import { Link, useParams, useSearchParams } from 'react-router-dom'
import type { AuditLogEventoDto } from '../../api/competencia'
import { OrganizadorLayout } from '../../components/organizador/OrganizadorLayout'
import { useAuditLog } from '../../hooks/useAuditLog'

function formatTimestamp(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('es-AR', {
    hour12: false,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

const TIPO_EVENTO_LABELS: Record<string, string> = {
  APRegistrado: 'AP declarado',
  AtletaLlamado: 'Atleta en llamada',
  ResultadoRegistrado: 'Resultado registrado',
  TarjetaAsignada: 'Tarjeta asignada',
  DNSRegistrado: 'DNS registrado',
  TarjetaEnRevision: 'Tarjeta en revisión',
  RevisionResuelta: 'Revisión resuelta',
  IntervaloOTConfigurado: 'Intervalo OT configurado',
  GrillaGenerada: 'Grilla generada',
  GrillaConfirmada: 'Grilla confirmada',
  CompetenciaIniciada: 'Competencia iniciada',
  CompetenciaFinalizada: 'Competencia finalizada',
}

function formatTipoEvento(tipo: string): string {
  return TIPO_EVENTO_LABELS[tipo] ?? tipo
}

function formatUnidad(datos: Record<string, unknown>): string {
  const unidad = String(datos.unidad ?? '')
  if (unidad === 'Metros') return ' m'
  if (unidad === 'Segundos') return ' s'
  return ''
}

function formatDatos(evento: AuditLogEventoDto) {
  const datos = evento.datos
  if ('ot_programado' in datos) {
    const ot = formatTimestamp(String(datos.ot_programado))
    const andarivel = 'andarivel' in datos ? ` · Andarivel ${String(datos.andarivel)}` : ''
    return `OT: ${ot}${andarivel}`
  }
  if ('valor_ap' in datos) return `AP declarado: ${String(datos.valor_ap)}${formatUnidad(datos)}`
  if ('valor_rp' in datos) return `RP registrado: ${String(datos.valor_rp)}${formatUnidad(datos)}`
  if ('tipo' in datos) return `Tarjeta: ${String(datos.tipo)}`
  if ('resolucion' in datos) return `Resolución: ${String(datos.resolucion)}`
  if ('penalizaciones' in datos) return `Penalizaciones: ${JSON.stringify(datos.penalizaciones)}`
  if ('motivo_dq' in datos && datos.motivo_dq) return `Motivo DQ: ${String(datos.motivo_dq)}`
  return ''
}

export function AuditoriaPerformancePage() {
  const { competenciaId, atletaId } = useParams()
  const [searchParams] = useSearchParams()
  const disciplina = searchParams.get('disciplina')
  const torneoId = searchParams.get('torneo_id')
  const auditLogQuery = useAuditLog(competenciaId, atletaId)

  return (
    <OrganizadorLayout
      title="Traza de performance"
      activeTournamentId={torneoId ?? undefined}
      subtitle={
        auditLogQuery.data
          ? `${auditLogQuery.data.atleta_nombre} · ${auditLogQuery.data.disciplina}`
          : 'Auditoria puntual de eventos'
      }
      actions={
        <Link
          to={`/organizador/competencias/${competenciaId}/auditoria?disciplina=${encodeURIComponent(disciplina ?? '')}&torneo_id=${encodeURIComponent(torneoId ?? '')}`}
          className="rounded-full border border-slate-600 bg-slate-800 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-slate-100"
        >
          Volver a disciplina
        </Link>
      }
    >
      <section className="rounded-[2rem] border border-slate-700 bg-slate-900/75 p-5 text-sm text-slate-300">
        Vista contextual de eventos por atleta. El shell principal permanece visible para volver a cualquier seccion primaria del organizador.
      </section>

      {auditLogQuery.isLoading ? (
        <section className="rounded-[2rem] border border-slate-700 bg-slate-900/70 p-5 text-sm text-slate-300">
          Cargando traza de eventos...
        </section>
      ) : null}

      {auditLogQuery.isError ? (
        <section className="rounded-[2rem] border border-red-500/40 bg-red-950/40 p-5 text-sm text-red-100">
          No se pudo cargar la traza de auditoria de la performance.
        </section>
      ) : null}

      {!auditLogQuery.isLoading && !auditLogQuery.isError && auditLogQuery.data ? (
        <>
          <section className="rounded-[2rem] border border-slate-700 bg-slate-900/85 p-5 shadow-[0_20px_60px_rgba(2,6,23,0.24)]">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
              Performance
            </p>
            <h2 className="mt-2 text-2xl font-semibold text-white">
              {auditLogQuery.data.atleta_nombre}
            </h2>
            <p className="mt-2 text-sm text-slate-300">
              {auditLogQuery.data.disciplina}
            </p>
          </section>

          {auditLogQuery.data.eventos.map((evento) => (
            <article
              key={`${evento.sequence}-${evento.tipo}`}
              className="rounded-[2rem] border border-slate-700 bg-slate-900/85 p-5 shadow-[0_20px_60px_rgba(2,6,23,0.24)]"
            >
              <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                    Evento #{evento.sequence}
                  </p>
                  <h3 className="mt-2 text-xl font-semibold text-white">{formatTipoEvento(evento.tipo)}</h3>
                </div>
                <p className="text-sm text-slate-400">{formatTimestamp(evento.timestamp)}</p>
              </div>
              <p className="mt-4 text-sm leading-6 text-slate-300">{formatDatos(evento)}</p>
            </article>
          ))}
        </>
      ) : null}
    </OrganizadorLayout>
  )
}
