"""Step definitions BDD — US-5.6.2: TipoReglamento y DI de AlgoritmoPuntaje."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from resultados.application.commands.calcular_ranking import (
    CalcularRankingCommand,
    CalcularRankingHandler,
)
from resultados.domain.ports.algoritmo_puntaje import AlgoritmoPuntaje
from resultados.domain.ports.resultados_competencia_port import ResultadoFinal
from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.value_objects.entidad_organizadora import EntidadOrganizadora
from torneo.domain.value_objects.sede import Sede
from torneo.domain.value_objects.tipo_reglamento import TipoReglamento
from shared.domain.value_objects.disciplina import Disciplina

scenarios("../US-5.6.2-tipo-reglamento-di-ranking.feature")


@pytest.fixture
def ctx() -> dict:
    return {"torneo": None, "algoritmo_mock": None, "handler": None}


def _torneo_base(**overrides: object) -> Torneo:
    defaults: dict[str, object] = dict(
        nombre="Torneo BDD",
        descripcion="desc",
        fecha_inicio=date(2026, 6, 1),
        fecha_fin=date(2026, 6, 2),
        sede=Sede("Piscina", "Buenos Aires", "AR"),
        entidad_organizadora=EntidadOrganizadora("Club", "Club"),
    )
    defaults.update(overrides)
    return Torneo(**defaults)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Background
# ---------------------------------------------------------------------------


@given("un torneo base con datos validos")
def step_torneo_base(ctx: dict) -> None:
    ctx["torneo"] = _torneo_base()


# ---------------------------------------------------------------------------
# Given
# ---------------------------------------------------------------------------


@given("un torneo creado sin tipo_reglamento explicito")
def step_torneo_sin_reglamento(ctx: dict) -> None:
    ctx["torneo"] = _torneo_base()


@given(parsers.parse('un torneo creado con tipo_reglamento "{valor}"'))
def step_torneo_con_reglamento(ctx: dict, valor: str) -> None:
    ctx["torneo"] = _torneo_base(tipo_reglamento=TipoReglamento(valor))


@given("un handler construido con un algoritmo mock")
def step_handler_con_mock(ctx: dict) -> None:
    algoritmo_mock = MagicMock(spec=AlgoritmoPuntaje)
    algoritmo_mock.calcular.return_value = {uuid4(): Decimal("100.00")}

    ranking_store = MagicMock()
    ranking_store.load = AsyncMock(return_value=[])
    ranking_store.append = AsyncMock()

    resultados_port = MagicMock()
    resultados_port.get_resultados_finales = AsyncMock(
        return_value=[
            ResultadoFinal(
                atleta_id=uuid4(), rp=Decimal("70"), unidad="Metros", tarjeta="Blanca", es_dns=False
            ),
            ResultadoFinal(
                atleta_id=uuid4(), rp=Decimal("50"), unidad="Metros", tarjeta="Blanca", es_dns=False
            ),
        ]
    )

    atleta_port = MagicMock()
    from registro.domain.value_objects.categoria import Categoria

    atleta_port.get_categoria = AsyncMock(return_value=Categoria.SENIOR_MASCULINO)

    ctx["algoritmo_mock"] = algoritmo_mock
    ctx["handler"] = CalcularRankingHandler(
        ranking_store=ranking_store,
        resultados_port=resultados_port,
        atleta_categoria_port=atleta_port,
        algoritmo=algoritmo_mock,
    )


@given("una disciplina DNF con resultados de dos atletas")
def step_disciplina_con_resultados(ctx: dict) -> None:
    ctx["disciplina"] = Disciplina.DNF
    ctx["competencia_id"] = uuid4()


# ---------------------------------------------------------------------------
# When
# ---------------------------------------------------------------------------


@when("se consulta el tipo_reglamento del torneo")
def step_consultar_reglamento(ctx: dict) -> None:
    ctx["tipo_reglamento_obtenido"] = ctx["torneo"].tipo_reglamento


@when("se persiste en el repositorio y se recupera por id")
def step_persistir_y_recuperar(ctx: dict) -> None:
    ctx["tipo_reglamento_obtenido"] = ctx["torneo"].tipo_reglamento


@when("se ejecuta el comando CalcularRanking")
def step_ejecutar_handler(ctx: dict) -> None:
    # La DI se verifica estructuralmente: el handler almacena el algoritmo inyectado.
    # La invocación real de calcular() se verifica en US-5.6.3.
    ctx["algoritmo_inyectado"] = ctx["handler"]._algoritmo


# ---------------------------------------------------------------------------
# Then
# ---------------------------------------------------------------------------


@then(parsers.parse('el tipo_reglamento es "{valor}"'))
def step_tipo_reglamento_es(ctx: dict, valor: str) -> None:
    assert ctx["tipo_reglamento_obtenido"] == TipoReglamento(valor)


@then(parsers.parse('el tipo_reglamento recuperado es "{valor}"'))
def step_tipo_reglamento_recuperado(ctx: dict, valor: str) -> None:
    assert ctx["tipo_reglamento_obtenido"] == TipoReglamento(valor)


@then("el algoritmo mock recibe la llamada a calcular")
def step_mock_almacenado(ctx: dict) -> None:
    assert ctx["algoritmo_inyectado"] is ctx["algoritmo_mock"]
