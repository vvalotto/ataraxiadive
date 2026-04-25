"""Tests unitarios del endpoint POST /competencia/{id}/registrar-ap — US-5.5.1."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from competencia.api.router import get_registrar_ap_handler, router
from competencia.application.commands.registrar_ap import (
    APYaRegistrado,
    GrillaYaConfirmadaError,
    PlazoAPVencidoError,
    RegistrarAPCommand,
)
from competencia.application.commands.registrar_resultado import UnidadIncompatible
from competencia.domain.value_objects.ap import ValorAPInvalido
from identidad.api.dependencies import get_current_user

COMPETENCIA_ID = UUID("00000000-0000-0000-0000-000000005501")
ATLETA_ID = UUID("aaaaaaaa-0000-0000-0000-000000000001")
PERFORMANCE_ID = UUID("bbbbbbbb-0000-0000-0000-000000000001")

ATLETA_USER = {
    "sub": str(ATLETA_ID),
    "email": "ana@email.com",
    "rol": "ATLETA",
}


class SpyRegistrarAPHandler:
    """Handler espía que captura el command recibido."""

    def __init__(self, return_id: UUID = PERFORMANCE_ID, raise_exc: Exception | None = None):
        self.command: RegistrarAPCommand | None = None
        self._return_id = return_id
        self._raise_exc = raise_exc

    async def handle(self, command: RegistrarAPCommand) -> UUID:
        self.command = command
        if self._raise_exc:
            raise self._raise_exc
        return self._return_id


def _build_client(handler: SpyRegistrarAPHandler) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_registrar_ap_handler] = lambda: handler
    app.dependency_overrides[get_current_user] = lambda: ATLETA_USER
    return TestClient(app)


def test_registrar_ap_201_retorna_performance_id() -> None:
    handler = SpyRegistrarAPHandler()
    client = _build_client(handler)

    response = client.post(
        f"/competencia/{COMPETENCIA_ID}/registrar-ap",
        json={"disciplina": "DNF", "valor_ap": 70, "unidad": "Metros"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["performance_id"] == str(PERFORMANCE_ID)


def test_registrar_ap_extrae_participante_id_del_jwt() -> None:
    handler = SpyRegistrarAPHandler()
    client = _build_client(handler)

    client.post(
        f"/competencia/{COMPETENCIA_ID}/registrar-ap",
        json={"disciplina": "DNF", "valor_ap": 70, "unidad": "Metros"},
    )

    assert handler.command is not None
    assert handler.command.participante_id == ATLETA_ID
    assert handler.command.competencia_id == COMPETENCIA_ID


def test_registrar_ap_409_si_ap_ya_registrado() -> None:
    handler = SpyRegistrarAPHandler(raise_exc=APYaRegistrado("INV-P-02: ya existe un AP"))
    client = _build_client(handler)

    response = client.post(
        f"/competencia/{COMPETENCIA_ID}/registrar-ap",
        json={"disciplina": "DNF", "valor_ap": 65, "unidad": "Metros"},
    )

    assert response.status_code == 409
    assert "ya existe un AP" in response.json()["detail"]


def test_registrar_ap_409_si_grilla_confirmada() -> None:
    handler = SpyRegistrarAPHandler(
        raise_exc=GrillaYaConfirmadaError("INV-P-04: grilla confirmada")
    )
    client = _build_client(handler)

    response = client.post(
        f"/competencia/{COMPETENCIA_ID}/registrar-ap",
        json={"disciplina": "DNF", "valor_ap": 70, "unidad": "Metros"},
    )

    assert response.status_code == 409


def test_registrar_ap_409_si_plazo_vencido() -> None:
    handler = SpyRegistrarAPHandler(raise_exc=PlazoAPVencidoError("INV-P-03: plazo vencido"))
    client = _build_client(handler)

    response = client.post(
        f"/competencia/{COMPETENCIA_ID}/registrar-ap",
        json={"disciplina": "DNF", "valor_ap": 70, "unidad": "Metros"},
    )

    assert response.status_code == 409


def test_registrar_ap_422_si_unidad_incompatible() -> None:
    handler = SpyRegistrarAPHandler(raise_exc=UnidadIncompatible("DNF requiere Metros"))
    client = _build_client(handler)

    response = client.post(
        f"/competencia/{COMPETENCIA_ID}/registrar-ap",
        json={"disciplina": "DNF", "valor_ap": 70, "unidad": "Segundos"},
    )

    assert response.status_code == 422


def test_registrar_ap_422_si_valor_ap_invalido() -> None:
    handler = SpyRegistrarAPHandler(raise_exc=ValorAPInvalido("INV-P-01: valor <= 0"))
    client = _build_client(handler)

    response = client.post(
        f"/competencia/{COMPETENCIA_ID}/registrar-ap",
        json={"disciplina": "DNF", "valor_ap": 0, "unidad": "Metros"},
    )

    assert response.status_code == 422


def test_registrar_ap_traduce_valor_decimal_correctamente() -> None:
    handler = SpyRegistrarAPHandler()
    client = _build_client(handler)

    client.post(
        f"/competencia/{COMPETENCIA_ID}/registrar-ap",
        json={"disciplina": "STA", "valor_ap": 300.5, "unidad": "Segundos"},
    )

    assert handler.command is not None
    assert handler.command.valor_ap == Decimal("300.5")
    assert handler.command.disciplina.value == "STA"
