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
from competencia.domain.exceptions import (
    DistanciaBlackoutObligatoria,  # noqa: F401 - re-export por compatibilidad
    DistanciaBlackoutNoAplica,  # noqa: F401 - re-export por compatibilidad
    EstadoInvalidoParaAsignarTarjeta,
    EstadoInvalidoParaCorregirResultado,
    EstadoInvalidoParaLlamar,
    EstadoInvalidoParaRegistrarDNS,
    EstadoInvalidoParaRegistrarResultado,
    MotivoDQObligatorio,  # noqa: F401 - re-export por compatibilidad
    MotivoObligatorio,
)
from competencia.domain.value_objects.ap import AP
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_performance import EstadoPerformance
from competencia.domain.value_objects.motivo_dq import MotivoDQ
from competencia.domain.value_objects.tarjeta_asignacion import TarjetaAsignacion
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta
from competencia.domain.value_objects.unidad_medida import UnidadMedida

__all__ = [
    "Performance",
    "DistanciaBlackoutObligatoria",
    "DistanciaBlackoutNoAplica",
    "MotivoDQObligatorio",
]


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
        self._motivo_dq: MotivoDQ | None = None
        self._motivo_texto: str | None = None
        self._estado: EstadoPerformance | None = None
        self._ot_programado: datetime | None = None
        self._posicion_grilla: int | None = None
        self._andarivel: int | None = None
        self._distancia_blackout: Decimal | None = None
        self._event_handlers: dict[str, Any] = {
            "APRegistrado": self._apply_ap_registrado,
            "AtletaLlamado": self._apply_atleta_llamado,
            "ResultadoRegistrado": self._apply_resultado_registrado,
            "DNSRegistrado": self._apply_dns_registrado,
            "TarjetaAsignada": self._apply_tarjeta_asignada,
            "ResultadoCorregido": self._apply_resultado_corregido,
        }

    # ── Propiedades ───────────────────────────────────────────────────────────

    @property
    def performance_id(self) -> UUID:
        """Identificador único de la Performance."""
        return self._performance_id

    @property
    def participante_id(self) -> UUID:
        """Identificador del participante asociado a esta Performance."""
        return self._participante_id

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

    @property
    def disciplina(self) -> Disciplina:
        """Disciplina de esta Performance."""
        return self._disciplina

    @property
    def motivo_dq(self) -> MotivoDQ | None:
        """Motivo formal de DQ asociado a la tarjeta roja."""
        return self._motivo_dq

    @property
    def motivo_texto(self) -> str | None:
        """Motivo textual libre asociado a la tarjeta."""
        return self._motivo_texto

    @property
    def posicion_grilla(self) -> int | None:
        """Posicion en la grilla de salida.

        Disponible tras ser llamado. None si aun no fue llamado.
        """
        return self._posicion_grilla

    @property
    def andarivel(self) -> int | None:
        """Número de andarivel asignado, disponible tras ser llamado. None si aún no fue llamado."""
        return self._andarivel

    @property
    def distancia_blackout(self) -> Decimal | None:
        """Distancia alcanzada en black-out, o None si no aplica."""
        return self._distancia_blackout

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

    def llamar(self, ot_programado: datetime, posicion_grilla: int, andarivel: int = 1) -> None:
        """Llama al atleta para que inicie su performance (OT programado).

        Verifica que la Performance esté en estado AnunciadaAP.
        La verificación de INV-P-05 (Competencia en EnEjecucion) y
        INV-C-05 (andarivel libre) es responsabilidad del handler.

        Args:
            ot_programado: Momento programado para el Official Top.
            posicion_grilla: Número de orden en la grilla de salida.
            andarivel: Número de andarivel asignado (default 1).

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
            andarivel=andarivel,
        )
        self._estado = EstadoPerformance.Llamada
        self._ot_programado = ot_programado
        self._andarivel = andarivel
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
        self,
        tipo: TipoTarjeta,
        asignada_por: str,
        motivo_dq: MotivoDQ | None = None,
        motivo_texto: str | None = None,
        distancia_blackout: Decimal | None = None,
    ) -> None:
        """Asigna la tarjeta al atleta tras registrar el resultado.

        Verifica que la Performance esté en estado ResultadoRegistrado (INV-P-07).
        Exige `motivo_texto` si la tarjeta es Amarilla (INV-P-11b).
        Exige `motivo_dq` si la tarjeta es Roja (INV-P-11).
        Exige distancia_blackout > 0 solo para motivos de blackout.

        Args:
            tipo: Tipo de tarjeta — Blanca, Amarilla o Roja.
            asignada_por: Identificador del juez que asigna la tarjeta.
            motivo_dq: Motivo reglamentario obligatorio para Roja.
            motivo_texto: Motivo libre obligatorio para Amarilla.
            distancia_blackout: Distancia alcanzada — obligatoria para motivos BKO.

        Raises:
            EstadoInvalidoParaAsignarTarjeta:
                Performance no en ResultadoRegistrado (INV-P-07).
            MotivoObligatorio: tarjeta Amarilla sin motivo libre.
            MotivoDQObligatorio: tarjeta Roja sin motivo reglamentario.
            DistanciaBlackoutObligatoria: blackout sin distancia o distancia <= 0.
            DistanciaBlackoutNoAplica: distancia informada para motivo sin blackout.
        """
        if self._estado != EstadoPerformance.ResultadoRegistrado:
            raise EstadoInvalidoParaAsignarTarjeta(
                f"Performance {self._performance_id} en estado {self._estado} "
                "— solo se puede asignar tarjeta desde ResultadoRegistrado"
            )

        tarjeta_asignacion = TarjetaAsignacion(
            tipo=tipo,
            motivo_dq=motivo_dq,
            motivo_texto=motivo_texto,
            distancia_blackout=distancia_blackout,
        )

        now = TarjetaAsignada.now()
        event = TarjetaAsignada(
            event_type="TarjetaAsignada",
            aggregate_id=str(self._performance_id),
            occurred_at=now,
            performance_id=str(self._performance_id),
            participante_id=str(self._participante_id),
            disciplina=self._disciplina.value,
            tipo=tarjeta_asignacion.tipo.value,
            motivo_dq_codigo=(
                tarjeta_asignacion.motivo_dq.value if tarjeta_asignacion.motivo_dq else None
            ),
            motivo_texto=tarjeta_asignacion.motivo_texto,
            asignada_por=asignada_por,
            asignada_en=now.isoformat(),
            distancia_blackout=(
                str(tarjeta_asignacion.distancia_blackout)
                if tarjeta_asignacion.distancia_blackout is not None
                else None
            ),
        )
        self._tarjeta = tarjeta_asignacion.tipo
        self._motivo_dq = tarjeta_asignacion.motivo_dq
        self._motivo_texto = tarjeta_asignacion.motivo_texto
        self._distancia_blackout = tarjeta_asignacion.distancia_blackout
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
        """Aplica un evento almacenado al estado interno del aggregate.

        Usa dispatch por tipo de evento (OCP: agregar un tipo nuevo no requiere
        modificar este método, solo registrar el handler en _event_handlers).
        """
        event_type = event["event_type"]
        payload = self._parse_payload(event["payload"])
        handler = self._event_handlers.get(event_type)
        if handler is not None:
            handler(payload)

    def _apply_ap_registrado(self, payload: dict[str, Any]) -> None:
        self._ap = AP(
            valor=Decimal(payload["valor_ap"]),
            unidad=UnidadMedida(payload["unidad"]),
        )
        self._estado = EstadoPerformance.AnunciadaAP

    def _apply_atleta_llamado(self, payload: dict[str, Any]) -> None:
        self._estado = EstadoPerformance.Llamada
        self._ot_programado = datetime.fromisoformat(payload["ot_programado"])
        self._posicion_grilla = payload["posicion_grilla"]
        self._andarivel = payload.get("andarivel", 1)

    def _apply_resultado_registrado(self, payload: dict[str, Any]) -> None:
        self._rp = Decimal(payload["valor_rp"])
        self._estado = EstadoPerformance.ResultadoRegistrado

    def _apply_dns_registrado(self, payload: dict[str, Any]) -> None:  # noqa: ARG002
        self._estado = EstadoPerformance.DNS

    def _apply_tarjeta_asignada(self, payload: dict[str, Any]) -> None:
        self._tarjeta = TipoTarjeta(payload["tipo"])
        self._estado = EstadoPerformance.Ejecutada
        legacy_motivo = payload.get("motivo")
        motivo_dq_codigo = payload.get("motivo_dq_codigo")
        self._motivo_texto = payload.get("motivo_texto")

        if motivo_dq_codigo:
            self._motivo_dq = MotivoDQ(motivo_dq_codigo)
        elif legacy_motivo == "black-out":
            self._motivo_dq = MotivoDQ.BKO_SUPERFICIE
        elif isinstance(legacy_motivo, str):
            self._motivo_texto = legacy_motivo

        if payload.get("distancia_blackout") is not None:
            self._distancia_blackout = Decimal(payload["distancia_blackout"])

    def _apply_resultado_corregido(self, payload: dict[str, Any]) -> None:
        self._rp = Decimal(payload["valor_rp_nuevo"])

    @staticmethod
    def _parse_payload(payload: Any) -> dict[str, Any]:
        """Parsea el payload del Event Store (puede ser str JSON o dict)."""
        if isinstance(payload, str):
            return json.loads(payload)  # type: ignore[no-any-return]
        return payload  # type: ignore[return-value]
