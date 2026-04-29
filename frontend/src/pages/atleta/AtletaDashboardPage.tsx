import { useMemo, useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Link, useLocation } from 'react-router-dom'
import { ApiError, inscribirAtleta } from '../../api/registro'
import {
  fetchTorneos,
  listarDisciplinasTorneo,
  type DisciplinaCodigo,
  type TorneoDto,
} from '../../api/torneo'
import useAuthStore from '../../stores/useAuthStore'

function formatearFecha(fechaIso: string): string {
  const fecha = new Date(fechaIso)
  return new Intl.DateTimeFormat('es-AR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(fecha)
}

const DISCIPLINA_LABELS: Record<DisciplinaCodigo, string> = {
  STA: 'STA',
  DNF: 'DNF',
  DYN: 'DYN',
  DYNB: 'DBF',
  DBF: 'DBF',
  SPE_2X50: 'SPE 2x50',
  SPE_4X50: 'SPE 4x50',
  SPE_8X50: 'SPE 8x50',
  SPE_16X50: 'SPE 16x50',
}

function formatDisciplina(disciplina: DisciplinaCodigo): string {
  return DISCIPLINA_LABELS[disciplina] ?? disciplina
}

function getInscripcionError(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 409) return error.message
    if (error.status === 422) return 'Debes seleccionar al menos una disciplina'
    return error.message
  }
  if (error instanceof Error) return error.message
  return 'No se pudo completar la inscripcion'
}

interface InscripcionPanelProps {
  torneo: TorneoDto
  atletaId: string | null
}

function InscripcionPanel({ torneo, atletaId }: InscripcionPanelProps) {
  const [open, setOpen] = useState(false)
  const [selected, setSelected] = useState<DisciplinaCodigo[]>([])
  const disciplinasQuery = useQuery({
    queryKey: ['disciplinas-torneo-atleta', torneo.torneo_id],
    queryFn: async () => {
      const disciplinas = await listarDisciplinasTorneo(torneo.torneo_id)
      return disciplinas.map((item) => item.disciplina)
    },
    enabled: open,
  })
  const inscripcionMutation = useMutation({
    mutationFn: (disciplinas: DisciplinaCodigo[]) => {
      if (!atletaId) {
        throw new Error('No se pudo identificar al atleta autenticado')
      }
      return inscribirAtleta({
        atletaId,
        torneoId: torneo.torneo_id,
        disciplinas,
      })
    },
    onSuccess: () => {
      setOpen(false)
      setSelected([])
    },
  })

  function toggleDisciplina(disciplina: DisciplinaCodigo) {
    setSelected((current) =>
      current.includes(disciplina)
        ? current.filter((item) => item !== disciplina)
        : [...current, disciplina],
    )
  }

  return (
    <div className="mt-5 rounded-[1.25rem] border border-teal-200/80 bg-teal-50/60 p-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal-700">
            Inscripcion
          </p>
          <p className="mt-1 text-sm text-stone-600">
            Selecciona las disciplinas para inscribirte en este torneo.
          </p>
        </div>
        <button
          type="button"
          onClick={() => setOpen((current) => !current)}
          className="rounded-lg bg-teal-700 px-4 py-2 text-sm font-semibold text-white"
        >
          {open ? 'Cancelar' : 'Inscribirme'}
        </button>
      </div>

      {inscripcionMutation.isSuccess ? (
        <div className="mt-4 rounded-xl border border-emerald-300 bg-emerald-50 p-3 text-sm text-emerald-900">
          Inscripcion confirmada.
        </div>
      ) : null}

      {open ? (
        <div className="mt-4 space-y-4">
          {disciplinasQuery.isLoading ? (
            <div className="rounded-xl border border-stone-200 bg-white p-3 text-sm text-stone-600">
              Cargando disciplinas...
            </div>
          ) : null}

          {disciplinasQuery.isError ? (
            <div className="rounded-xl border border-red-300 bg-red-50 p-3 text-sm text-red-900">
              No se pudieron cargar las disciplinas del torneo.
            </div>
          ) : null}

          {!disciplinasQuery.isLoading &&
          !disciplinasQuery.isError &&
          (disciplinasQuery.data?.length ?? 0) === 0 ? (
            <div className="rounded-xl border border-stone-200 bg-white p-3 text-sm text-stone-600">
              Este torneo no tiene disciplinas configuradas.
            </div>
          ) : null}

          {!disciplinasQuery.isLoading &&
          !disciplinasQuery.isError &&
          (disciplinasQuery.data?.length ?? 0) > 0 ? (
            <>
              <div className="grid gap-2 sm:grid-cols-2">
                {disciplinasQuery.data?.map((disciplina) => {
                  const checked = selected.includes(disciplina)
                  return (
                    <label
                      key={disciplina}
                      className="flex items-center gap-3 rounded-xl border border-stone-200 bg-white px-4 py-3 text-sm text-stone-800"
                    >
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => toggleDisciplina(disciplina)}
                        className="h-4 w-4 rounded border-stone-300 text-teal-700 focus:ring-teal-600"
                      />
                      <span className="font-medium">{formatDisciplina(disciplina)}</span>
                    </label>
                  )
                })}
              </div>

              {inscripcionMutation.isError ? (
                <div className="rounded-xl border border-red-300 bg-red-50 p-3 text-sm text-red-900">
                  {getInscripcionError(inscripcionMutation.error)}
                </div>
              ) : null}

              <button
                type="button"
                onClick={() => inscripcionMutation.mutate(selected)}
                disabled={inscripcionMutation.isPending || !atletaId}
                className="rounded-lg bg-stone-900 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-stone-400"
              >
                {inscripcionMutation.isPending ? 'Confirmando...' : 'Confirmar inscripcion'}
              </button>
            </>
          ) : null}
        </div>
      ) : null}
    </div>
  )
}

export function AtletaDashboardPage() {
  const location = useLocation()
  const email = useAuthStore((s) => s.email)
  const atletaId = useAuthStore((s) => s.userId)
  const logout = useAuthStore((s) => s.logout)
  const torneosQuery = useQuery({
    queryKey: ['torneos-atleta'],
    queryFn: fetchTorneos,
  })
  const torneosDisponibles = useMemo(
    () =>
      (torneosQuery.data ?? []).filter((torneo) => torneo.estado === 'INSCRIPCION_ABIERTA'),
    [torneosQuery.data],
  )

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,#daf1f7_0%,#d5eee4_22%,#f6f2e8_60%,#efe6d4_100%)] text-stone-900">
      <div className="mx-auto max-w-6xl px-5 py-6 sm:px-8 lg:px-10">
        <header className="rounded-[2rem] border border-teal-200/70 bg-white/80 p-6 shadow-[0_20px_60px_rgba(45,94,99,0.12)] backdrop-blur">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div className="max-w-3xl">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-teal-700">
                Atleta
              </p>
              <h1 className="mt-2 text-3xl font-semibold tracking-tight text-stone-900">
                Mi portal
              </h1>
              <p className="mt-2 text-sm text-stone-600">
                Perfil personal y torneos con inscripcion abierta para proximas competencias.
              </p>
            </div>
            <button
              type="button"
              onClick={logout}
              className="rounded-lg bg-stone-900 px-4 py-2 text-sm font-semibold text-stone-50"
            >
              Cerrar sesion
            </button>
          </div>
        </header>

        {location.state && (location.state as { passwordUpdated?: boolean }).passwordUpdated ? (
          <div className="mt-4 rounded-[1.5rem] border border-emerald-300 bg-emerald-50 px-5 py-4 text-sm text-emerald-900">
            Contrasena actualizada correctamente.
          </div>
        ) : null}

        <main className="mt-6 grid gap-4 lg:grid-cols-[320px_minmax(0,1fr)]">
          <section className="rounded-[2rem] border border-teal-200/70 bg-white/85 p-5 shadow-[0_20px_60px_rgba(45,94,99,0.08)]">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal-700">
              Mi perfil
            </p>
            <div className="mt-5 space-y-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
                  Email
                </p>
                <p className="mt-1 text-base font-semibold text-stone-900">
                  {email ?? 'Sin email disponible'}
                </p>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
                  Rol
                </p>
                <p className="mt-1 text-base font-semibold text-stone-900">Atleta</p>
              </div>
              <Link
                to="/cambiar-password"
                className="inline-flex rounded-lg border border-teal-700 px-4 py-2 text-sm font-semibold text-teal-900"
              >
                Cambiar contrasena
              </Link>
            </div>
          </section>

          <section className="rounded-[2rem] border border-teal-200/70 bg-white/85 p-5 shadow-[0_20px_60px_rgba(45,94,99,0.08)]">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal-700">
                  Torneos disponibles
                </p>
                <h2 className="mt-1 text-xl font-semibold text-stone-900">
                  Inscripcion abierta
                </h2>
              </div>
              <p className="text-sm text-stone-600">
                {torneosDisponibles.length} torneos habilitados
              </p>
            </div>

            {torneosQuery.isLoading ? (
              <div className="mt-5 rounded-xl border border-stone-200 bg-stone-50 p-4 text-sm text-stone-600">
                Cargando torneos disponibles...
              </div>
            ) : null}

            {torneosQuery.isError ? (
              <div className="mt-5 rounded-xl border border-red-300 bg-red-50 p-4 text-sm text-red-900">
                No se pudieron cargar los torneos.
              </div>
            ) : null}

            {!torneosQuery.isLoading && !torneosQuery.isError && torneosDisponibles.length === 0 ? (
              <div className="mt-5 rounded-xl border border-stone-200 bg-stone-50 p-4 text-sm text-stone-600">
                No hay torneos disponibles en este momento
              </div>
            ) : null}

            {!torneosQuery.isLoading && !torneosQuery.isError && torneosDisponibles.length > 0 ? (
              <div className="mt-5 grid gap-4">
                {torneosDisponibles.map((torneo) => (
                  <article
                    key={torneo.torneo_id}
                    className="rounded-[1.5rem] border border-stone-200 bg-[linear-gradient(135deg,#ffffff_0%,#f3fbf7_100%)] p-5"
                  >
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
                      Torneo
                    </p>
                    <h3 className="mt-2 text-lg font-semibold text-stone-900">{torneo.nombre}</h3>
                    <p className="mt-3 text-sm text-stone-600">
                      {torneo.sede.nombre}, {torneo.sede.ciudad}, {torneo.sede.pais}
                    </p>
                    <p className="mt-2 text-sm text-stone-600">
                      {formatearFecha(torneo.fecha_inicio)} al {formatearFecha(torneo.fecha_fin)}
                    </p>
                    <InscripcionPanel torneo={torneo} atletaId={atletaId} />
                  </article>
                ))}
              </div>
            ) : null}
          </section>
        </main>
      </div>
    </div>
  )
}
