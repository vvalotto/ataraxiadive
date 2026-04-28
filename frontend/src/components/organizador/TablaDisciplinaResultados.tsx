import { useMemo } from 'react'
import type { GrillaAtletaDto } from '../../api/competencia'
import type { InscriptoDetalleDto } from '../../api/registro'
import type { RankingCompetenciaDto } from '../../api/resultados'
import { FilaResultado, type FilaResultadoData } from './FilaResultado'

interface TablaDisciplinaResultadosProps {
  grilla: GrillaAtletaDto[]
  ranking: RankingCompetenciaDto | null
  inscriptos: InscriptoDetalleDto[]
}

function derivarGenero(categoria: string): 'M' | 'F' | '?' {
  const partes = categoria.split('_')
  const sufijo = partes[partes.length - 1]
  if (sufijo === 'MASCULINO') return 'M'
  if (sufijo === 'FEMENINO') return 'F'
  return '?'
}

function derivarCategoriaCorta(categoria: string): string {
  return categoria.split('_')[0] ?? categoria
}

function formatearLinea(andarivel: number): string {
  return andarivel === 1 ? 'A' : andarivel === 2 ? 'B' : String(andarivel)
}

export function TablaDisciplinaResultados({
  grilla,
  ranking,
  inscriptos,
}: TablaDisciplinaResultadosProps) {
  const filas = useMemo<FilaResultadoData[]>(() => {
    const rankingPorAtleta = new Map<
      string,
      { rp: string | null; unidad: string | null; tarjeta: string | null; puntos: string | null; categoria: string }
    >()

    if (ranking) {
      for (const grupo of ranking.rankings) {
        for (const entrada of grupo.entradas) {
          rankingPorAtleta.set(entrada.atleta_id, {
            rp: entrada.rp,
            unidad: entrada.unidad,
            tarjeta: entrada.es_dns ? 'DNS' : (entrada.tarjeta ?? null),
            puntos: entrada.puntos ?? null,
            categoria: grupo.categoria,
          })
        }
      }
    }

    const inscriptosPorAtleta = new Map<string, InscriptoDetalleDto>()
    for (const inscripto of inscriptos) {
      inscriptosPorAtleta.set(inscripto.atleta_id, inscripto)
    }

    return grilla
      .slice()
      .sort((a, b) => a.posicion - b.posicion)
      .map((atleta): FilaResultadoData => {
        const rankData = rankingPorAtleta.get(atleta.atleta_id)
        const inscriptoData = inscriptosPorAtleta.get(atleta.atleta_id)

        const categoriaRaw =
          rankData?.categoria ?? inscriptoData?.categoria ?? ''

        return {
          posicion_ot: atleta.posicion,
          atleta_id: atleta.atleta_id,
          nombre: atleta.nombre_atleta,
          genero: derivarGenero(categoriaRaw),
          categoria_corta: derivarCategoriaCorta(categoriaRaw),
          club: inscriptoData?.club ?? '',
          ap: `${atleta.ap_declarado} ${atleta.unidad}`.trim(),
          ot: atleta.ot_programado,
          linea: formatearLinea(atleta.andarivel),
          rp: rankData?.rp ?? null,
          unidad: rankData?.unidad ?? atleta.unidad,
          tarjeta: rankData?.tarjeta ?? null,
          puntos: rankData?.puntos ?? null,
        }
      })
  }, [grilla, ranking, inscriptos])

  if (filas.length === 0) {
    return (
      <p className="py-6 text-center text-sm text-slate-400">
        No hay atletas en la grilla de esta disciplina.
      </p>
    )
  }

  return (
    <div className="overflow-x-auto rounded-[1.5rem] border border-slate-800 bg-slate-950/40">
      <table className="w-full min-w-[900px] border-collapse text-sm">
        <thead>
          <tr className="border-b border-slate-700 bg-slate-950/70 text-left text-xs font-semibold uppercase tracking-wide text-slate-400">
            <th className="px-3 py-2 text-center">#OT</th>
            <th className="px-3 py-2">Nombre</th>
            <th className="px-3 py-2 text-center">Gén.</th>
            <th className="px-3 py-2">Categoría</th>
            <th className="px-3 py-2">Club</th>
            <th className="px-3 py-2">AP</th>
            <th className="px-3 py-2">OT</th>
            <th className="px-3 py-2 text-center">Línea</th>
            <th className="px-3 py-2">RP</th>
            <th className="px-3 py-2">Tarjeta</th>
            <th className="px-3 py-2 text-right">Pts FAAS</th>
          </tr>
        </thead>
        <tbody className="bg-slate-900/40">
          {filas.map((fila) => (
            <FilaResultado key={fila.atleta_id} fila={fila} />
          ))}
        </tbody>
      </table>
    </div>
  )
}
