"""Aggregate Competencia — ciclo de vida de una disciplina en un torneo."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from uuid import UUID

from shared.domain.base.aggregate_root import AggregateRoot
from competencia.domain.entities.grilla_de_salida import GrillaDeSalida
from competencia.domain.events.competencia_finalizada import CompetenciaFinalizada
from competencia.domain.events.competencia_iniciada import CompetenciaIniciada
from competencia.domain.events.grilla_confirmada import GrillaConfirmada
from competencia.domain.events.grilla_de_salida_ajustada import GrillaDeSalidaAjustada
from competencia.domain.events.grilla_de_salida_generada import GrillaDeSalidaGenerada
from competencia.domain.events.intervalo_ot_configurado import IntervaloOTConfigurado
from competencia.domain.exceptions import (
    CompetenciaNoConfirmada,
    CompetenciaNoFinalizable,
    GrillaNoGenerada,
    GrillaYaConfirmada,
    IntervaloNoConfigurado,
    PerformanceNoEncontrada,
    SinPerformancesParaGrilla,
)
from competencia.domain.ports.performances_ap_port import PerformancesAPData
from competencia.domain.value_objects.cambio_grilla import CambioGrilla
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.disciplina_descriptor import DisciplinaDescriptor
from competencia.domain.value_objects.estado_competencia import EstadoCompetencia
from competencia.domain.value_objects.intervalo_disciplina import IntervaloDisciplina


class Competencia(AggregateRoot):
    """Aggregate raíz que modela el ciclo de vida de una disciplina en un torneo.

    Stream ID: "competencia-{competencia_id}"

    Estados:
        Preparacion → Confirmada → EnEjecucion → Finalizada

    Invariantes:
        INV-C-01: intervaloDisciplina debe estar configurado antes de GenerarGrilla.
        INV-CT-01: torneo_id es opcional — None para competencias standalone (SP1/SP2).
        INV-CT-02: si torneo_id se provee, se persiste en el payload de IntervaloOTConfigurado.
        INV-CT-03: streams existentes sin torneo_id se reconstituyen
        correctamente (backward compat).
    """

    def __init__(
        self,
        competencia_id: UUID,
        disciplina: Disciplina,
        torneo_id: UUID | None = None,
    ) -> None:
        super().__init__()
        self._competencia_id = competencia_id
        self._disciplina = disciplina
        self._torneo_id: UUID | None = torneo_id
        self._estado: EstadoCompetencia = EstadoCompetencia.Preparacion
        self._intervalo: IntervaloDisciplina | None = None
        self._grilla_confirmada: bool = False
        self._hash_sha256: str | None = None
        self._grilla = GrillaDeSalida()

    # ── Propiedades ───────────────────────────────────────────────────────────

    @property
    def competencia_id(self) -> UUID:
        """Identificador único de la Competencia."""
        return self._competencia_id

    @property
    def disciplina(self) -> Disciplina:
        """Disciplina asociada a esta Competencia."""
        return self._disciplina

    @property
    def estado(self) -> EstadoCompetencia:
        """Estado actual de la Competencia."""
        return self._estado

    @property
    def intervalo(self) -> IntervaloDisciplina | None:
        """Intervalo entre OTs configurado, o None si aún no fue configurado."""
        return self._intervalo

    @property
    def grilla(self) -> list[Any]:
        """Grilla de salida actual (última generada), o lista vacía si no fue generada."""
        return self._grilla.entradas

    @property
    def torneo_id(self) -> UUID | None:
        """Torneo al que pertenece esta competencia, o None si es standalone."""
        return self._torneo_id

    @property
    def grilla_confirmada(self) -> bool:
        """True si la grilla fue confirmada de forma irreversible."""
        return self._grilla_confirmada

    @property
    def hash_sha256(self) -> str | None:
        """Hash SHA-256 persistido al cierre, o None si la competencia no finalizó."""
        return self._hash_sha256

    # ── Comandos de dominio ───────────────────────────────────────────────────

    def configurar_intervalo_ot(
        self, intervalo_minutos: int, configurado_por: str, torneo_id: UUID | None = None
    ) -> None:
        """Configura (o reconfigura) el intervalo de tiempo entre OTs consecutivos.

        La operación es repetible. Si ya existe un IntervaloOTConfigurado previo,
        se emite uno nuevo con el valor actualizado (P-03: OTs desactualizados
        hasta regenerar grilla).

        Si la grilla ya fue confirmada (GrillaConfirmada emitido), la operación
        no está permitida — la grilla está congelada.

        Args:
            intervalo_minutos: Tiempo en minutos entre OTs. Debe ser > 0.
            configurado_por: Identificador del organizador o juez.

        Raises:
            IntervaloInvalido: Si intervalo_minutos <= 0.
            GrillaYaConfirmada: Si la grilla ya fue confirmada para esta competencia.
        """
        if self._grilla_confirmada:
            raise GrillaYaConfirmada(
                f"Competencia {self._competencia_id}: grilla confirmada — "
                "no se puede reconfigurar el intervalo OT"
            )

        intervalo = IntervaloDisciplina(minutos=intervalo_minutos)  # valida > 0

        if torneo_id is not None:
            self._torneo_id = torneo_id

        event = IntervaloOTConfigurado(
            event_type="IntervaloOTConfigurado",
            aggregate_id=str(self._competencia_id),
            occurred_at=IntervaloOTConfigurado.now(),
            competencia_id=str(self._competencia_id),
            disciplina=self._disciplina.value,
            intervalo_minutos=intervalo.minutos,
            configurado_por=configurado_por,
            torneo_id=str(torneo_id) if torneo_id else None,
        )
        self._intervalo = intervalo
        self._record(event)

    def generar_grilla(
        self,
        ot_inicio: datetime,
        performances: list[PerformancesAPData],
        descriptor: DisciplinaDescriptor,
        andariveles: int = 1,
    ) -> None:
        """Genera (o regenera) la Grilla de Salida ordenando atletas por AP.

        Ordenamiento (política P-01):
            - Disciplinas de tiempo (STA): AP mayor → menor (primero el más largo).
            - Disciplinas de distancia (DNF, DYN, etc.): AP menor → mayor
              (primero el más conservador).

        Cálculo de OT (política P-02):
            OT_atleta = ot_inicio + (posicion − 1) × intervaloDisciplina

        La operación es repetible mientras la grilla no esté confirmada.

        Args:
            ot_inicio: Timestamp de inicio de la competencia (hora cero de la grilla).
            performances: Lista de performances con AP registrado para esta competencia.
                Debe contener solo las que están en estado AnunciadaAP.
            andariveles: Número de andariveles disponibles (default 1 — Inc 2.1).

        Raises:
            IntervaloNoConfigurado: INV-C-01 — intervalo no configurado.
            GrillaYaConfirmada: La grilla fue confirmada — regeneración no permitida.
            SinPerformancesParaGrilla: No hay performances con AP para generar la grilla.
        """
        if self._intervalo is None:
            raise IntervaloNoConfigurado(
                f"Competencia {self._competencia_id}: INV-C-01 — "
                "intervaloDisciplina no configurado"
            )
        if self._grilla_confirmada:
            raise GrillaYaConfirmada(
                f"Competencia {self._competencia_id}: grilla confirmada — " "no se puede regenerar"
            )
        if not performances:
            raise SinPerformancesParaGrilla(
                f"Competencia {self._competencia_id}: no hay performances con AP"
            )

        entradas = self._grilla.generar(
            ot_inicio=ot_inicio,
            performances=performances,
            descriptor=descriptor,
            intervalo=self._intervalo,
            andariveles=andariveles,
        )
        now = GrillaDeSalidaGenerada.now()
        event = GrillaDeSalidaGenerada(
            event_type="GrillaDeSalidaGenerada",
            aggregate_id=str(self._competencia_id),
            occurred_at=now,
            competencia_id=str(self._competencia_id),
            disciplina=self._disciplina.value,
            ot_inicio=ot_inicio.isoformat(),
            performances=tuple(self._serializar_grilla(entradas)),
            generada_en=now.isoformat(),
        )
        self._record(event)

    def ajustar_grilla(self, cambios: list[CambioGrilla]) -> None:
        """Aplica ajustes manuales sobre la Grilla de Salida generada.

        Permite modificar la posición o el andarivel de uno o más atletas.
        Si se cambia la posición, los OTs se recalculan para todos los atletas
        según la política P-02.

        La operación es acumulativa: puede llamarse múltiples veces antes de
        confirmar la grilla, emitiendo un evento por cada llamada.

        Args:
            cambios: Lista de cambios a aplicar. Cada cambio especifica
                performance_id, campo ("posicion"|"andarivel") y valor_nuevo.

        Raises:
            GrillaNoGenerada: Si la grilla no fue generada aún.
            GrillaYaConfirmada: INV-C-02 — grilla confirmada, ajuste no permitido.
            PerformanceNoEncontrada: Si algún performance_id no existe en la grilla.
        """
        if not self._grilla.esta_generada:
            raise GrillaNoGenerada(
                f"Competencia {self._competencia_id}: grilla no generada — "
                "ejecutar generar_grilla() antes de ajustar"
            )
        if self._grilla_confirmada:
            raise GrillaYaConfirmada(
                f"Competencia {self._competencia_id}: INV-C-02 — "
                "grilla confirmada, ajuste no permitido"
            )

        grilla_por_id = {entrada.performance_id: entrada for entrada in self._grilla.entradas}
        for cambio in cambios:
            if cambio.performance_id not in grilla_por_id:
                raise PerformanceNoEncontrada(
                    f"Competencia {self._competencia_id}: performance "
                    f"{cambio.performance_id} no encontrada en la grilla"
                )
        _, cambios_payload = self._grilla.ajustar(cambios=cambios, intervalo=self._intervalo)

        now = GrillaDeSalidaAjustada.now()
        event = GrillaDeSalidaAjustada(
            event_type="GrillaDeSalidaAjustada",
            aggregate_id=str(self._competencia_id),
            occurred_at=now,
            competencia_id=str(self._competencia_id),
            disciplina=self._disciplina.value,
            cambios=tuple(cambios_payload),
            ajustada_en=now.isoformat(),
        )
        self._record(event)

    def confirmar_grilla(self) -> None:
        """Confirma la Grilla de Salida, congelándola de forma irreversible (INV-C-02).

        Después de este evento, GenerarGrilla, AjustarGrilla y ConfigurarIntervaloOT
        quedan bloqueados. Transiciona el estado a Confirmada.

        Raises:
            GrillaNoGenerada: Si la grilla no fue generada aún.
            GrillaYaConfirmada: Si la grilla ya fue confirmada previamente.
        """
        if not self._grilla.esta_generada:
            raise GrillaNoGenerada(
                f"Competencia {self._competencia_id}: grilla no generada — "
                "confirmar_grilla requiere GrillaDeSalidaGenerada previo"
            )
        if self._grilla_confirmada:
            raise GrillaYaConfirmada(
                f"Competencia {self._competencia_id}: INV-C-02 — "
                "grilla ya confirmada, operación irreversible"
            )

        now = GrillaConfirmada.now()
        event = GrillaConfirmada(
            event_type="GrillaConfirmada",
            aggregate_id=str(self._competencia_id),
            occurred_at=now,
            competencia_id=str(self._competencia_id),
            disciplina=self._disciplina.value,
            confirmada_en=now.isoformat(),
        )
        self._grilla_confirmada = True
        self._estado = EstadoCompetencia.Confirmada
        self._record(event)

    def iniciar_competencia(self, juez_id: str) -> None:
        """Inicia la Competencia, habilitando el registro de performances (INV-C-03).

        Precondición: la grilla debe estar confirmada (estado Confirmada).
        Transiciona el estado a EnEjecucion.

        Args:
            juez_id: Identificador del juez que inicia la competencia.

        Raises:
            CompetenciaNoConfirmada: INV-C-03 — competencia no está en estado Confirmada.
        """
        if self._estado != EstadoCompetencia.Confirmada:
            raise CompetenciaNoConfirmada(
                f"Competencia {self._competencia_id}: INV-C-03 — "
                f"estado actual '{self._estado}', se requiere 'Confirmada'"
            )

        now = CompetenciaIniciada.now()
        event = CompetenciaIniciada(
            event_type="CompetenciaIniciada",
            aggregate_id=str(self._competencia_id),
            occurred_at=now,
            competencia_id=str(self._competencia_id),
            disciplina=self._disciplina.value,
            juez_id=juez_id,
            iniciada_en=now.isoformat(),
        )
        self._estado = EstadoCompetencia.EnEjecucion
        self._record(event)

    def finalizar(
        self,
        total_performances: int,
        ejecutadas: int,
        dns_count: int,
        hash_sha256: str,
        origen: str = "automatico",
        finalizada_por: str | None = None,
    ) -> None:
        """Finaliza la Competencia cuando todas las performances están completas (INV-C-04).

        Emite CompetenciaFinalizada y transiciona el estado a Finalizada.

        Args:
            total_performances: Total de performances de la disciplina.
            ejecutadas: Cantidad en estado Ejecutada.
            dns_count: Cantidad en estado DNS.
            hash_sha256: Hash SHA-256 de la secuencia canónica de eventos de la disciplina.
            origen: Origen auditable del cierre.
            finalizada_por: Usuario que solicito el cierre manual, si aplica.

        Raises:
            CompetenciaNoFinalizable: INV-C-04 — quedan performances en AnunciadaAP o Llamada.
        """
        pendientes = total_performances - ejecutadas - dns_count
        if pendientes > 0:
            raise CompetenciaNoFinalizable(
                f"Competencia {self._competencia_id}: INV-C-04 — "
                f"{pendientes} performance(s) aún pendientes"
            )

        now = CompetenciaFinalizada.now()
        event = CompetenciaFinalizada(
            event_type="CompetenciaFinalizada",
            aggregate_id=str(self._competencia_id),
            occurred_at=now,
            competencia_id=str(self._competencia_id),
            disciplina=self._disciplina.value,
            total_performances=total_performances,
            ejecutadas=ejecutadas,
            dns_count=dns_count,
            finalizada_en=now.isoformat(),
            hash_sha256=hash_sha256,
            origen=origen,
            finalizada_por=finalizada_por,
        )
        self._estado = EstadoCompetencia.Finalizada
        self._hash_sha256 = hash_sha256
        self._record(event)

    # ── Reconstitución desde eventos ──────────────────────────────────────────

    @classmethod
    def reconstitute(
        cls, competencia_id: UUID, disciplina: Disciplina, events: list[dict[str, Any]]
    ) -> "Competencia":
        """Reconstruye el aggregate desde los eventos del Event Store.

        Args:
            competencia_id: Identificador de la competencia.
            disciplina: Disciplina asociada.
            events: Lista de registros del Event Store (con event_type, payload).

        Returns:
            Competencia con el estado proyectado desde los eventos.
        """
        competencia = cls(competencia_id=competencia_id, disciplina=disciplina)
        for event in events:
            competencia._apply_stored(event)
        return competencia

    def _apply_stored(self, event: dict[str, Any]) -> None:
        """Aplica un evento almacenado al estado interno del aggregate."""
        event_type = event["event_type"]
        payload = self._parse_payload(event["payload"])

        _handlers: dict[str, Any] = {
            "IntervaloOTConfigurado": self._apply_intervalo_ot_configurado,
            "GrillaDeSalidaGenerada": self._apply_grilla_de_salida_generada,
            "GrillaDeSalidaAjustada": self._apply_grilla_de_salida_ajustada,
            "GrillaConfirmada": self._apply_grilla_confirmada,
            "CompetenciaIniciada": self._apply_competencia_iniciada,
            "CompetenciaFinalizada": self._apply_competencia_finalizada,
        }

        handler = _handlers.get(event_type)
        if handler is not None:
            handler(payload)

    def _apply_intervalo_ot_configurado(self, payload: dict[str, Any]) -> None:
        self._intervalo = IntervaloDisciplina(minutos=payload["intervalo_minutos"])
        raw = payload.get("torneo_id")
        if raw is not None:
            self._torneo_id = UUID(raw)

    def _apply_grilla_de_salida_generada(self, payload: dict[str, Any]) -> None:
        self._grilla.cargar_desde_payload(payload["performances"])

    def _apply_grilla_de_salida_ajustada(self, payload: dict[str, Any]) -> None:
        self._grilla.aplicar_cambios_persistidos(
            cambios=payload["cambios"],
            intervalo=self._intervalo,
        )

    def _apply_grilla_confirmada(self, payload: dict[str, Any]) -> None:  # noqa: ARG002
        self._grilla_confirmada = True
        self._estado = EstadoCompetencia.Confirmada

    def _apply_competencia_iniciada(self, payload: dict[str, Any]) -> None:  # noqa: ARG002
        self._estado = EstadoCompetencia.EnEjecucion

    def _apply_competencia_finalizada(self, payload: dict[str, Any]) -> None:
        self._estado = EstadoCompetencia.Finalizada
        self._hash_sha256 = payload.get("hash_sha256")

    @staticmethod
    def _parse_payload(payload: Any) -> dict[str, Any]:
        """Parsea el payload del Event Store (puede ser str JSON o dict)."""
        if isinstance(payload, str):
            return json.loads(payload)  # type: ignore[no-any-return]
        return payload  # type: ignore[return-value]

    @staticmethod
    def _serializar_grilla(entradas: list[Any]) -> list[dict[str, object]]:
        return [
            {
                "performance_id": str(entrada.performance_id),
                "atleta_id": str(entrada.atleta_id),
                "posicion": entrada.posicion,
                "andarivel": entrada.andarivel,
                "ot_programado": entrada.ot_programado.isoformat(),
            }
            for entrada in entradas
        ]
