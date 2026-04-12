"""Aggregate Performance — ciclo de vida de la actuación de un atleta."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID

from shared.domain.base.aggregate_root import AggregateRoot
from competencia.domain.aggregates.performance_events import (
    crear_ap_registrado,
    crear_atleta_llamado,
    crear_dns_registrado,
    crear_resultado_corregido,
    crear_resultado_registrado,
    crear_revision_resuelta,
    crear_tarjeta_asignada,
)
from competencia.domain.aggregates.performance_state import reconstituir_performance
from competencia.domain.exceptions import (
    DisciplinaNoAdmitePenalizaciones,  # noqa: F401 - re-export por compatibilidad
    DistanciaBlackoutObligatoria,  # noqa: F401 - re-export por compatibilidad
    DistanciaBlackoutNoAplica,  # noqa: F401 - re-export por compatibilidad
    EstadoInvalidoParaAsignarTarjeta,
    EstadoInvalidoParaCorregirResultado,
    EstadoInvalidoParaLlamar,
    EstadoInvalidoParaRegistrarDNS,
    EstadoInvalidoParaRegistrarResultado,
    EstadoInvalidoParaResolverRevision,
    MotivoDQObligatorio,  # noqa: F401 - re-export por compatibilidad
    MotivoObligatorio,
    PenalizacionesObligatorias,  # noqa: F401 - re-export por compatibilidad
)
from competencia.domain.value_objects.ap import AP
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_performance import EstadoPerformance
from competencia.domain.value_objects.resolucion_tarjeta import ResolucionTarjeta
from competencia.domain.value_objects.rp_final import RPFinal
from competencia.domain.value_objects.tarjeta_asignacion import TarjetaAsignacion
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta
from competencia.domain.value_objects.unidad_medida import UnidadMedida

if TYPE_CHECKING:
    from competencia.domain.value_objects.motivo_dq import MotivoDQ
    from competencia.domain.value_objects.penalizacion_tecnica import PenalizacionTecnica

__all__ = [
    "Performance",
    "DisciplinaNoAdmitePenalizaciones",
    "DistanciaBlackoutObligatoria",
    "DistanciaBlackoutNoAplica",
    "MotivoDQObligatorio",
    "PenalizacionesObligatorias",
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
        self._rp_medido: Decimal | None = None
        self._rp_penalizado: Decimal | None = None
        self._tarjeta: TipoTarjeta | None = None
        self._motivo_dq: MotivoDQ | None = None
        self._motivo_texto: str | None = None
        self._penalizaciones: tuple[PenalizacionTecnica, ...] = ()
        self._estado: EstadoPerformance | None = None
        self._ot_programado: datetime | None = None
        self._posicion_grilla: int | None = None
        self._andarivel: int | None = None
        self._distancia_blackout: Decimal | None = None

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
        """RP efectivo para ranking: penalizado si existe, medido en caso contrario."""
        return self._rp_penalizado if self._rp_penalizado is not None else self._rp_medido

    @property
    def rp_medido(self) -> Decimal | None:
        """RP medido antes de aplicar penalizaciones."""
        return self._rp_medido

    @property
    def rp_penalizado(self) -> Decimal | None:
        """RP final luego de aplicar penalizaciones."""
        return self._rp_penalizado

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
    def penalizaciones(self) -> tuple[PenalizacionTecnica, ...]:
        """Penalizaciones técnicas acumuladas de la performance."""
        return self._penalizaciones

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

    @property
    def ot_programado(self) -> datetime | None:
        """OT programado, disponible tras ser llamado. None si aún no fue llamado."""
        return self._ot_programado

    # ── Comandos de dominio ───────────────────────────────────────────────────

    def registrar_ap(self, valor: Decimal, unidad: UnidadMedida) -> None:
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

        event = crear_ap_registrado(
            performance_id=self._performance_id,
            competencia_id=self._competencia_id,
            participante_id=self._participante_id,
            disciplina=self._disciplina,
            ap=ap,
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

        event = crear_atleta_llamado(
            performance_id=self._performance_id,
            participante_id=self._participante_id,
            disciplina=self._disciplina,
            ot_programado=ot_programado,
            posicion_grilla=posicion_grilla,
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

        event = crear_resultado_registrado(
            performance_id=self._performance_id,
            participante_id=self._participante_id,
            disciplina=self._disciplina,
            valor_rp=valor_rp,
            unidad=unidad,
            registrado_por=registrado_por,
        )
        self._rp = valor_rp
        self._rp_medido = valor_rp
        self._rp_penalizado = None
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

        event = crear_dns_registrado(
            performance_id=self._performance_id,
            participante_id=self._participante_id,
            disciplina=self._disciplina,
            ot_programado=self._ot_programado,
            registrado_por=registrado_por,
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

        event = crear_resultado_corregido(
            performance_id=self._performance_id,
            participante_id=self._participante_id,
            disciplina=self._disciplina,
            valor_rp_anterior=self._rp,
            valor_rp_nuevo=valor_rp,
            unidad=unidad,
            motivo=motivo,
            registrado_por=registrado_por,
        )
        self._aplicar_rp_final(RPFinal.desde_medicion(valor_rp, self._penalizaciones))
        self._record(event)

    def asignar_tarjeta(
        self,
        tipo: TipoTarjeta,
        asignada_por: str,
        motivo_dq: MotivoDQ | None = None,
        motivo_texto: str | None = None,
        distancia_blackout: Decimal | None = None,
        penalizaciones: tuple[PenalizacionTecnica, ...] = (),
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
            penalizaciones: Penalizaciones técnicas para BlancaConPenalizaciones.

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
            penalizaciones=penalizaciones,
        )
        resolucion = ResolucionTarjeta.desde_asignacion(tarjeta_asignacion, self._rp_medido)

        event = crear_tarjeta_asignada(
            performance_id=self._performance_id,
            participante_id=self._participante_id,
            disciplina=self._disciplina,
            resolucion=resolucion,
            asignada_por=asignada_por,
        )
        if tipo == TipoTarjeta.Amarilla:
            self._tarjeta = tipo
            self._motivo_dq = None
            self._motivo_texto = motivo_texto
            self._distancia_blackout = None
            self._penalizaciones = ()
            self._estado = EstadoPerformance.EnRevision
        else:
            self._aplicar_resolucion_tarjeta(resolucion)
        self._record(event)

    def resolver_revision(
        self,
        tipo: TipoTarjeta,
        resuelta_por: str,
        motivo_dq: MotivoDQ | None = None,
        penalizaciones: tuple[PenalizacionTecnica, ...] = (),
    ) -> None:
        """Resuelve una performance que quedó en revisión tras tarjeta amarilla."""
        if self._estado != EstadoPerformance.EnRevision:
            raise EstadoInvalidoParaResolverRevision(
                f"Performance {self._performance_id} en estado {self._estado} "
                "— solo se puede resolver revision desde EnRevision"
            )

        tarjeta_asignacion = TarjetaAsignacion(
            tipo=tipo,
            motivo_dq=motivo_dq,
            motivo_texto=None,
            distancia_blackout=None,
            penalizaciones=penalizaciones,
        )
        resolucion = ResolucionTarjeta.desde_asignacion(tarjeta_asignacion, self._rp_medido)
        event = crear_revision_resuelta(
            performance_id=self._performance_id,
            participante_id=self._participante_id,
            disciplina=self._disciplina,
            resolucion=resolucion,
            resuelta_por=resuelta_por,
        )
        self._aplicar_resolucion_tarjeta(resolucion)
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
        return reconstituir_performance(events)

    def _aplicar_resolucion_tarjeta(self, resolucion: ResolucionTarjeta) -> None:
        self._tarjeta = resolucion.tipo
        self._motivo_dq = resolucion.motivo_dq
        self._motivo_texto = resolucion.motivo_texto
        self._distancia_blackout = resolucion.distancia_blackout
        self._penalizaciones = resolucion.penalizaciones
        self._estado = EstadoPerformance.Ejecutada
        self._aplicar_rp_final(resolucion.rp_final)

    def _aplicar_rp_final(self, rp_final: RPFinal) -> None:
        self._rp_medido = rp_final.medido
        self._rp_penalizado = rp_final.penalizado
        self._rp = rp_final.observable
