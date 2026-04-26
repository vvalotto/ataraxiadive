import { useMutation, useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { fetchTorneo, listarDisciplinasTorneo } from '../../api/torneo'
import { fetchAtletaMe, inscribirAtleta } from '../../api/registro'
import useAuthStore from '../../stores/useAuthStore'
import { AtletaShell } from '../../components/atleta/AtletaShell'
import { ApiError } from '../../api/registro'
import { formatCategoria, formatDisciplina, formatFecha } from './portalData'
import type { DisciplinaCodigo } from '../../api/torneo'

type WizardStep = 1 | 2 | 3

function getInscripcionError(error: unknown): string {
  if (error instanceof ApiError) return error.message
  if (error instanceof Error) return error.message
  return 'No se pudo completar la inscripción.'
}

export function AtletaInscripcionPage() {
  const { torneoId } = useParams<{ torneoId: string }>()
  const atletaId = useAuthStore((state) => state.userId)
  const email = useAuthStore((state) => state.email)
  const navigate = useNavigate()
  const [step, setStep] = useState<WizardStep>(1)
  const [nombreCompleto, setNombreCompleto] = useState('')
  const [fechaNacimiento, setFechaNacimiento] = useState('')
  const [genero, setGenero] = useState('F')
  const [documentoTipo, setDocumentoTipo] = useState('DNI')
  const [documentoNumero, setDocumentoNumero] = useState('')
  const [telefono, setTelefono] = useState('')
  const [categoria, setCategoria] = useState('')
  const [brevet, setBrevet] = useState('')
  const [disciplinasSeleccionadas, setDisciplinasSeleccionadas] = useState<string[]>([])
  const [certificado, setCertificado] = useState<File | null>(null)
  const [comprobante, setComprobante] = useState<File | null>(null)
  const [validationError, setValidationError] = useState('')

  const query = useQuery({
    queryKey: ['atleta-inscripcion-form', torneoId, atletaId],
    queryFn: async () => {
      const [torneo, disciplinas, atleta] = await Promise.all([
        fetchTorneo(torneoId ?? ''),
        listarDisciplinasTorneo(torneoId ?? ''),
        fetchAtletaMe(),
      ])
      return { torneo, disciplinas, atleta }
    },
    enabled: Boolean(torneoId && atletaId),
  })

  const mutation = useMutation({
    mutationFn: async () => {
      const registroAtletaId = query.data?.atleta.atleta_id
      if (!registroAtletaId || !torneoId) {
        throw new Error('No se pudo identificar al atleta o torneo para inscribirse.')
      }
      return inscribirAtleta({
        atletaId: registroAtletaId,
        torneoId,
        disciplinas: disciplinasSeleccionadas as DisciplinaCodigo[],
      })
    },
    onSuccess: () => {
      navigate('/atleta/mis-inscripciones')
    },
  })

  const atleta = query.data?.atleta
  const nombreCompletoValue = nombreCompleto || (atleta ? `${atleta.nombre} ${atleta.apellido}`.trim() : '')
  const fechaNacimientoValue = fechaNacimiento || atleta?.fecha_nacimiento || ''
  const categoriaValue = categoria || atleta?.categoria || ''
  const brevetValue = brevet || atleta?.brevet || ''

  function toggleDisciplina(disciplina: string) {
    setDisciplinasSeleccionadas((current) =>
      current.includes(disciplina)
        ? current.filter((item) => item !== disciplina)
        : [...current, disciplina],
    )
  }

  function nextStep() {
    if (step === 1) {
      if (!nombreCompletoValue || !fechaNacimientoValue || !documentoNumero || !telefono) {
        setValidationError('Completá todos los datos personales obligatorios.')
        return
      }
    }
    if (step === 2) {
      if (disciplinasSeleccionadas.length === 0 || !categoriaValue) {
        setValidationError('Seleccioná al menos una disciplina y confirmá la categoría.')
        return
      }
    }
    setValidationError('')
    setStep((current) => Math.min(3, current + 1) as WizardStep)
  }

  function prevStep() {
    setValidationError('')
    setStep((current) => Math.max(1, current - 1) as WizardStep)
  }

  async function submit() {
    if (!certificado || !comprobante) {
      setValidationError('El certificado médico y el comprobante de pago son obligatorios.')
      return
    }
    setValidationError('')
    await mutation.mutateAsync()
  }

  return (
    <AtletaShell title="Inscribirme" subtitle="Completá el wizard de 3 pasos para enviar tu inscripción." showBack>
      {query.isLoading ? (
        <div className="rounded-3xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-300">
          Cargando formulario de inscripción...
        </div>
      ) : null}

      {query.isError ? (
        <div className="rounded-3xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-100">
          No se pudo preparar el formulario de inscripción.
        </div>
      ) : null}

      {query.data ? (
        <div className="space-y-4">
          <section className="rounded-[1.75rem] border border-slate-800 bg-slate-900 p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-sky-400">
              Paso {step} de 3
            </p>
            <h2 className="mt-1 text-lg font-semibold text-white">{query.data.torneo.nombre}</h2>
            <p className="mt-1 text-sm text-slate-400">
              {formatFecha(query.data.torneo.fecha_inicio)} al {formatFecha(query.data.torneo.fecha_fin)}
            </p>
            <div className="mt-4 grid grid-cols-3 gap-2">
              {[1, 2, 3].map((item) => (
                <div
                  key={item}
                  className={[
                    'h-2 rounded-full',
                    item <= step ? 'bg-sky-400' : 'bg-slate-800',
                  ].join(' ')}
                />
              ))}
            </div>
          </section>

          {step === 1 ? (
            <section className="space-y-3 rounded-[1.75rem] border border-slate-800 bg-slate-900 p-4">
              <p className="text-sm font-semibold text-white">1. Datos personales</p>
              <label className="block text-sm text-slate-300">
                Correo
                <input
                  value={email ?? ''}
                  readOnly
                  className="mt-2 w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-400"
                />
              </label>
              <label className="block text-sm text-slate-300">
                Nombre y apellido *
                <input
                  value={nombreCompletoValue}
                  onChange={(event) => setNombreCompleto(event.target.value)}
                  className="mt-2 w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100"
                />
              </label>
              <label className="block text-sm text-slate-300">
                Fecha de nacimiento *
                <input
                  type="date"
                  value={fechaNacimientoValue}
                  onChange={(event) => setFechaNacimiento(event.target.value)}
                  className="mt-2 w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100"
                />
              </label>
              <label className="block text-sm text-slate-300">
                Género *
                <select
                  value={genero}
                  onChange={(event) => setGenero(event.target.value)}
                  className="mt-2 w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100"
                >
                  <option value="F">Femenino</option>
                  <option value="M">Masculino</option>
                  <option value="X">Otro</option>
                </select>
              </label>
              <div className="grid grid-cols-[110px_minmax(0,1fr)] gap-3">
                <label className="block text-sm text-slate-300">
                  Tipo
                  <select
                    value={documentoTipo}
                    onChange={(event) => setDocumentoTipo(event.target.value)}
                    className="mt-2 w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100"
                  >
                    <option value="DNI">DNI</option>
                    <option value="PAS">Pasaporte</option>
                  </select>
                </label>
                <label className="block text-sm text-slate-300">
                  Documento *
                  <input
                    value={documentoNumero}
                    onChange={(event) => setDocumentoNumero(event.target.value)}
                    className="mt-2 w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100"
                  />
                </label>
              </div>
              <label className="block text-sm text-slate-300">
                Teléfono *
                <input
                  value={telefono}
                  onChange={(event) => setTelefono(event.target.value)}
                  className="mt-2 w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100"
                />
              </label>
            </section>
          ) : null}

          {step === 2 ? (
            <section className="space-y-3 rounded-[1.75rem] border border-slate-800 bg-slate-900 p-4">
              <p className="text-sm font-semibold text-white">2. Datos de competencia</p>
              <p className="text-sm text-slate-400">
                Seleccioná disciplinas y revisá tu categoría antes de enviar.
              </p>
              <div className="grid gap-3">
                {query.data.disciplinas.map((disciplina) => {
                  const selected = disciplinasSeleccionadas.includes(disciplina.disciplina)
                  return (
                    <button
                      key={disciplina.disciplina}
                      type="button"
                      onClick={() => toggleDisciplina(disciplina.disciplina)}
                      className={[
                        'rounded-3xl border px-4 py-4 text-left text-sm font-semibold transition-colors',
                        selected
                          ? 'border-sky-400 bg-sky-500/10 text-sky-200'
                          : 'border-slate-800 bg-slate-950/70 text-slate-200',
                      ].join(' ')}
                    >
                      {formatDisciplina(disciplina.disciplina)}
                    </button>
                  )
                })}
              </div>
              <label className="block text-sm text-slate-300">
                Categoría *
                {categoriaValue === 'MASTER_MASCULINO' || categoriaValue === 'MASTER_FEMENINO' ? (
                  <select
                    value={categoria || categoriaValue}
                    onChange={(event) => setCategoria(event.target.value)}
                    className="mt-2 w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100"
                  >
                    <option value={categoriaValue}>{formatCategoria(categoriaValue)}</option>
                    <option value={categoriaValue === 'MASTER_MASCULINO' ? 'SENIOR_MASCULINO' : 'SENIOR_FEMENINO'}>
                      {formatCategoria(categoriaValue === 'MASTER_MASCULINO' ? 'SENIOR_MASCULINO' : 'SENIOR_FEMENINO')}
                    </option>
                  </select>
                ) : (
                  <input
                    value={formatCategoria(categoriaValue)}
                    readOnly
                    className="mt-2 w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-400"
                  />
                )}
              </label>
              <label className="block text-sm text-slate-300">
                Nº Brevet FAAS
                <input
                  value={brevetValue}
                  onChange={(event) => setBrevet(event.target.value)}
                  className="mt-2 w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100"
                />
              </label>
            </section>
          ) : null}

          {step === 3 ? (
            <section className="space-y-3 rounded-[1.75rem] border border-slate-800 bg-slate-900 p-4">
              <p className="text-sm font-semibold text-white">3. Requisitos</p>
              <div className="rounded-3xl border border-amber-400/30 bg-amber-400/10 p-4 text-sm text-amber-100">
                La inscripción quedará pendiente de verificación hasta revisar la documentación obligatoria.
              </div>
              <label className="block rounded-3xl border border-slate-800 bg-slate-950/70 p-4 text-sm text-slate-300">
                Certificado médico *
                <input
                  type="file"
                  onChange={(event) => setCertificado(event.target.files?.[0] ?? null)}
                  className="mt-3 block w-full text-sm text-slate-300"
                />
                <p className="mt-2 text-xs text-slate-500">PDF o imagen. Máximo 10 MB.</p>
              </label>
              <label className="block rounded-3xl border border-slate-800 bg-slate-950/70 p-4 text-sm text-slate-300">
                Comprobante de pago *
                <input
                  type="file"
                  onChange={(event) => setComprobante(event.target.files?.[0] ?? null)}
                  className="mt-3 block w-full text-sm text-slate-300"
                />
                <p className="mt-2 text-xs text-slate-500">PDF o imagen. Máximo 10 MB.</p>
              </label>
            </section>
          ) : null}

          {validationError ? (
            <div className="rounded-3xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-100">
              {validationError}
            </div>
          ) : null}

          {mutation.isError ? (
            <div className="rounded-3xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-100">
              {getInscripcionError(mutation.error)}
            </div>
          ) : null}

          <div className="flex gap-3">
            {step > 1 ? (
              <button
                type="button"
                onClick={prevStep}
                className="flex-1 rounded-2xl border border-slate-700 px-4 py-3 text-sm font-semibold text-slate-200"
              >
                ← Anterior
              </button>
            ) : (
              <button
                type="button"
                onClick={() => navigate(-1)}
                className="flex-1 rounded-2xl border border-slate-700 px-4 py-3 text-sm font-semibold text-slate-200"
              >
                Cancelar
              </button>
            )}

            {step < 3 ? (
              <button
                type="button"
                onClick={nextStep}
                className="flex-1 rounded-2xl bg-sky-500 px-4 py-3 text-sm font-semibold uppercase tracking-[0.16em] text-slate-950"
              >
                Siguiente →
              </button>
            ) : (
              <button
                type="button"
                onClick={submit}
                disabled={mutation.isPending}
                className="flex-1 rounded-2xl bg-sky-500 px-4 py-3 text-sm font-semibold uppercase tracking-[0.16em] text-slate-950 disabled:opacity-60"
              >
                {mutation.isPending ? 'Enviando...' : 'Enviar inscripción'}
              </button>
            )}
          </div>
        </div>
      ) : null}
    </AtletaShell>
  )
}
