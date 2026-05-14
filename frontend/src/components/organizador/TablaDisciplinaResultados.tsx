import { useMemo } from 'react'
import type { GrillaAtletaDto } from '../../api/competencia'
import type { InscriptoDetalleDto } from '../../api/registro'
import type { RankingCompetenciaDto } from '../../api/resultados'
import { formatMarca } from '../../utils/marca'
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

function formatearAndarivel(andarivel: number | null | undefined): string {
  if (!andarivel) return '—'
  return String(andarivel)
}

export function TablaDisciplinaResultados({
  grilla,
  ranking,
  inscriptos,
}: TablaDisciplinaResultadosProps) {
  const filas = useMemo<FilaResultadoData[]>(() => {
    const rankingPorAtleta = new Map<
      string,
      { rp: string | null; unidad: string | null; tarjeta: string | null; categoria: string; motivo_dq: string | null; penalizaciones: string[]; rp_medido: string | null }
    >()

    if (ranking) {
      for (const grupo of ranking.rankings) {
        for (const entrada of grupo.entradas) {
          rankingPorAtleta.set(entrada.atleta_id, {
            rp: entrada.rp,
            unidad: entrada.unidad,
            tarjeta: entrada.es_dns ? 'DNS' : (entrada.tarjeta ?? null),
            categoria: grupo.categoria,
            motivo_dq: entrada.motivo_dq ?? null,
            penalizaciones: entrada.penalizaciones ?? [],
            rp_medido: entrada.rp_medido ?? null,
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
          ap: formatMarca(atleta.ap_declarado, atleta.unidad),
          ot: new Date(atleta.ot_programado).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false }),
          linea: formatearAndarivel(atleta.andarivel),
          rp: rankData?.rp ?? null,
          unidad: rankData?.unidad ?? atleta.unidad,
          tarjeta: rankData?.tarjeta ?? null,
          motivo_dq: rankData?.motivo_dq ?? atleta.motivo_dq ?? null,
          penalizaciones: rankData?.penalizaciones ?? atleta.penalizaciones ?? [],
          rp_medido: rankData?.rp_medido ?? null,
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
            <th className="px-3 py-2 text-center">Anuncio</th>
            <th className="px-3 py-2 text-center">OT</th>
            <th className="px-3 py-2 text-center">Línea</th>
            <th className="px-3 py-2 text-center">Performance</th>
            <th className="px-3 py-2 text-center">Tarjeta</th>
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
