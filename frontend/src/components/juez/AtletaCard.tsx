import { formatMarca } from '../../utils/marca'

interface AtletaCardProps {
  nombreAtleta: string
  apDeclarado: string
  unidad: string
  andarivel: number
  otProgramado: string
  estado: string
}

function formatOt(iso: string) {
  const date = new Date(iso)
  return Number.isNaN(date.getTime())
    ? iso
    : date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export function AtletaCard({
  nombreAtleta,
  apDeclarado,
  unidad,
  andarivel,
  otProgramado,
  estado,
}: AtletaCardProps) {
  const showEstado = estado !== 'AnunciadaAP'

  return (
    <section className="rounded-[2rem] border border-slate-800 bg-slate-900/80 p-5 shadow-[0_24px_80px_-50px_rgba(34,211,238,0.7)]">
      {showEstado ? (
        <p className="text-center text-xs font-semibold uppercase tracking-[0.24em] text-cyan-300">
          {estado}
        </p>
      ) : null}
      <h2 className="mt-3 text-2xl font-semibold text-white">{nombreAtleta}</h2>
      <div className="mt-4 space-y-3 text-sm text-slate-300">
        <div className="rounded-2xl bg-slate-950/70 p-3">
          <p className="text-[11px] uppercase tracking-[0.18em] text-slate-500">
            Performance anunciada
          </p>
          <p className="mt-2 text-lg font-semibold text-slate-50">
            {formatMarca(apDeclarado, unidad)}
          </p>
        </div>
        <div className="rounded-2xl bg-slate-950/70 p-3">
          <p className="text-[11px] uppercase tracking-[0.18em] text-slate-500">Andarivel</p>
          <p className="mt-2 text-lg font-semibold text-slate-50">{andarivel}</p>
        </div>
        <div className="rounded-2xl bg-slate-950/70 p-3">
          <p className="text-[11px] uppercase tracking-[0.18em] text-slate-500">OT</p>
          <p className="mt-2 text-lg font-semibold text-slate-50">{formatOt(otProgramado)}</p>
        </div>
      </div>
    </section>
  )
}
