"""Aggregate Performance — ciclo de vida de la actuación de un atleta."""
from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from shared.domain.base.aggregate_root import AggregateRoot
from competencia.domain.events.ap_registrado import APRegistrado
from competencia.domain.events.atleta_llamado import AtletaLlamado
from competencia.domain.events.dns_registrado import DNSRegistrado
from competencia.domain.events.resultado_corregido import ResultadoCorregido
from competencia.domain.events.resultado_registrado import ResultadoRegistrado
from competencia.domain.events.tarjeta_asignada import TarjetaAsignada
from competencia.domain.value_objects.ap import AP
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_performance import EstadoPerformance
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta
from competencia.domain.value_objects.unidad_medida import UnidadMedida


class EstadoInvalidoParaLlamar(Exception):
    """Performance no está en estado AnunciadaAP — no se puede llamar al atleta."""


class EstadoInvalidoParaRegistrarResultado(Exception):
    """Performance no está en estado Llamada — no se puede registrar el resultado."""


class EstadoInvalidoParaRegistrarDNS(Exception):
    """Performance no está en estado Llamada — no se puede registrar DNS (INV-P-08)."""


class EstadoInvalidoParaAsignarTarjeta(Exception):
    """Performance no está en estado ResultadoRegistrado — no se puede asignar tarjeta."""


class MotivoObligatorio(Exception):
    """Tarjeta amarilla o roja requieren motivo obligatorio (INV-P-11).
    También aplica a la corrección de resultado (INV-P-12)."""


class EstadoInvalidoParaCorregirResultado(Exception):
    """Performance no está en estado Ejecutada — no se puede corregir el resultado (INV-P-12/13)."""


class Performance(AggregateRoot):
    """Aggregate raíz que modela el ciclo de vida de la actuación de un atleta.

    Stream ID: "performance-{competencia_id}-{participante_id}-{disciplina}"

    Estados:
        AnunciadaAP → Llamada → ResultadoRegistrado → Ejecutada  (camino nominal)
        AnunciadaAP → Llamada → DNS                              (atleta no se presentó)

    Invariantes (ver event-storming-competencia.md):
        INV-P-01: valorAP > 0  (validado por AP value object)
        INV-P-05: llamar() solo si Competencia en EnEjecucion (verificado por handler)
    """

    def __init__(
        self,
        performance_id: UUID,
        competencia_id: UUID,
        participante_id: UUID,
        disciplina: Disciplina,
    ) -> None:
        super().__init__()
        self._performance_id = performance_id
        self._competencia_id = competencia_id
        self._participante_id = participante_id
        self._disciplina = disciplina
        self._ap: AP | None = None
        self._rp: Decimal | None = None
        self._tarjeta: TipoTarjeta | None = None
        self._estado: EstadoPerformance | None = None
        self._ot_programado: datetime | None = None

    # ── Propiedades ───────────────────────────────────────────────────────────

    @property
    def performance_id(self) -> UUID:
        """Identificador único de la Performance."""
        return self._performance_id

    @property
    def estado(self) -> EstadoPerformance | None:
        """Estado actual de la Performance."""
        return self._estado

    @property
    def ap(self) -> AP | None:
        """AP registrado, o None si aún no fue declarado."""
        return self._ap

    @property
    def rp(self) -> Decimal | None:
        """RP registrado, o None si aún no fue registrado."""
        return self._rp

    @property
    def tarjeta(self) -> TipoTarjeta | None:
        """Tarjeta asignada, o None si aún no fue asignada."""
        return self._tarjeta

    # ── Comandos de dominio ───────────────────────────────────────────────────

    def registrarAP(self, valor: Decimal, unidad: UnidadMedida) -> None:
        """Registra el Announced Performance del atleta.

        Valida INV-P-01 a través del value object AP.
        Emite APRegistrado y transiciona al estado AnunciadaAP.

        Args:
            valor: Marca declarada. Debe ser > 0 (INV-P-01).
            unidad: Unidad de medida (Metros | Segundos).

        Raises:
            ValorAPInvalido: Si valor <= 0 (INV-P-01).
        """
        ap = AP(valor=valor, unidad=unidad)  # valida INV-P-01

        event = APRegistrado(
            event_type="APRegistrado",
            aggregate_id=str(self._performance_id),
            occurred_at=APRegistrado.now(),
            performance_id=str(self._performance_id),
            competencia_id=str(self._competencia_id),
            participante_id=str(self._participante_id),
            disciplina=self._disciplina.value,
            valor_ap=str(ap.valor),
            unidad=ap.unidad.value,
        )
        self._ap = ap
        self._estado = EstadoPerformance.AnunciadaAP
        self._record(event)

    def llamar(self, ot_programado: datetime, posicion_grilla: int) -> None:
        """Llama al atleta para que inicie su performance (OT programado).

        Verifica que la Performance esté en estado AnunciadaAP.
        La verificación de INV-P-05 (Competencia en EnEjecucion) es
        responsabilidad del handler, que consulta CompetenciaEstadoPort.

        Args:
            ot_programado: Momento programado para el Official Top.
            posicion_grilla: Número de orden en la grilla de salida.

        Raises:
            EstadoInvalidoParaLlamar: Si la Performance no está en AnunciadaAP.
        """
        if self._estado != EstadoPerformance.AnunciadaAP:
            raise EstadoInvalidoParaLlamar(
                f"Performance {self._performance_id} en estado {self._estado} "
                "— solo se puede llamar desde AnunciadaAP"
            )

        now = AtletaLlamado.now()
        event = AtletaLlamado(
            event_type="AtletaLlamado",
            aggregate_id=str(self._performance_id),
            occurred_at=now,
            performance_id=str(self._performance_id),
            participante_id=str(self._participante_id),
            disciplina=self._disciplina.value,
            posicion_grilla=posicion_grilla,
            ot_programado=ot_programado.isoformat(),
            llamado_en=now.isoformat(),
        )
        self._estado = EstadoPerformance.Llamada
        self._ot_programado = ot_programado
        self._record(event)

    def registrar_resultado(
        self, valor_rp: Decimal, unidad: UnidadMedida, registrado_por: str
    ) -> None:
        """Registra el resultado efectivo (RP) del atleta.

        Verifica que la Performance esté en estado Llamada (INV-P-06).

        Args:
            valor_rp: Realized Performance — marca efectivamente lograda.
            unidad: Unidad de medida del RP (Metros | Segundos).
            registrado_por: Identificador del juez que registra el resultado.

        Raises:
            EstadoInvalidoParaRegistrarResultado: Si la Performance no está en Llamada (INV-P-06).
        """
        if self._estado != EstadoPerformance.Llamada:
            raise EstadoInvalidoParaRegistrarResultado(
                f"Performance {self._performance_id} en estado {self._estado} "
                "— solo se puede registrar resultado desde Llamada"
            )

        now = ResultadoRegistrado.now()
        event = ResultadoRegistrado(
            event_type="ResultadoRegistrado",
            aggregate_id=str(self._performance_id),
            occurred_at=now,
            performance_id=str(self._performance_id),
            participante_id=str(self._participante_id),
            disciplina=self._disciplina.value,
            valor_rp=str(valor_rp),
            unidad=unidad.value,
            registrado_por=registrado_por,
            registrado_en=now.isoformat(),
        )
        self._rp = valor_rp
        self._estado = EstadoPerformance.ResultadoRegistrado
        self._record(event)

    def registrar_dns(self, registrado_por: str) -> None:
        """Registra que el atleta no se presentó al Official Top (DNS).

        Verifica que la Performance esté en estado Llamada (INV-P-08).
        La exclusión mutua con ResultadoRegistrado (INV-P-09) se garantiza
        estructuralmente: desde Llamada no es posible que ya exista un RP.

        Args:
            registrado_por: Identificador del juez que registra el DNS.

        Raises:
            EstadoInvalidoParaRegistrarDNS: Si la Performance no está en Llamada (INV-P-08).
        """
        if self._estado != EstadoPerformance.Llamada:
            raise EstadoInvalidoParaRegistrarDNS(
                f"Performance {self._performance_id} en estado {self._estado} "
                "— solo se puede registrar DNS desde Llamada"
            )

        now = DNSRegistrado.now()
        event = DNSRegistrado(
            event_type="DNSRegistrado",
            aggregate_id=str(self._performance_id),
            occurred_at=now,
            performance_id=str(self._performance_id),
            participante_id=str(self._participante_id),
            disciplina=self._disciplina.value,
            ot_programado=self._ot_programado.isoformat() if self._ot_programado else "",
            registrado_por=registrado_por,
            registrado_en=now.isoformat(),
        )
        self._estado = EstadoPerformance.DNS
        self._record(event)

    def corregir_resultado(
        self, valor_rp: Decimal, unidad: UnidadMedida, registrado_por: str, motivo: str
    ) -> None:
        """Corrige el resultado efectivo (RP) de un atleta ya ejecutado.

        Solo permitido si la Performance está en estado Ejecutada (INV-P-12).
        No permitido si la Performance está en DNS (INV-P-13) — garantizado
        estructuralmente por la verificación de Ejecutada.
        Motivo obligatorio sin excepción (INV-P-12).
        INV-P-15 (ventana de impugnación) diferido a SP3.

        Args:
            valor_rp: Nuevo valor del Realized Performance corregido.
            unidad: Unidad de medida del RP corregido.
            registrado_por: Identificador del juez que realiza la corrección.
            motivo: Razón de la corrección — obligatorio (INV-P-12).

        Raises:
            EstadoInvalidoParaCorregirResultado: Performance no en Ejecutada (INV-P-12/13).
            MotivoObligatorio: motivo ausente o vacío (INV-P-12).
        """
        if self._estado != EstadoPerformance.Ejecutada:
            raise EstadoInvalidoParaCorregirResultado(
                f"Performance {self._performance_id} en estado {self._estado} "
                "— solo se puede corregir el resultado desde Ejecutada"
            )
        if not motivo:
            raise MotivoObligatorio(
                "La corrección de resultado requiere motivo obligatorio (INV-P-12)"
            )

        now = ResultadoCorregido.now()
        event = ResultadoCorregido(
            event_type="ResultadoCorregido",
            aggregate_id=str(self._performance_id),
            occurred_at=now,
            performance_id=str(self._performance_id),
            participante_id=str(self._participante_id),
            disciplina=self._disciplina.value,
            valor_rp_anterior=str(self._rp) if self._rp is not None else "",
            valor_rp_nuevo=str(valor_rp),
            unidad=unidad.value,
            motivo=motivo,
            registrado_por=registrado_por,
            corregido_en=now.isoformat(),
        )
        self._rp = valor_rp
        self._record(event)

    def asignar_tarjeta(
        self, tipo: TipoTarjeta, asignada_por: str, motivo: str | None = None
    ) -> None:
        """Asigna la tarjeta al atleta tras registrar el resultado.

        Verifica que la Performance esté en estado ResultadoRegistrado (INV-P-07).
        Exige motivo si la tarjeta es Amarilla o Roja (INV-P-11).

        Args:
            tipo: Tipo de tarjeta — Blanca, Amarilla o Roja.
            asignada_por: Identificador del juez que asigna la tarjeta.
            motivo: Motivo obligatorio para Amarilla y Roja (INV-P-11).

        Raises:
            EstadoInvalidoParaAsignarTarjeta: Performance no en ResultadoRegistrado (INV-P-07).
            MotivoObligatorio: tarjeta Amarilla o Roja sin motivo (INV-P-11).
        """
        if self._estado != EstadoPerformance.ResultadoRegistrado:
            raise EstadoInvalidoParaAsignarTarjeta(
                f"Performance {self._performance_id} en estado {self._estado} "
                "— solo se puede asignar tarjeta desde ResultadoRegistrado"
            )
        if tipo in (TipoTarjeta.Amarilla, TipoTarjeta.Roja) and not motivo:
            raise MotivoObligatorio(
                f"Tarjeta {tipo} requiere motivo obligatorio (INV-P-11)"
            )

        now = TarjetaAsignada.now()
        event = TarjetaAsignada(
            event_type="TarjetaAsignada",
            aggregate_id=str(self._performance_id),
            occurred_at=now,
            performance_id=str(self._performance_id),
            participante_id=str(self._participante_id),
            disciplina=self._disciplina.value,
            tipo=tipo.value,
            motivo=motivo,
            asignada_por=asignada_por,
            asignada_en=now.isoformat(),
        )
        self._tarjeta = tipo
        self._estado = EstadoPerformance.Ejecutada
        self._record(event)

    # ── Reconstitución desde eventos ──────────────────────────────────────────

    @classmethod
    def reconstitute(cls, events: list[dict[str, Any]]) -> "Performance":
        """Reconstruye el aggregate desde los eventos del Event Store.

        Args:
            events: Lista de registros del Event Store (con event_type, payload).

        Returns:
            Performance con el estado proyectado desde los eventos.

        Raises:
            ValueError: Si la lista de eventos está vacía o el primer evento
                no es APRegistrado.
        """
        if not events:
            raise ValueError("No se puede reconstituir Performance sin eventos")

        first = events[0]
        if first["event_type"] != "APRegistrado":
            raise ValueError(
                f"El primer evento debe ser APRegistrado, recibido: {first['event_type']}"
            )

        payload = cls._parse_payload(first["payload"])
        performance = cls(
            performance_id=UUID(payload["performance_id"]),
            competencia_id=UUID(payload["competencia_id"]),
            participante_id=UUID(payload["participante_id"]),
            disciplina=Disciplina(payload["disciplina"]),
        )

        for event in events:
            performance._apply_stored(event)

        return performance

    def _apply_stored(self, event: dict[str, Any]) -> None:
        """Aplica un evento almacenado al estado interno del aggregate."""
        event_type = event["event_type"]
        payload = self._parse_payload(event["payload"])

        if event_type == "APRegistrado":
            self._ap = AP(
                valor=Decimal(payload["valor_ap"]),
                unidad=UnidadMedida(payload["unidad"]),
            )
            self._estado = EstadoPerformance.AnunciadaAP
        elif event_type == "AtletaLlamado":
            self._estado = EstadoPerformance.Llamada
            self._ot_programado = datetime.fromisoformat(payload["ot_programado"])
        elif event_type == "ResultadoRegistrado":
            self._rp = Decimal(payload["valor_rp"])
            self._estado = EstadoPerformance.ResultadoRegistrado
        elif event_type == "DNSRegistrado":
            self._estado = EstadoPerformance.DNS
        elif event_type == "TarjetaAsignada":
            self._tarjeta = TipoTarjeta(payload["tipo"])
            self._estado = EstadoPerformance.Ejecutada
        elif event_type == "ResultadoCorregido":
            self._rp = Decimal(payload["valor_rp_nuevo"])

    @staticmethod
    def _parse_payload(payload: Any) -> dict[str, Any]:
        """Parsea el payload del Event Store (puede ser str JSON o dict)."""
        if isinstance(payload, str):
            return json.loads(payload)  # type: ignore[no-any-return]
        return payload  # type: ignore[return-value]
