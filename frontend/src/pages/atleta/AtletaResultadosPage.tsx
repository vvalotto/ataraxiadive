import { AtletaShell } from '../../components/atleta/AtletaShell'

export function AtletaResultadosPage() {
  return (
    <AtletaShell title="Mis resultados" subtitle="Resultados publicados y ranking por disciplina.">
      <div className="rounded-[1.75rem] border border-slate-800 bg-slate-900 p-5">
        <p className="text-sm font-semibold text-white">Resultados aún no publicados</p>
        <p className="mt-2 text-sm text-slate-400">
          Esta vista queda preparada dentro del shell UX del atleta. Los resultados aparecerán cuando la organización los publique.
        </p>
      </div>
    </AtletaShell>
  )
}
