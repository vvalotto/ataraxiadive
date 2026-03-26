"""Aggregate Competencia — ciclo de vida de una disciplina en un torneo."""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from shared.domain.base.aggregate_root import AggregateRoot
from competencia.domain.events.competencia_iniciada import CompetenciaIniciada
from competencia.domain.events.grilla_confirmada import GrillaConfirmada
from competencia.domain.events.grilla_de_salida_ajustada import GrillaDeSalidaAjustada
from competencia.domain.events.grilla_de_salida_generada import GrillaDeSalidaGenerada
from competencia.domain.events.intervalo_ot_configurado import IntervaloOTConfigurado
from competencia.domain.exceptions import (
    CompetenciaNoConfirmada,
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
from competencia.domain.value_objects.entrada_grilla import EntradaGrilla
from competencia.domain.value_objects.estado_competencia import EstadoCompetencia
from competencia.domain.value_objects.intervalo_disciplina import IntervaloDisciplina


class Competencia(AggregateRoot):
    """Aggregate raíz que modela el ciclo de vida de una disciplina en un torneo.

    Stream ID: "competencia-{competencia_id}"

    Estados:
        Preparacion → Confirmada → EnEjecucion → Finalizada

    Invariantes:
        INV-C-01: intervaloDisciplina debe estar configurado antes de GenerarGrilla.
    """

    def __init__(
        self,
        competencia_id: UUID,
        disciplina: Disciplina,
    ) -> None:
        super().__init__()
        self._competencia_id = competencia_id
        self._disciplina = disciplina
        self._estado: EstadoCompetencia = EstadoCompetencia.Preparacion
        self._intervalo: IntervaloDisciplina | None = None
        self._grilla_confirmada: bool = False
        self._grilla: list[EntradaGrilla] = []

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
    def grilla(self) -> list[EntradaGrilla]:
        """Grilla de salida actual (última generada), o lista vacía si no fue generada."""
        return list(self._grilla)

    @property
    def grilla_confirmada(self) -> bool:
        """True si la grilla fue confirmada de forma irreversible."""
        return self._grilla_confirmada

    # ── Comandos de dominio ───────────────────────────────────────────────────

    def configurar_intervalo_ot(
        self, intervalo_minutos: int, configurado_por: str
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

        event = IntervaloOTConfigurado(
            event_type="IntervaloOTConfigurado",
            aggregate_id=str(self._competencia_id),
            occurred_at=IntervaloOTConfigurado.now(),
            competencia_id=str(self._competencia_id),
            disciplina=self._disciplina.value,
            intervalo_minutos=intervalo.minutos,
            configurado_por=configurado_por,
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
                f"Competencia {self._competencia_id}: grilla confirmada — "
                "no se puede regenerar"
            )
        if not performances:
            raise SinPerformancesParaGrilla(
                f"Competencia {self._competencia_id}: no hay performances con AP"
            )

        ordenadas = _ordenar_performances(performances, descriptor)
        now = GrillaDeSalidaGenerada.now()

        entradas = []
        perf_payloads = []
        for posicion, perf in enumerate(ordenadas, start=1):
            ot_atleta = ot_inicio + timedelta(
                minutes=(posicion - 1) * self._intervalo.minutos
            )
            andarivel = _calcular_andarivel(posicion, andariveles)
            entradas.append(
                EntradaGrilla(
                    performance_id=perf.performance_id,
                    atleta_id=perf.atleta_id,
                    posicion=posicion,
                    andarivel=andarivel,
                    ot_programado=ot_atleta,
                )
            )
            perf_payloads.append(
                {
                    "performance_id": str(perf.performance_id),
                    "atleta_id": str(perf.atleta_id),
                    "posicion": posicion,
                    "andarivel": andarivel,
                    "ot_programado": ot_atleta.isoformat(),
                }
            )

        event = GrillaDeSalidaGenerada(
            event_type="GrillaDeSalidaGenerada",
            aggregate_id=str(self._competencia_id),
            occurred_at=now,
            competencia_id=str(self._competencia_id),
            disciplina=self._disciplina.value,
            ot_inicio=ot_inicio.isoformat(),
            performances=tuple(perf_payloads),
            generada_en=now.isoformat(),
        )
        self._grilla = entradas
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
        if not self._grilla:
            raise GrillaNoGenerada(
                f"Competencia {self._competencia_id}: grilla no generada — "
                "ejecutar generar_grilla() antes de ajustar"
            )
        if self._grilla_confirmada:
            raise GrillaYaConfirmada(
                f"Competencia {self._competencia_id}: INV-C-02 — "
                "grilla confirmada, ajuste no permitido"
            )

        grilla_por_id = {e.performance_id: e for e in self._grilla}
        for cambio in cambios:
            if cambio.performance_id not in grilla_por_id:
                raise PerformanceNoEncontrada(
                    f"Competencia {self._competencia_id}: performance "
                    f"{cambio.performance_id} no encontrada en la grilla"
                )

        grilla_mutable = {e.performance_id: e for e in self._grilla}
        cambios_payload: list[dict[str, object]] = []
        hubo_cambio_posicion = False

        for cambio in cambios:
            entrada = grilla_mutable[cambio.performance_id]
            valor_anterior = (
                entrada.posicion if cambio.campo == "posicion" else entrada.andarivel
            )
            if cambio.campo == "posicion":
                posicion_nueva = cambio.valor_nuevo
                posicion_vieja = entrada.posicion
                # Si la posición destino está ocupada, desplazar al ocupante
                ocupante_id = next(
                    (pid for pid, e in grilla_mutable.items()
                     if e.posicion == posicion_nueva and pid != cambio.performance_id),
                    None,
                )
                if ocupante_id is not None:
                    ocupante = grilla_mutable[ocupante_id]
                    grilla_mutable[ocupante_id] = EntradaGrilla(
                        performance_id=ocupante.performance_id,
                        atleta_id=ocupante.atleta_id,
                        posicion=posicion_vieja,
                        andarivel=ocupante.andarivel,
                        ot_programado=ocupante.ot_programado,
                    )
                    cambios_payload.append(
                        {
                            "performance_id": str(ocupante_id),
                            "campo": "posicion",
                            "valor_anterior": posicion_nueva,
                            "valor_nuevo": posicion_vieja,
                        }
                    )
                grilla_mutable[cambio.performance_id] = EntradaGrilla(
                    performance_id=entrada.performance_id,
                    atleta_id=entrada.atleta_id,
                    posicion=posicion_nueva,
                    andarivel=entrada.andarivel,
                    ot_programado=entrada.ot_programado,
                )
                hubo_cambio_posicion = True
            else:
                grilla_mutable[cambio.performance_id] = EntradaGrilla(
                    performance_id=entrada.performance_id,
                    atleta_id=entrada.atleta_id,
                    posicion=entrada.posicion,
                    andarivel=cambio.valor_nuevo,
                    ot_programado=entrada.ot_programado,
                )
            cambios_payload.append(
                {
                    "performance_id": str(cambio.performance_id),
                    "campo": cambio.campo,
                    "valor_anterior": valor_anterior,
                    "valor_nuevo": cambio.valor_nuevo,
                }
            )

        nueva_grilla = sorted(grilla_mutable.values(), key=lambda e: e.posicion)

        if hubo_cambio_posicion and self._intervalo is not None:
            ot_inicio = min(e.ot_programado for e in self._grilla)
            nueva_grilla = [
                EntradaGrilla(
                    performance_id=e.performance_id,
                    atleta_id=e.atleta_id,
                    posicion=e.posicion,
                    andarivel=e.andarivel,
                    ot_programado=ot_inicio + timedelta(
                        minutes=(e.posicion - 1) * self._intervalo.minutos
                    ),
                )
                for e in nueva_grilla
            ]

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
        self._grilla = nueva_grilla
        self._record(event)

    def confirmar_grilla(self) -> None:
        """Confirma la Grilla de Salida, congelándola de forma irreversible (INV-C-02).

        Después de este evento, GenerarGrilla, AjustarGrilla y ConfigurarIntervaloOT
        quedan bloqueados. Transiciona el estado a Confirmada.

        Raises:
            GrillaNoGenerada: Si la grilla no fue generada aún.
            GrillaYaConfirmada: Si la grilla ya fue confirmada previamente.
        """
        if not self._grilla:
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
        }

        handler = _handlers.get(event_type)
        if handler is not None:
            handler(payload)

    def _apply_intervalo_ot_configurado(self, payload: dict[str, Any]) -> None:
        self._intervalo = IntervaloDisciplina(minutos=payload["intervalo_minutos"])

    def _apply_grilla_de_salida_generada(self, payload: dict[str, Any]) -> None:
        self._grilla = [
            EntradaGrilla(
                performance_id=UUID(p["performance_id"]),
                atleta_id=UUID(p["atleta_id"]),
                posicion=p["posicion"],
                andarivel=p["andarivel"],
                ot_programado=datetime.fromisoformat(p["ot_programado"]),
            )
            for p in payload["performances"]
        ]

    def _apply_grilla_de_salida_ajustada(self, payload: dict[str, Any]) -> None:
        grilla_por_id = {e.performance_id: e for e in self._grilla}
        for cambio in payload["cambios"]:
            pid = UUID(cambio["performance_id"])
            entrada = grilla_por_id[pid]
            if cambio["campo"] == "posicion":
                grilla_por_id[pid] = EntradaGrilla(
                    performance_id=entrada.performance_id,
                    atleta_id=entrada.atleta_id,
                    posicion=cambio["valor_nuevo"],
                    andarivel=entrada.andarivel,
                    ot_programado=entrada.ot_programado,
                )
            else:
                grilla_por_id[pid] = EntradaGrilla(
                    performance_id=entrada.performance_id,
                    atleta_id=entrada.atleta_id,
                    posicion=entrada.posicion,
                    andarivel=cambio["valor_nuevo"],
                    ot_programado=entrada.ot_programado,
                )
        nueva_grilla = sorted(grilla_por_id.values(), key=lambda e: e.posicion)
        hubo_cambio_posicion = any(c["campo"] == "posicion" for c in payload["cambios"])
        if hubo_cambio_posicion and self._intervalo is not None:
            ot_inicio = min(e.ot_programado for e in self._grilla)
            nueva_grilla = [
                EntradaGrilla(
                    performance_id=e.performance_id,
                    atleta_id=e.atleta_id,
                    posicion=e.posicion,
                    andarivel=e.andarivel,
                    ot_programado=ot_inicio + timedelta(
                        minutes=(e.posicion - 1) * self._intervalo.minutos
                    ),
                )
                for e in nueva_grilla
            ]
        self._grilla = nueva_grilla

    def _apply_grilla_confirmada(self, payload: dict[str, Any]) -> None:  # noqa: ARG002
        self._grilla_confirmada = True
        self._estado = EstadoCompetencia.Confirmada

    def _apply_competencia_iniciada(self, payload: dict[str, Any]) -> None:  # noqa: ARG002
        self._estado = EstadoCompetencia.EnEjecucion

    @staticmethod
    def _parse_payload(payload: Any) -> dict[str, Any]:
        """Parsea el payload del Event Store (puede ser str JSON o dict)."""
        if isinstance(payload, str):
            return json.loads(payload)  # type: ignore[no-any-return]
        return payload  # type: ignore[return-value]


# ── Helpers de dominio ────────────────────────────────────────────────────────


def _ordenar_performances(
    performances: list[PerformancesAPData], descriptor: DisciplinaDescriptor
) -> list[PerformancesAPData]:
    """Ordena las performances según la política P-01.

    STA (tiempo): AP mayor → menor (primero el que declara más tiempo).
    Distancia: AP menor → mayor (primero el más conservador).
    """
    return sorted(performances, key=lambda p: p.valor_ap, reverse=not descriptor.orden_ascendente)


def _calcular_andarivel(posicion: int, total_andariveles: int) -> int:
    """Asigna andarivel round-robin por posición.

    Con 1 andarivel: todos en andarivel 1.
    Con N andariveles: posicion 1→1, 2→2, ..., N→N, N+1→1, ...
    """
    return ((posicion - 1) % total_andariveles) + 1
