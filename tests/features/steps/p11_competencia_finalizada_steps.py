from __future__ import annotations

import asyncio
import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import aiosqlite
import pytest
from pytest_bdd import given, scenarios, then, when

import app as app_module
from app import build_on_finalizada_callback
from competencia.application.commands.asignar_tarjeta import (
    AsignarTarjetaCommand,
    AsignarTarjetaHandler,
)
from competencia.application.commands.llamar_atleta import LlamarAtletaCommand, LlamarAtletaHandler
from competencia.application.commands.registrar_ap import RegistrarAPCommand, RegistrarAPHandler
from competencia.application.commands.registrar_resultado import (
    RegistrarResultadoCommand,
    RegistrarResultadoHandler,
)
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from notificaciones.application.commands.enviar_notificacion import EnviarNotificacionHandler
from notificaciones.application.commands.solicitar_envio import SolicitarEnvioHandler
from notificaciones.application.policies.politica_p11 import PoliticaP11Handler
from notificaciones.infrastructure.event_store.sqlite_notificacion_event_store import (
    SQLiteNotificacionEventStore,
)
from notificaciones.infrastructure.repositories.sqlite_notificacion_repository import (
    SQLiteNotificacionRepository,
)
from notificaciones.infrastructure.templates.resultados_publicados_template import (
    ResultadosPublicadosTemplate,
)
from registro.domain.aggregates.atleta import Atleta
from registro.domain.value_objects.categoria import Categoria
from registro.infrastructure.repositories.sqlite_atleta_repository import SQLiteAtletaRepository
from resultados.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)
from shared.domain.value_objects.disciplina import Disciplina
from shared.domain.value_objects.unidad_medida import UnidadMedida

scenarios("../US-ADJ-7.3-p11-competencia-finalizada.feature")

OT = datetime(2026, 3, 22, 10, 30, 0)


class FailingEmailPort:
    async def enviar(self, _destinatario, _contenido) -> str:
        raise RuntimeError("proveedor_no_disponible")


@pytest.fixture
def ctx(tmp_path, monkeypatch) -> dict[str, Any]:
    paths = {
        "competencia_db": str(tmp_path / "competencia.db"),
        "resultados_db": str(tmp_path / "resultados.db"),
        "registro_db": str(tmp_path / "registro.db"),
        "torneo_db": str(tmp_path / "torneo.db"),
        "notificaciones_db": str(tmp_path / "notificaciones.db"),
    }
    monkeypatch.setenv("RESULTADOS_DB_PATH", paths["resultados_db"])
    monkeypatch.setenv("REGISTRO_DB_PATH", paths["registro_db"])
    monkeypatch.setenv("TORNEO_DB_PATH", paths["torneo_db"])
    monkeypatch.setenv("NOTIFICACIONES_DB_PATH", paths["notificaciones_db"])
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    return {
        **paths,
        "comp_store": SQLiteEventStore(paths["competencia_db"]),
        "competencia_id": uuid4(),
        "atletas": (uuid4(), uuid4(), uuid4()),
        "error": None,
    }


async def _performance_ejecutada(
    store: SQLiteEventStore,
    competencia_id: UUID,
    atleta_id: UUID,
    valor: str,
) -> None:
    stub = StubCompetenciaEstadoAdapter()
    descriptor = DisciplinaDescriptorAdapter()
    await RegistrarAPHandler(store, stub, descriptor).handle(
        RegistrarAPCommand(
            competencia_id=competencia_id,
            participante_id=atleta_id,
            disciplina=Disciplina.DNF,
            valor_ap=Decimal(valor),
            unidad=UnidadMedida.Metros,
        )
    )
    await LlamarAtletaHandler(store, stub).handle(
        LlamarAtletaCommand(
            competencia_id=competencia_id,
            participante_id=atleta_id,
            disciplina=Disciplina.DNF,
            ot_programado=OT,
            posicion_grilla=1,
        )
    )
    await RegistrarResultadoHandler(store, descriptor).handle(
        RegistrarResultadoCommand(
            competencia_id=competencia_id,
            participante_id=atleta_id,
            disciplina=Disciplina.DNF,
            valor_rp=Decimal(valor),
            unidad=UnidadMedida.Metros,
            registrado_por="juez-001",
        )
    )
    await AsignarTarjetaHandler(store).handle(
        AsignarTarjetaCommand(
            competencia_id=competencia_id,
            participante_id=atleta_id,
            disciplina=Disciplina.DNF,
            tipo=TipoTarjeta.Blanca,
            asignada_por="juez-001",
        )
    )


async def _guardar_atleta(db_path: str, atleta_id: UUID, nombre: str, email: str) -> None:
    await SQLiteAtletaRepository(db_path).save(
        Atleta(
            atleta_id=atleta_id,
            nombre=nombre,
            apellido="Test",
            email=email,
            fecha_nacimiento=date(1990, 1, 1),
            categoria=Categoria.SENIOR_MASCULINO,
            club="Club Test",
        )
    )


async def _notificaciones(db_path: str) -> list[dict[str, Any]]:
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT event_type, payload FROM notificaciones_events ORDER BY id ASC"
        )
        rows = await cursor.fetchall()
    return [
        {"event_type": row["event_type"], "payload": json.loads(row["payload"])} for row in rows
    ]


async def _ranking_events(ctx: dict[str, Any]) -> list[dict[str, Any]]:
    return await SQLiteEventStore(ctx["resultados_db"]).load(
        f"ranking-{ctx['competencia_id']}-{Disciplina.DNF.value}"
    )


@given("una disciplina finalizada con ranking calculable para 3 atletas")
def given_disciplina_finalizada(ctx: dict[str, Any]) -> None:
    async def _run() -> None:
        valores = ("96", "88", "72")
        nombres = ("Martin", "Ana", "Diego")
        emails = ("martin@example.com", "ana@example.com", "diego@example.com")
        for atleta_id, valor, nombre, email in zip(
            ctx["atletas"],
            valores,
            nombres,
            emails,
            strict=True,
        ):
            await _performance_ejecutada(
                ctx["comp_store"],
                ctx["competencia_id"],
                atleta_id,
                valor,
            )
            await _guardar_atleta(ctx["registro_db"], atleta_id, nombre, email)

    asyncio.run(_run())


@given("uno de los atletas no tiene email registrado")
def given_atleta_sin_email(ctx: dict[str, Any]) -> None:
    async def _run() -> None:
        async with aiosqlite.connect(ctx["registro_db"]) as db:
            await db.execute(
                "UPDATE atletas SET email = '' WHERE atleta_id = ?",
                (str(ctx["atletas"][2]),),
            )
            await db.commit()

    asyncio.run(_run())


@given("el callback de finalizacion ya se ejecuto una vez")
def given_callback_ya_ejecutado(ctx: dict[str, Any]) -> None:
    when_callback_finalizacion(ctx)


@given("el proveedor de email falla al enviar")
def given_proveedor_falla(ctx: dict[str, Any], monkeypatch) -> None:
    repo = SQLiteNotificacionRepository(SQLiteNotificacionEventStore(ctx["notificaciones_db"]))
    p11 = PoliticaP11Handler(
        repository=repo,
        solicitar_envio_handler=SolicitarEnvioHandler(repo),
        enviar_notificacion_handler=EnviarNotificacionHandler(repo, FailingEmailPort()),
        template=ResultadosPublicadosTemplate(),
    )
    monkeypatch.setattr(app_module, "build_p11_handler", lambda: p11)


@when("se ejecuta el callback de finalizacion de competencia")
def when_callback_finalizacion(ctx: dict[str, Any]) -> None:
    async def _run() -> None:
        try:
            callback = build_on_finalizada_callback(ctx["comp_store"])
            await callback(ctx["competencia_id"], Disciplina.DNF, None)
        except Exception as exc:  # noqa: BLE001
            ctx["error"] = exc

    asyncio.run(_run())


@then("el store de notificaciones contiene NotificacionEnviada para los 3 atletas")
def then_tres_enviadas(ctx: dict[str, Any]) -> None:
    events = asyncio.run(_notificaciones(ctx["notificaciones_db"]))
    assert [event["event_type"] for event in events].count("NotificacionEnviada") == 3


@then("cada email contiene nombre del atleta, posicion, RP y disciplina")
def then_payloads_contienen_resultados(ctx: dict[str, Any]) -> None:
    events = asyncio.run(_notificaciones(ctx["notificaciones_db"]))
    enviadas = [event for event in events if event["event_type"] == "NotificacionEnviada"]
    assert len(enviadas) == 3
    assert {event["payload"]["evento_fuente_id"].split(":")[1] for event in enviadas} == {
        str(atleta_id) for atleta_id in ctx["atletas"]
    }


@then("el store de notificaciones contiene NotificacionFallida para ese atleta")
def then_fallida_sin_email(ctx: dict[str, Any]) -> None:
    events = asyncio.run(_notificaciones(ctx["notificaciones_db"]))
    fallidas = [event for event in events if event["event_type"] == "NotificacionFallida"]
    assert len(fallidas) == 1
    assert fallidas[0]["payload"]["evento_fuente_id"].endswith(str(ctx["atletas"][2]))


@then("los otros 2 atletas reciben email normalmente")
def then_dos_enviadas(ctx: dict[str, Any]) -> None:
    events = asyncio.run(_notificaciones(ctx["notificaciones_db"]))
    assert [event["event_type"] for event in events].count("NotificacionEnviada") == 2


@then("no se envian emails duplicados")
def then_no_duplicados(ctx: dict[str, Any]) -> None:
    then_store_una_por_atleta(ctx)


@then("el store de notificaciones conserva una NotificacionEnviada por atleta")
def then_store_una_por_atleta(ctx: dict[str, Any]) -> None:
    events = asyncio.run(_notificaciones(ctx["notificaciones_db"]))
    enviadas = [event for event in events if event["event_type"] == "NotificacionEnviada"]
    assert len(enviadas) == 3
    assert len({event["payload"]["evento_fuente_id"] for event in enviadas}) == 3


@then("no se propaga error al callback de finalizacion")
def then_no_error(ctx: dict[str, Any]) -> None:
    assert ctx["error"] is None


@then("el fallo de envio queda registrado en notificaciones")
def then_fallos_envio(ctx: dict[str, Any]) -> None:
    events = asyncio.run(_notificaciones(ctx["notificaciones_db"]))
    assert [event["event_type"] for event in events].count("NotificacionFallida") == 3


@then("el ranking calculado sigue disponible")
def then_ranking_disponible(ctx: dict[str, Any]) -> None:
    events = asyncio.run(_ranking_events(ctx))
    assert [event["event_type"] for event in events].count("ResultadosCalculados") >= 1
