"""Entidad GrillaDeSalida — encapsula la logica de orden y ajustes de grilla."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from competencia.domain.ports.performances_ap_port import PerformancesAPData
from competencia.domain.value_objects.cambio_grilla import CambioGrilla
from competencia.domain.value_objects.disciplina_descriptor import DisciplinaDescriptor
from competencia.domain.value_objects.entrada_grilla import EntradaGrilla
from competencia.domain.value_objects.intervalo_disciplina import IntervaloDisciplina


class GrillaDeSalida:
    """Entidad interna del aggregate Competencia para modelar la grilla."""

    def __init__(self, entradas: list[EntradaGrilla] | None = None) -> None:
        self._entradas = list(entradas or [])

    @property
    def esta_generada(self) -> bool:
        return bool(self._entradas)

    @property
    def entradas(self) -> list[EntradaGrilla]:
        return list(self._entradas)

    def generar(
        self,
        ot_inicio: datetime,
        performances: list[PerformancesAPData],
        descriptor: DisciplinaDescriptor,
        intervalo: IntervaloDisciplina,
        andariveles: int,
    ) -> list[EntradaGrilla]:
        ordenadas = sorted(
            performances,
            key=lambda performance: performance.valor_ap,
            reverse=not descriptor.orden_ascendente,
        )
        self._entradas = [
            EntradaGrilla(
                performance_id=perf.performance_id,
                atleta_id=perf.atleta_id,
                posicion=posicion,
                andarivel=((posicion - 1) % andariveles) + 1,
                ot_programado=ot_inicio
                + timedelta(
                    minutes=self._grupo_salida_para_posicion(posicion, andariveles)
                    * intervalo.minutos
                ),
                juez_id=None,
            )
            for posicion, perf in enumerate(ordenadas, start=1)
        ]
        return self.entradas

    def ajustar(
        self,
        cambios: list[CambioGrilla],
        intervalo: IntervaloDisciplina | None,
    ) -> tuple[list[EntradaGrilla], list[dict[str, object]]]:
        grilla_mutable = {entrada.performance_id: entrada for entrada in self._entradas}
        cambios_payload: list[dict[str, object]] = []
        hubo_cambio_posicion = False

        for cambio in cambios:
            if cambio.campo == "posicion":
                cambios_payload.extend(self._aplicar_cambio_posicion(grilla_mutable, cambio))
                hubo_cambio_posicion = True
            else:
                cambios_payload.append(self._aplicar_cambio_andarivel(grilla_mutable, cambio))

        nueva_grilla = self._ordenar_y_recalcular(
            list(grilla_mutable.values()),
            intervalo,
            hubo_cambio_posicion,
        )

        self._entradas = nueva_grilla
        return self.entradas, cambios_payload

    def cargar_desde_payload(self, performances: list[dict[str, Any]]) -> None:
        self._entradas = [
            EntradaGrilla(
                performance_id=UUID(performance["performance_id"]),
                atleta_id=UUID(performance["atleta_id"]),
                posicion=performance["posicion"],
                andarivel=performance["andarivel"],
                ot_programado=datetime.fromisoformat(performance["ot_programado"]),
                juez_id=performance.get("juez_id"),
            )
            for performance in performances
        ]

    def aplicar_cambios_persistidos(
        self,
        cambios: list[dict[str, Any]],
        intervalo: IntervaloDisciplina | None,
    ) -> None:
        grilla_mutable = {entrada.performance_id: entrada for entrada in self._entradas}
        hubo_cambio_posicion = False
        for cambio in cambios:
            self._aplicar_cambio_persistido(grilla_mutable, cambio)
            hubo_cambio_posicion = hubo_cambio_posicion or cambio["campo"] == "posicion"

        nueva_grilla = self._ordenar_y_recalcular(
            list(grilla_mutable.values()),
            intervalo,
            hubo_cambio_posicion,
        )

        self._entradas = nueva_grilla

    def _aplicar_cambio_posicion(
        self,
        grilla_mutable: dict[UUID, EntradaGrilla],
        cambio: CambioGrilla,
    ) -> list[dict[str, object]]:
        entrada = grilla_mutable[cambio.performance_id]
        posicion_nueva = cambio.valor_nuevo
        posicion_vieja = entrada.posicion
        cambios_payload: list[dict[str, object]] = []
        ocupante_id = self._buscar_ocupante_posicion(
            grilla_mutable,
            posicion_nueva,
            cambio.performance_id,
        )

        if ocupante_id is not None:
            ocupante = grilla_mutable[ocupante_id]
            grilla_mutable[ocupante_id] = self._reemplazar_entrada(
                ocupante,
                posicion=posicion_vieja,
            )
            cambios_payload.append(
                self._crear_cambio_payload(ocupante_id, "posicion", posicion_nueva, posicion_vieja)
            )

        grilla_mutable[cambio.performance_id] = self._reemplazar_entrada(
            entrada,
            posicion=posicion_nueva,
        )
        cambios_payload.append(
            self._crear_cambio_payload(
                cambio.performance_id,
                "posicion",
                posicion_vieja,
                posicion_nueva,
            )
        )
        return cambios_payload

    def _aplicar_cambio_andarivel(
        self,
        grilla_mutable: dict[UUID, EntradaGrilla],
        cambio: CambioGrilla,
    ) -> dict[str, object]:
        entrada = grilla_mutable[cambio.performance_id]
        grilla_mutable[cambio.performance_id] = self._reemplazar_entrada(
            entrada,
            andarivel=cambio.valor_nuevo,
        )
        return self._crear_cambio_payload(
            cambio.performance_id,
            "andarivel",
            entrada.andarivel,
            cambio.valor_nuevo,
        )

    def asignar_juez(self, performance_id: UUID, juez_id: str) -> None:
        self._entradas = [
            (
                self._reemplazar_entrada(entrada, juez_id=juez_id)
                if entrada.performance_id == performance_id
                else entrada
            )
            for entrada in self._entradas
        ]

    def _aplicar_cambio_persistido(
        self,
        grilla_mutable: dict[UUID, EntradaGrilla],
        cambio: dict[str, Any],
    ) -> None:
        performance_id = UUID(cambio["performance_id"])
        entrada = grilla_mutable[performance_id]
        if cambio["campo"] == "posicion":
            grilla_mutable[performance_id] = self._reemplazar_entrada(
                entrada,
                posicion=cambio["valor_nuevo"],
            )
            return
        grilla_mutable[performance_id] = self._reemplazar_entrada(
            entrada,
            andarivel=cambio["valor_nuevo"],
        )

    def _ordenar_y_recalcular(
        self,
        entradas: list[EntradaGrilla],
        intervalo: IntervaloDisciplina | None,
        hubo_cambio_posicion: bool,
    ) -> list[EntradaGrilla]:
        nueva_grilla = sorted(entradas, key=lambda entrada: entrada.posicion)
        if hubo_cambio_posicion and intervalo is not None:
            return self._recalcular_ots(nueva_grilla, intervalo)
        return nueva_grilla

    @staticmethod
    def _buscar_ocupante_posicion(
        grilla_mutable: dict[UUID, EntradaGrilla],
        posicion: int,
        performance_id_excluido: UUID,
    ) -> UUID | None:
        return next(
            (
                performance_id
                for performance_id, entrada in grilla_mutable.items()
                if entrada.posicion == posicion and performance_id != performance_id_excluido
            ),
            None,
        )

    @staticmethod
    def _reemplazar_entrada(
        entrada: EntradaGrilla,
        *,
        posicion: int | None = None,
        andarivel: int | None = None,
        juez_id: str | None = None,
    ) -> EntradaGrilla:
        return EntradaGrilla(
            performance_id=entrada.performance_id,
            atleta_id=entrada.atleta_id,
            posicion=entrada.posicion if posicion is None else posicion,
            andarivel=entrada.andarivel if andarivel is None else andarivel,
            ot_programado=entrada.ot_programado,
            juez_id=entrada.juez_id if juez_id is None else juez_id,
        )

    @staticmethod
    def _crear_cambio_payload(
        performance_id: UUID,
        campo: str,
        valor_anterior: int,
        valor_nuevo: int,
    ) -> dict[str, object]:
        return {
            "performance_id": str(performance_id),
            "campo": campo,
            "valor_anterior": valor_anterior,
            "valor_nuevo": valor_nuevo,
        }

    def _recalcular_ots(
        self,
        entradas: list[EntradaGrilla],
        intervalo: IntervaloDisciplina,
    ) -> list[EntradaGrilla]:
        ot_inicio = min(entrada.ot_programado for entrada in self._entradas)
        andariveles = max(entrada.andarivel for entrada in self._entradas)
        return [
            EntradaGrilla(
                performance_id=entrada.performance_id,
                atleta_id=entrada.atleta_id,
                posicion=entrada.posicion,
                andarivel=entrada.andarivel,
                ot_programado=ot_inicio
                + timedelta(
                    minutes=self._grupo_salida_para_posicion(entrada.posicion, andariveles)
                    * intervalo.minutos
                ),
                juez_id=entrada.juez_id,
            )
            for entrada in entradas
        ]

    @staticmethod
    def _grupo_salida_para_posicion(posicion: int, andariveles: int) -> int:
        return (posicion - 1) // andariveles
