"""Query y Handler para ObtenerRankingProvisional — resultados en tiempo real."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from shared.domain.ports.event_store_port import EventStorePort
from shared.domain.value_objects.disciplina import Disciplina
from resultados.application.queries.obtener_ranking import RankingCategoriaDTO, RankingEntradaDTO
from resultados.domain.ports.resultados_competencia_port import AtletaCategoriaPort

_TARJETAS_INVALIDAS = {"Roja"}


@dataclass(frozen=True)
class ObtenerRankingProvisionalQuery:
    """Query para obtener el ranking provisional (en tiempo real) de una disciplina."""

    competencia_id: UUID
    disciplina: Disciplina


class ObtenerRankingProvisionalHandler:
    """Handler que construye un ranking provisional desde los eventos de BC Competencia.

    Lee los streams `performance-{competencia_id}-*` de competencia.db e incluye
    todas las performances que ya tienen RP registrado (con o sin tarjeta asignada)
    y las que son DNS.  Devuelve los mismos DTOs que ObtenerRankingHandler para
    que el router los formatee de la misma manera.

    Args:
        competencia_store: Event Store del BC Competencia.
        atleta_categoria_port: ACL para resolver categoría por atleta_id.
    """

    def __init__(
        self,
        competencia_store: EventStorePort,
        atleta_categoria_port: AtletaCategoriaPort,
    ) -> None:
        self._competencia_store = competencia_store
        self._atleta_categoria_port = atleta_categoria_port

    async def handle(self, query: ObtenerRankingProvisionalQuery) -> list[RankingCategoriaDTO]:
        """Retorna las entradas del ranking provisional agrupadas por categoría.

        Returns:
            Lista de RankingCategoriaDTO ordenada por categoría.
            Lista vacía si ningún atleta completó su performance.
        """
        prefix = f"performance-{query.competencia_id}-"
        all_streams = await self._competencia_store.load_all_streams_with_prefix(prefix)

        estados = []
        for stream in all_streams:
            estado = _extraer_estado_provisional(stream, query.disciplina)
            if estado is not None:
                estados.append(estado)

        if not estados:
            return []

        for estado in estados:
            try:
                categoria = await self._atleta_categoria_port.get_categoria(
                    UUID(estado["atleta_id"])
                )
                estado["categoria"] = categoria.value
            except Exception:
                estado["categoria"] = "SENIOR_MASCULINO"

        return _construir_grupos(estados)


def _extraer_estado_provisional(
    stream_events: list[dict],
    disciplina_buscada: Disciplina,
) -> dict | None:
    if not stream_events:
        return None

    estado: dict = {
        "atleta_id": None,
        "disciplina": None,
        "rp": None,
        "unidad": None,
        "tarjeta": None,
        "motivo_dq": None,
        "es_dns": False,
        "tiene_rp": False,
    }

    for event in stream_events:
        payload = event["payload"]
        if isinstance(payload, str):
            import json

            payload = json.loads(payload)
        _aplicar(estado, event["event_type"], payload)

    if estado["disciplina"] != disciplina_buscada.value:
        return None
    if not estado["tiene_rp"] and not estado["es_dns"]:
        return None
    if estado["atleta_id"] is None:
        return None

    return estado


def _aplicar(estado: dict, event_type: str, payload: dict) -> None:
    if event_type == "APRegistrado":
        estado["atleta_id"] = payload.get("participante_id")
        estado["disciplina"] = payload.get("disciplina")
        estado["unidad"] = payload.get("unidad")
    elif event_type == "ResultadoRegistrado":
        rp_raw = payload.get("valor_rp") or payload.get("rp")
        if rp_raw is not None:
            estado["rp"] = str(Decimal(str(rp_raw)))
        estado["unidad"] = payload.get("unidad", estado["unidad"])
        estado["tiene_rp"] = True
    elif event_type == "TarjetaAsignada":
        estado["tarjeta"] = payload.get("tipo")
        estado["motivo_dq"] = payload.get("motivo_dq_codigo")
        rp_final = payload.get("rp_penalizado") or payload.get("rp_medido")
        if rp_final is not None:
            estado["rp"] = str(Decimal(str(rp_final)))
    elif event_type == "RevisionResuelta":
        estado["tarjeta"] = payload.get("tipo")
        estado["motivo_dq"] = payload.get("motivo_dq_codigo")
        rp_final = payload.get("rp_penalizado") or payload.get("rp_medido")
        if rp_final is not None:
            estado["rp"] = str(Decimal(str(rp_final)))
        estado["tiene_rp"] = rp_final is not None or estado["tiene_rp"]
    elif event_type == "DNSRegistrado":
        estado["es_dns"] = True
        estado["atleta_id"] = payload.get("participante_id")
        estado["disciplina"] = payload.get("disciplina")


def _construir_grupos(estados: list[dict]) -> list[RankingCategoriaDTO]:
    por_categoria: dict[str, list[dict]] = defaultdict(list)
    for e in estados:
        por_categoria[e["categoria"]].append(e)

    grupos: list[RankingCategoriaDTO] = []
    for categoria in sorted(por_categoria):
        entradas = _rankear_categoria(por_categoria[categoria])
        grupos.append(RankingCategoriaDTO(categoria=categoria, entradas=entradas))
    return grupos


def _rankear_categoria(estados: list[dict]) -> list[RankingEntradaDTO]:
    validos = [e for e in estados if not e["es_dns"] and e["tarjeta"] not in _TARJETAS_INVALIDAS]
    invalidos = [e for e in estados if e["es_dns"] or e["tarjeta"] in _TARJETAS_INVALIDAS]

    def _sort_key(e: dict) -> Decimal:
        if e["rp"] is None:
            return Decimal(0)
        return Decimal(e["rp"])

    validos_ordenados = sorted(validos, key=_sort_key, reverse=True)

    entradas: list[RankingEntradaDTO] = []
    posicion = 1
    for i, e in enumerate(validos_ordenados):
        if i > 0 and e["rp"] == validos_ordenados[i - 1]["rp"]:
            pos = entradas[-1].posicion
        else:
            pos = posicion
        entradas.append(
            RankingEntradaDTO(
                posicion=pos,
                atleta_id=e["atleta_id"],
                rp=e["rp"],
                unidad=e["unidad"],
                tarjeta=e["tarjeta"],
                es_dns=False,
                en_podio=pos <= 3,
                puntos="0.00",
                motivo_dq=e.get("motivo_dq"),
            )
        )
        posicion = len(entradas) + 1

    for e in invalidos:
        entradas.append(
            RankingEntradaDTO(
                posicion=posicion,
                atleta_id=e["atleta_id"],
                rp=None,
                unidad=None,
                tarjeta=e["tarjeta"],
                es_dns=e["es_dns"],
                en_podio=False,
                puntos="0.00",
                motivo_dq=e.get("motivo_dq"),
            )
        )
        posicion += 1

    return entradas
