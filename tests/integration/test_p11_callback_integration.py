from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import aiosqlite
import pytest

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
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta

OT = datetime(2026, 3, 22, 10, 30, 0)


class FailingEmailPort:
    async def enviar(self, _destinatario, _contenido) -> str:
        raise RuntimeError("proveedor_no_disponible")


async def _performance_ejecutada(
    comp_store: SQLiteEventStore,
    competencia_id: UUID,
    atleta_id: UUID,
    valor: str,
) -> None:
    stub = StubCompetenciaEstadoAdapter()
    descriptor = DisciplinaDescriptorAdapter()
    await RegistrarAPHandler(comp_store, stub, descriptor).handle(
        RegistrarAPCommand(
            competencia_id=competencia_id,
            participante_id=atleta_id,
            disciplina=Disciplina.DNF,
            valor_ap=Decimal(valor),
            unidad=UnidadMedida.Metros,
        )
    )
    await LlamarAtletaHandler(comp_store, stub).handle(
        LlamarAtletaCommand(
            competencia_id=competencia_id,
            participante_id=atleta_id,
            disciplina=Disciplina.DNF,
            ot_programado=OT,
            posicion_grilla=1,
        )
    )
    await RegistrarResultadoHandler(comp_store, descriptor).handle(
        RegistrarResultadoCommand(
            competencia_id=competencia_id,
            participante_id=atleta_id,
            disciplina=Disciplina.DNF,
            valor_rp=Decimal(valor),
            unidad=UnidadMedida.Metros,
            registrado_por="juez-001",
        )
    )
    await AsignarTarjetaHandler(comp_store).handle(
        AsignarTarjetaCommand(
            competencia_id=competencia_id,
            participante_id=atleta_id,
            disciplina=Disciplina.DNF,
            tipo=TipoTarjeta.Blanca,
            asignada_por="juez-001",
        )
    )


async def _guardar_atleta(
    registro_db_path: str,
    atleta_id: UUID,
    nombre: str,
    email: str,
) -> None:
    await SQLiteAtletaRepository(registro_db_path).save(
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


async def _ranking_events(resultados_db_path: str, competencia_id: UUID) -> list[dict[str, Any]]:
    store = SQLiteEventStore(resultados_db_path)
    return await store.load(f"ranking-{competencia_id}-{Disciplina.DNF.value}")


@pytest.fixture
async def p11_context(tmp_path, monkeypatch):
    competencia_db = str(tmp_path / "competencia.db")
    resultados_db = str(tmp_path / "resultados.db")
    registro_db = str(tmp_path / "registro.db")
    torneo_db = str(tmp_path / "torneo.db")
    notificaciones_db = str(tmp_path / "notificaciones.db")
    monkeypatch.setenv("RESULTADOS_DB_PATH", resultados_db)
    monkeypatch.setenv("REGISTRO_DB_PATH", registro_db)
    monkeypatch.setenv("TORNEO_DB_PATH", torneo_db)
    monkeypatch.setenv("NOTIFICACIONES_DB_PATH", notificaciones_db)
    monkeypatch.delenv("RESEND_API_KEY", raising=False)

    comp_store = SQLiteEventStore(competencia_db)
    competencia_id = uuid4()
    atletas = (uuid4(), uuid4(), uuid4())
    await _performance_ejecutada(comp_store, competencia_id, atletas[0], "96")
    await _performance_ejecutada(comp_store, competencia_id, atletas[1], "88")
    await _performance_ejecutada(comp_store, competencia_id, atletas[2], "72")
    await _guardar_atleta(registro_db, atletas[0], "Martin", "martin@example.com")
    await _guardar_atleta(registro_db, atletas[1], "Ana", "ana@example.com")
    await _guardar_atleta(registro_db, atletas[2], "Diego", "diego@example.com")

    return {
        "comp_store": comp_store,
        "competencia_id": competencia_id,
        "atletas": atletas,
        "registro_db": registro_db,
        "resultados_db": resultados_db,
        "notificaciones_db": notificaciones_db,
    }


@pytest.mark.asyncio
async def test_on_finalizada_calcula_ranking_y_dispara_p11(p11_context) -> None:
    callback = build_on_finalizada_callback(p11_context["comp_store"])

    await callback(p11_context["competencia_id"], Disciplina.DNF, None)

    notifications = await _notificaciones(p11_context["notificaciones_db"])
    assert [event["event_type"] for event in notifications].count("NotificacionEnviada") == 3
    assert (
        len(await _ranking_events(p11_context["resultados_db"], p11_context["competencia_id"])) == 1
    )
    assert {
        event["payload"]["evento_fuente_id"]
        for event in notifications
        if event["event_type"] == "NotificacionEnviada"
    } == {
        f"{p11_context['competencia_id']}:{p11_context['atletas'][0]}",
        f"{p11_context['competencia_id']}:{p11_context['atletas'][1]}",
        f"{p11_context['competencia_id']}:{p11_context['atletas'][2]}",
    }


@pytest.mark.asyncio
async def test_on_finalizada_registra_fallo_si_atleta_no_tiene_email(
    p11_context,
) -> None:
    missing_atleta = p11_context["atletas"][2]
    async with aiosqlite.connect(p11_context["registro_db"]) as db:
        await db.execute(
            "UPDATE atletas SET email = '' WHERE atleta_id = ?",
            (str(missing_atleta),),
        )
        await db.commit()
    callback = build_on_finalizada_callback(p11_context["comp_store"])

    await callback(p11_context["competencia_id"], Disciplina.DNF, None)

    notifications = await _notificaciones(p11_context["notificaciones_db"])
    assert [event["event_type"] for event in notifications].count("NotificacionEnviada") == 2
    fallidas = [event for event in notifications if event["event_type"] == "NotificacionFallida"]
    assert len(fallidas) == 1
    assert fallidas[0]["payload"]["evento_fuente_id"] == (
        f"{p11_context['competencia_id']}:{missing_atleta}"
    )


@pytest.mark.asyncio
async def test_on_finalizada_no_duplica_notificaciones_si_reprocesa(
    p11_context,
) -> None:
    callback = build_on_finalizada_callback(p11_context["comp_store"])

    await callback(p11_context["competencia_id"], Disciplina.DNF, None)
    await callback(p11_context["competencia_id"], Disciplina.DNF, None)

    notifications = await _notificaciones(p11_context["notificaciones_db"])
    assert [event["event_type"] for event in notifications].count("NotificacionEnviada") == 3


@pytest.mark.asyncio
async def test_on_finalizada_no_propaga_fallo_de_p11_y_conserva_ranking(
    p11_context,
    monkeypatch,
) -> None:
    repo = SQLiteNotificacionRepository(
        SQLiteNotificacionEventStore(p11_context["notificaciones_db"])
    )
    failing_p11 = PoliticaP11Handler(
        repository=repo,
        solicitar_envio_handler=SolicitarEnvioHandler(repo),
        enviar_notificacion_handler=EnviarNotificacionHandler(repo, FailingEmailPort()),
        template=ResultadosPublicadosTemplate(),
    )
    monkeypatch.setattr(app_module, "build_p11_handler", lambda: failing_p11)
    callback = build_on_finalizada_callback(p11_context["comp_store"])

    await callback(p11_context["competencia_id"], Disciplina.DNF, None)

    notifications = await _notificaciones(p11_context["notificaciones_db"])
    assert [event["event_type"] for event in notifications].count("NotificacionFallida") == 3
    assert (
        len(await _ranking_events(p11_context["resultados_db"], p11_context["competencia_id"])) == 1
    )
