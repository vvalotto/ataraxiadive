from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID, uuid4

import pytest

from app import _notificar_resultados_p11, _obtener_nombre_torneo
from notificaciones.application.policies.politica_p11 import ResultadosPublicados
from registro.domain.aggregates.atleta import Atleta
from registro.domain.value_objects.categoria import Categoria
from resultados.domain.events.resultados_calculados import ResultadosCalculados
from shared.domain.value_objects.disciplina import Disciplina
from shared.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.value_objects.entidad_organizadora import EntidadOrganizadora
from torneo.domain.value_objects.sede import Sede


@dataclass
class FakeP11Handler:
    eventos: list[ResultadosPublicados]

    async def handle(self, evento: ResultadosPublicados) -> None:
        self.eventos.append(evento)


class FakeAtletaRepo:
    def __init__(self, atletas: dict[UUID, Atleta]) -> None:
        self._atletas = atletas

    async def find_by_id(self, atleta_id: UUID) -> Atleta | None:
        return self._atletas.get(atleta_id)


class FakeTorneoRepo:
    def __init__(self, torneo: Torneo | None) -> None:
        self._torneo = torneo

    async def find_by_id(self, _torneo_id: UUID) -> Torneo | None:
        return self._torneo


def _atleta(atleta_id: UUID, nombre: str, apellido: str, email: str) -> Atleta:
    return Atleta(
        atleta_id=atleta_id,
        nombre=nombre,
        apellido=apellido,
        email=email,
        fecha_nacimiento=date(1990, 1, 1),
        categoria=Categoria.SENIOR_MASCULINO,
        club="Club Test",
    )


def _torneo(torneo_id: UUID) -> Torneo:
    return Torneo(
        torneo_id=torneo_id,
        nombre="Open BA 2026",
        descripcion="Torneo de apnea",
        fecha_inicio=date(2026, 5, 15),
        fecha_fin=date(2026, 5, 16),
        sede=Sede(nombre="Club Nautico", ciudad="Buenos Aires", pais="Argentina"),
        entidad_organizadora=EntidadOrganizadora(nombre="ADA", tipo="FEDERACION"),
    )


async def _guardar_ranking(
    store: SQLiteEventStore,
    competencia_id: UUID,
    disciplina: Disciplina,
    atletas: tuple[UUID, UUID, UUID],
) -> None:
    event = ResultadosCalculados(
        event_type="ResultadosCalculados",
        aggregate_id=f"{competencia_id}-{disciplina.value}",
        occurred_at=ResultadosCalculados.now(),
        competencia_id=str(competencia_id),
        disciplina=disciplina.value,
        total=3,
        entries=(
            {
                "posicion": 1,
                "atleta_id": str(atletas[0]),
                "categoria": Categoria.SENIOR_MASCULINO.value,
                "rp": "96",
                "unidad": "Metros",
                "tarjeta": "Blanca",
                "es_dns": False,
                "en_podio": True,
            },
            {
                "posicion": 2,
                "atleta_id": str(atletas[1]),
                "categoria": Categoria.SENIOR_MASCULINO.value,
                "rp": "88",
                "unidad": "Metros",
                "tarjeta": "Blanca",
                "es_dns": False,
                "en_podio": True,
            },
            {
                "posicion": 3,
                "atleta_id": str(atletas[2]),
                "categoria": Categoria.SENIOR_MASCULINO.value,
                "rp": None,
                "unidad": None,
                "tarjeta": None,
                "es_dns": True,
                "en_podio": False,
            },
        ),
        calculado_en=ResultadosCalculados.now().isoformat(),
    )
    await store.append(
        f"ranking-{competencia_id}-{disciplina.value}",
        event.event_type,
        event.to_payload(),
    )


@pytest.mark.asyncio
async def test_notificar_resultados_p11_construye_evento_desde_ranking(tmp_path) -> None:
    competencia_id = uuid4()
    torneo_id = uuid4()
    disciplina = Disciplina.DNF
    atletas_ids = (uuid4(), uuid4(), uuid4())
    ranking_store = SQLiteEventStore(str(tmp_path / "resultados.db"))
    await _guardar_ranking(ranking_store, competencia_id, disciplina, atletas_ids)
    p11 = FakeP11Handler(eventos=[])

    await _notificar_resultados_p11(
        ranking_store=ranking_store,
        competencia_id=competencia_id,
        disciplina=disciplina,
        torneo_id=torneo_id,
        registro_db_path=str(tmp_path / "registro.db"),
        torneo_db_path=str(tmp_path / "torneo.db"),
        p11_handler=p11,  # type: ignore[arg-type]
        atleta_repo=FakeAtletaRepo(
            {
                atletas_ids[0]: _atleta(atletas_ids[0], "Martin", "Garcia", "m@example.com"),
                atletas_ids[1]: _atleta(atletas_ids[1], "Ana", "Lopez", "a@example.com"),
                atletas_ids[2]: _atleta(atletas_ids[2], "Diego", "Vega", "d@example.com"),
            }
        ),  # type: ignore[arg-type]
        torneo_repo=FakeTorneoRepo(_torneo(torneo_id)),  # type: ignore[arg-type]
    )

    assert len(p11.eventos) == 1
    evento = p11.eventos[0]
    assert evento.id == str(competencia_id)
    assert evento.torneo_nombre == "Open BA 2026"
    assert evento.disciplina == "DNF"
    assert [resultado.atleta_nombre for resultado in evento.resultados] == [
        "Martin Garcia",
        "Ana Lopez",
        "Diego Vega",
    ]
    assert evento.resultados[2].estado == "DNS"
    assert evento.resultados[2].rp == "DNS"
    assert [podio.atleta_nombre for podio in evento.podio] == ["Martin Garcia", "Ana Lopez"]


@pytest.mark.asyncio
async def test_notificar_resultados_p11_no_llama_politica_si_ranking_vacio(tmp_path) -> None:
    p11 = FakeP11Handler(eventos=[])

    await _notificar_resultados_p11(
        ranking_store=SQLiteEventStore(str(tmp_path / "resultados.db")),
        competencia_id=uuid4(),
        disciplina=Disciplina.DNF,
        torneo_id=None,
        registro_db_path=str(tmp_path / "registro.db"),
        torneo_db_path=str(tmp_path / "torneo.db"),
        p11_handler=p11,  # type: ignore[arg-type]
    )

    assert p11.eventos == []


@pytest.mark.asyncio
async def test_obtener_nombre_torneo_usa_fallback_sin_torneo_id(tmp_path) -> None:
    nombre = await _obtener_nombre_torneo(None, str(tmp_path / "torneo.db"))

    assert nombre == "Torneo sin nombre"


@pytest.mark.asyncio
async def test_obtener_nombre_torneo_usa_fallback_si_no_existe(tmp_path) -> None:
    torneo_id = uuid4()

    nombre = await _obtener_nombre_torneo(
        torneo_id,
        str(tmp_path / "torneo.db"),
        FakeTorneoRepo(None),  # type: ignore[arg-type]
    )

    assert nombre == f"Torneo {torneo_id}"
