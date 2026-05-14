interface GrillaRowProps {
  posicion: number
  nombre: string
  ot: string
  andarivel: number
  isSelf: boolean
}

export function GrillaRow({
  posicion,
  nombre,
  ot,
  andarivel,
  isSelf,
}: GrillaRowProps) {
  return (
    <tr className={isSelf ? 'bg-sky-500/10' : undefined}>
      <td className="py-2 pr-3 text-center text-xs font-semibold text-slate-400">{posicion}</td>
      <td className="py-2 pr-3">
        <div className="flex items-center gap-1.5">
          <span className={`text-sm font-semibold ${isSelf ? 'text-sky-300' : 'text-white'}`}>
            {nombre}
          </span>
          {isSelf ? (
            <span className="rounded-full border border-sky-400/40 bg-sky-400/10 px-1.5 py-0.5 text-[10px] font-semibold text-sky-300">
              Vos
            </span>
          ) : null}
        </div>
      </td>
      <td className="py-2 pr-3 text-center text-sm font-semibold text-slate-200">{ot}</td>
      <td className="py-2 text-center text-sm text-slate-400">{andarivel}</td>
    </tr>
  )
}
