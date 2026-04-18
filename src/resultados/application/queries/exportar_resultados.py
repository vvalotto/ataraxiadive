"""Query y Handler para ExportarResultados — US-4.6.4."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal
import json
from uuid import UUID

from competencia.infrastructure.repositories.sqlite_competencias_por_torneo import (
    SQLiteCompetenciasPorTorneo,
)
from resultados.application.queries.obtener_overall import (
    ObtenerOverallHandler,
    ObtenerOverallQuery,
)
from resultados.application.queries.obtener_ranking import (
    ObtenerRankingHandler,
    ObtenerRankingQuery,
)
from resultados.domain.aggregates.ranking_competencia import RankingCompetencia
from resultados.domain.exceptions import ResultadosIncompletos, TorneoNoEncontrado
from resultados.infrastructure.repositories.atleta_info_adapter import (
    AtletaInfo,
    AtletaInfoAdapter,
)
from resultados.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)
from torneo.infrastructure.repositories.sqlite_torneo_repository import SQLiteTorneoRepository
from shared.domain.ports.event_store_port import EventStorePort
from shared.domain.value_objects.disciplina import Disciplina


@dataclass(frozen=True)
class ExportarResultadosQuery:
    """Query para exportar todos los resultados de un torneo."""

    torneo_id: UUID


@dataclass(frozen=True)
class ExportDisciplinaEntradaDTO:
    """Fila exportable del ranking de una disciplina."""

    posicion: int
    atleta_id: str
    atleta_nombre: str
    categoria: str
    club: str
    ap: str | None
    rp: str | None
    tarjeta: str
    penalizaciones: int
    puntos: int


@dataclass(frozen=True)
class ExportDisciplinaDTO:
    """Bloque de una disciplina dentro de la exportación."""

    disciplina: str
    estado: str
    hash_sha256: str | None
    ranking: list[ExportDisciplinaEntradaDTO]


@dataclass(frozen=True)
class ExportOverallEntradaDTO:
    """Fila exportable del overall del torneo."""

    posicion: int
    atleta_id: str
    atleta_nombre: str
    categoria: str
    club: str
    puntos_totales: int


@dataclass(frozen=True)
class ExportResultadosDTO:
    """Payload consolidado para serialización JSON o CSV."""

    torneo_id: str
    torneo_nombre: str
    exportado_en: str
    disciplinas: list[ExportDisciplinaDTO]
    overall: list[ExportOverallEntradaDTO]


@dataclass(frozen=True)
class _PerformanceExportData:
    atleta_id: UUID
    disciplina: Disciplina
    ap: Decimal | None
    rp: Decimal | None
    tarjeta: str | None
    penalizaciones: int
    es_dns: bool
    finalizada: bool
    unidad: str | None = None


class ExportarResultadosHandler:
    """Consolida resultados exportables de todas las disciplinas de un torneo."""

    def __init__(
        self,
        ranking_store: EventStorePort,
        competencia_store: EventStorePort,
        competencias_por_torneo: SQLiteCompetenciasPorTorneo,
        torneo_repo: SQLiteTorneoRepository,
        atleta_info_adapter: AtletaInfoAdapter,
        descriptor: DisciplinaDescriptorAdapter | None = None,
    ) -> None:
        self._ranking_store = ranking_store
        self._competencia_store = competencia_store
        self._competencias_por_torneo = competencias_por_torneo
        self._torneo_repo = torneo_repo
        self._atleta_info_adapter = atleta_info_adapter
        self._descriptor = descriptor or DisciplinaDescriptorAdapter()

    async def handle(self, query: ExportarResultadosQuery) -> ExportResultadosDTO:
        """Retorna la exportación completa del torneo."""
        torneo = await self._torneo_repo.find_by_id(query.torneo_id)
        if torneo is None:
            raise TorneoNoEncontrado(f"Torneo {query.torneo_id} no encontrado")

        competencias = await self._competencias_por_torneo.listar_por_torneo(query.torneo_id)
        disciplinas = [
            await self._exportar_disciplina(competencia.competencia_id, competencia.disciplina)
            for competencia in competencias
        ]
        overall = await self._exportar_overall(query.torneo_id)

        return ExportResultadosDTO(
            torneo_id=str(query.torneo_id),
            torneo_nombre=torneo.nombre,
            exportado_en=datetime.now(timezone.utc).isoformat(),
            disciplinas=disciplinas,
            overall=overall,
        )

    async def _exportar_disciplina(
        self,
        competencia_id: UUID,
        disciplina_raw: str,
    ) -> ExportDisciplinaDTO:
        disciplina = Disciplina(disciplina_raw)
        estado, hash_sha256 = await _obtener_estado_y_hash(
            self._competencia_store,
            competencia_id,
            disciplina,
        )
        performances = await _obtener_performances_exportables(
            self._competencia_store,
            competencia_id,
            disciplina,
        )
        ranking = await self._resolver_ranking_disciplina(competencia_id, disciplina, performances)

        return ExportDisciplinaDTO(
            disciplina=disciplina.value,
            estado=estado,
            hash_sha256=hash_sha256 if estado == "Finalizada" else None,
            ranking=ranking,
        )

    async def _resolver_ranking_disciplina(
        self,
        competencia_id: UUID,
        disciplina: Disciplina,
        performances: list[_PerformanceExportData],
    ) -> list[ExportDisciplinaEntradaDTO]:
        ranking_handler = ObtenerRankingHandler(self._ranking_store)
        ranking_grupos = await ranking_handler.handle(
            ObtenerRankingQuery(competencia_id=competencia_id, disciplina=disciplina)
        )
        ranking_entries = [entry for grupo in ranking_grupos for entry in grupo.entradas]

        if not ranking_entries:
            ranking_entries = await self._calcular_ranking_parcial(
                competencia_id,
                disciplina,
                performances,
            )

        performance_map = {performance.atleta_id: performance for performance in performances}
        filas: list[ExportDisciplinaEntradaDTO] = []
        for entry in ranking_entries:
            atleta_id = UUID(entry.atleta_id)
            performance = performance_map.get(atleta_id)
            if performance is None:
                continue
            atleta_info = await self._atleta_info_adapter.get_atleta_info(atleta_id)
            filas.append(
                _construir_fila_disciplina(
                    entry.posicion,
                    performance,
                    atleta_info,
                )
            )
        return filas

    async def _calcular_ranking_parcial(
        self,
        competencia_id: UUID,
        disciplina: Disciplina,
        performances: list[_PerformanceExportData],
    ):
        resultados = []
        for performance in performances:
            atleta_info = await self._atleta_info_adapter.get_atleta_info(performance.atleta_id)
            resultados.append(
                replace(
                    _performance_a_resultado_final(performance),
                    categoria=atleta_info.categoria,
                )
            )
        if not resultados:
            return []

        ranking = RankingCompetencia.reconstitute(competencia_id, disciplina, events=[])
        try:
            ranking.calcular(resultados, self._descriptor.describe(disciplina))
        except ResultadosIncompletos:
            return []

        return [
            _PartialRankingEntry(
                posicion=entry.posicion,
                atleta_id=str(entry.atleta_id),
            )
            for entry in ranking.entries
        ]

    async def _exportar_overall(self, torneo_id: UUID) -> list[ExportOverallEntradaDTO]:
        overall_handler = ObtenerOverallHandler(self._ranking_store)
        overall_grupos = await overall_handler.handle(ObtenerOverallQuery(torneo_id=torneo_id))

        filas: list[ExportOverallEntradaDTO] = []
        for grupo in overall_grupos:
            for entry in grupo.entradas:
                atleta_info = await self._atleta_info_adapter.get_atleta_info(UUID(entry.atleta_id))
                filas.append(
                    ExportOverallEntradaDTO(
                        posicion=entry.posicion,
                        atleta_id=entry.atleta_id,
                        atleta_nombre=atleta_info.nombre_completo,
                        categoria=grupo.categoria,
                        club=atleta_info.club,
                        puntos_totales=entry.puntaje,
                    )
                )
        return filas


@dataclass(frozen=True)
class _PartialRankingEntry:
    posicion: int
    atleta_id: str


def _construir_fila_disciplina(
    posicion: int,
    performance: _PerformanceExportData,
    atleta_info: AtletaInfo,
) -> ExportDisciplinaEntradaDTO:
    tarjeta = "DNS" if performance.es_dns else (performance.tarjeta or "Pendiente")
    puntos = posicion if not performance.es_dns and tarjeta != "Roja" else 0
    return ExportDisciplinaEntradaDTO(
        posicion=posicion,
        atleta_id=str(performance.atleta_id),
        atleta_nombre=atleta_info.nombre_completo,
        categoria=atleta_info.categoria.value,
        club=atleta_info.club,
        ap=_decimal_to_str(performance.ap),
        rp=_decimal_to_str(performance.rp),
        tarjeta=tarjeta,
        penalizaciones=performance.penalizaciones,
        puntos=puntos,
    )


async def _obtener_estado_y_hash(
    competencia_store: EventStorePort,
    competencia_id: UUID,
    disciplina: Disciplina,
) -> tuple[str, str | None]:
    events = await competencia_store.load(f"competencia-{competencia_id}")
    if not events:
        return ("Preparacion", None)

    estado = "Preparacion"
    hash_sha256 = None
    for event in events:
        event_type = event["event_type"]
        if event_type == "GrillaConfirmada":
            estado = "Confirmada"
        elif event_type == "CompetenciaIniciada":
            estado = "EnEjecucion"
        elif event_type == "CompetenciaFinalizada":
            payload = _parse_payload(event["payload"])
            estado = "Finalizada"
            hash_sha256 = payload.get("hash_sha256")
    return estado, hash_sha256


async def _obtener_performances_exportables(
    competencia_store: EventStorePort,
    competencia_id: UUID,
    disciplina_buscada: Disciplina,
) -> list[_PerformanceExportData]:
    prefix = f"performance-{competencia_id}-"
    streams = await competencia_store.load_all_streams_with_prefix(prefix)
    resultados: list[_PerformanceExportData] = []
    for stream_events in streams:
        performance = _extraer_performance_exportable(stream_events, disciplina_buscada)
        if performance is not None:
            resultados.append(performance)
    return resultados


def _extraer_performance_exportable(
    stream_events: list[dict],
    disciplina_buscada: Disciplina,
) -> _PerformanceExportData | None:
    if not stream_events:
        return None

    estado: dict[str, object] = {
        "atleta_id": None,
        "disciplina": None,
        "ap": None,
        "rp": None,
        "unidad": None,
        "tarjeta": None,
        "es_dns": False,
        "penalizaciones": 0,
        "finalizada": False,
    }

    for event in stream_events:
        _aplicar_evento_performance_exportable(estado, event)

    if estado["disciplina"] != disciplina_buscada or estado["atleta_id"] is None:
        return None
    if not bool(estado["finalizada"]):
        return None

    return _PerformanceExportData(
        atleta_id=estado["atleta_id"],
        disciplina=estado["disciplina"],
        ap=estado["ap"],
        rp=estado["rp"],
        unidad=estado["unidad"],
        tarjeta=estado["tarjeta"],
        penalizaciones=int(estado["penalizaciones"]),
        es_dns=bool(estado["es_dns"]),
        finalizada=bool(estado["finalizada"]),
    )


def _performance_a_resultado_final(performance: _PerformanceExportData):
    from resultados.domain.ports.resultados_competencia_port import ResultadoFinal

    return ResultadoFinal(
        atleta_id=performance.atleta_id,
        rp=None if performance.es_dns else performance.rp,
        unidad=None if performance.es_dns else performance.unidad,
        tarjeta=performance.tarjeta,
        es_dns=performance.es_dns,
    )


def _decimal_to_str(value: Decimal | None) -> str | None:
    return str(value) if value is not None else None


def _parse_payload(payload: object) -> dict[str, object]:
    if isinstance(payload, str):
        return json.loads(payload)
    return payload


def _aplicar_evento_performance_exportable(estado: dict[str, object], event: dict) -> None:
    payload = _parse_payload(event["payload"])
    event_type = event["event_type"]
    if event_type == "APRegistrado":
        _aplicar_ap_registrado(estado, payload)
    elif event_type == "ResultadoRegistrado":
        _aplicar_resultado_registrado(estado, payload)
    elif event_type in {"TarjetaAsignada", "RevisionResuelta"}:
        _aplicar_cierre_con_tarjeta(estado, payload)
    elif event_type == "DNSRegistrado":
        _aplicar_dns_registrado(estado)


def _aplicar_ap_registrado(estado: dict[str, object], payload: dict[str, object]) -> None:
    estado["atleta_id"] = UUID(str(payload["participante_id"]))
    estado["disciplina"] = Disciplina(str(payload["disciplina"]))
    estado["ap"] = Decimal(str(payload["valor_ap"]))
    estado["unidad"] = str(payload["unidad"])


def _aplicar_resultado_registrado(estado: dict[str, object], payload: dict[str, object]) -> None:
    estado["rp"] = Decimal(str(payload["valor_rp"]))
    estado["unidad"] = str(payload["unidad"])


def _aplicar_cierre_con_tarjeta(estado: dict[str, object], payload: dict[str, object]) -> None:
    estado["tarjeta"] = str(payload["tipo"])
    rp_final = payload.get("rp_penalizado") or payload.get("rp_medido")
    if rp_final is not None:
        estado["rp"] = Decimal(str(rp_final))
    estado["penalizaciones"] = len(payload.get("penalizaciones", []))
    estado["finalizada"] = True


def _aplicar_dns_registrado(estado: dict[str, object]) -> None:
    estado["es_dns"] = True
    estado["finalizada"] = True
