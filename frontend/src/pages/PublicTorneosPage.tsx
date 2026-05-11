import { useQuery } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import { fetchTorneos, listarDisciplinasTorneo, type EstadoTorneo, type TorneoDto } from '../api/torneo'
import { formatFecha } from './atleta/portalData'
import { useNavigateWithRedirect } from '../hooks/useNavigateWithRedirect'
import useAuthStore from '../stores/useAuthStore'

const ESTADO_BADGE: Record<EstadoTorneo, { label: string; classes: string }> = {
  CREADO: {
    label: 'Próximo',
    classes: 'border-slate-600/40 bg-slate-600/10 text-slate-300',
  },
  INSCRIPCION_ABIERTA: {
    label: 'Inscripciones abiertas',
    classes: 'border-sky-500/40 bg-sky-500/10 text-sky-300',
  },
  PREPARACION: {
    label: 'Preparación',
    classes: 'border-yellow-500/40 bg-yellow-500/10 text-yellow-300',
  },
  EJECUCION: {
    label: 'En ejecución',
    classes: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300',
  },
  PREMIACION: {
    label: 'Premiación',
    classes: 'border-amber-400/40 bg-amber-400/10 text-amber-300',
  },
  CERRADO: {
    label: 'Cerrado',
    classes: 'border-slate-700/40 bg-slate-700/10 text-slate-400',
  },
  CANCELADO: {
    label: 'Cancelado',
    classes: 'border-red-500/40 bg-red-500/10 text-red-400',
  },
}

interface Accion {
  label: string
  destino: string | null
  deshabilitado?: boolean
  publico?: boolean
}

function accionPorEstado(torneo: TorneoDto, rol: string | null): Accion | null {
  switch (torneo.estado) {
    case 'INSCRIPCION_ABIERTA':
      return { label: 'Inscribirse', destino: `/atleta/torneos/${torneo.torneo_id}/inscripcion` }
    case 'EJECUCION':
      if (rol === 'juez') return { label: 'Ver panel', destino: '/juez/disciplinas' }
      if (rol === 'organizador') return { label: 'Ver panel', destino: '/organizador/torneo' }
      return { label: 'Ver panel', destino: `/portalapnea/${torneo.torneo_id}`, publico: true }
    case 'PREMIACION':
    case 'CERRADO':
      return { label: 'Ver resultados', destino: null, deshabilitado: true }
    default:
      return null
  }
}

const CATEGORIA_LABELS: Record<string, string> = {
  JUNIOR: 'Junior',
  SENIOR: 'Senior',
  MASTER: 'Master',
}

function TorneoCard({ torneo }: { torneo: TorneoDto }) {
  const navigateWithRedirect = useNavigateWithRedirect()
  const navigate = useNavigate()
  const rol = useAuthStore((s) => s.rol)
  const badge = ESTADO_BADGE[torneo.estado]
  const accion = accionPorEstado(torneo, rol)

  const { data: disciplinas } = useQuery({
    queryKey: ['disciplinas-torneo-public', torneo.torneo_id],
    queryFn: () => listarDisciplinasTorneo(torneo.torneo_id),
    staleTime: 60_000,
  })

  const disciplinaNames = disciplinas?.map((d) => d.disciplina) ?? []
  const categorias = torneo.grupos_etarios.map((g) => CATEGORIA_LABELS[g] ?? g)

  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900 p-5">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h2 className="truncate text-base font-semibold text-white">{torneo.nombre}</h2>
          <p className="mt-1 text-sm text-slate-400">
            {formatFecha(torneo.fecha_inicio)}
            {torneo.fecha_fin !== torneo.fecha_inicio
              ? ` — ${formatFecha(torneo.fecha_fin)}`
              : null}{' '}
            · {torneo.sede.ciudad}, {torneo.sede.pais}
          </p>
        </div>
        <span
          className={`shrink-0 rounded-full border px-3 py-1 text-xs font-semibold ${badge.classes}`}
        >
          {badge.label}
        </span>
      </div>

      {(disciplinaNames.length > 0 || categorias.length > 0) && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {disciplinaNames.map((d) => (
            <span
              key={d}
              className="rounded-full border border-sky-700/40 bg-sky-900/30 px-2.5 py-0.5 text-xs font-semibold text-sky-300"
            >
              {d}
            </span>
          ))}
          {categorias.map((c) => (
            <span
              key={c}
              className="rounded-full border border-slate-600/40 bg-slate-800/60 px-2.5 py-0.5 text-xs font-semibold text-slate-300"
            >
              {c}
            </span>
          ))}
        </div>
      )}

      {accion ? (
        <div className="mt-4">
          {accion.deshabilitado ? (
            <button
              disabled
              title="Resultados disponibles próximamente"
              className="rounded-2xl border border-slate-700 bg-slate-800 px-4 py-2 text-sm font-semibold text-slate-500 opacity-60 cursor-not-allowed"
            >
              {accion.label}
            </button>
          ) : (
            <button
              onClick={() => accion.destino && (accion.publico ? navigate(accion.destino) : navigateWithRedirect(accion.destino))}
              className="rounded-2xl bg-sky-500 px-4 py-2 text-sm font-semibold text-slate-950 transition-colors hover:bg-sky-400"
            >
              {accion.label}
            </button>
          )}
        </div>
      ) : null}
    </div>
  )
}

export function PublicTorneosPage() {
  const rol = useAuthStore((s) => s.rol)

  const { data: torneos, isLoading, isError } = useQuery({
    queryKey: ['torneos-publicos'],
    queryFn: fetchTorneos,
  })

  const portalLink = (() => {
    if (rol === 'juez') return '/juez/disciplinas'
    if (rol === 'organizador') return '/organizador/torneo'
    if (rol === 'atleta') return '/atleta'
    return null
  })()

  const sorted = torneos
    ? [...torneos].sort(
        (a, b) => new Date(a.fecha_inicio).getTime() - new Date(b.fecha_inicio).getTime(),
      )
    : []

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 bg-slate-900/80 px-4 py-3">
        <div className="mx-auto flex max-w-lg items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-[0.24em] text-sky-400">
            AtaraxiaDive
          </span>
          {portalLink ? (
            <Link
              to={portalLink}
              className="rounded-2xl bg-sky-500 px-4 py-2 text-xs font-semibold text-slate-950 transition-colors hover:bg-sky-400"
            >
              Mi portal
            </Link>
          ) : (
            <Link
              to="/login"
              className="rounded-2xl border border-slate-700 bg-slate-800 px-4 py-2 text-xs font-semibold text-slate-200 transition-colors hover:bg-slate-700"
            >
              Iniciar sesión
            </Link>
          )}
        </div>
      </header>

      <main className="mx-auto max-w-lg px-4 py-6">
        <h1 className="mb-1 text-2xl font-semibold text-slate-50">Torneos de Apnea</h1>
        <p className="mb-6 text-sm text-slate-400">
          Calendario de competencias — inscripciones y resultados
        </p>

        {isLoading ? (
          <div className="rounded-3xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-300">
            Cargando torneos...
          </div>
        ) : null}

        {isError ? (
          <div className="rounded-3xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-100">
            No se pudieron cargar los torneos.
          </div>
        ) : null}

        {!isLoading && !isError && sorted.length === 0 ? (
          <div className="rounded-3xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-400">
            No hay torneos programados próximamente.
          </div>
        ) : null}

        {sorted.length > 0 ? (
          <div className="space-y-4">
            {sorted.map((torneo) => (
              <TorneoCard key={torneo.torneo_id} torneo={torneo} />
            ))}
          </div>
        ) : null}
      </main>
    </div>
  )
}
