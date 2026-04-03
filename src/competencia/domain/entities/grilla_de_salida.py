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
                ot_programado=ot_inicio + timedelta(minutes=(posicion - 1) * intervalo.minutos),
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
            entrada = grilla_mutable[cambio.performance_id]
            valor_anterior = entrada.posicion if cambio.campo == "posicion" else entrada.andarivel

            if cambio.campo == "posicion":
                posicion_nueva = cambio.valor_nuevo
                posicion_vieja = entrada.posicion
                ocupante_id = next(
                    (
                        performance_id
                        for performance_id, entrada_existente in grilla_mutable.items()
                        if entrada_existente.posicion == posicion_nueva
                        and performance_id != cambio.performance_id
                    ),
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

        nueva_grilla = sorted(grilla_mutable.values(), key=lambda entrada: entrada.posicion)
        if hubo_cambio_posicion and intervalo is not None:
            nueva_grilla = self._recalcular_ots(nueva_grilla, intervalo)

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
            )
            for performance in performances
        ]

    def aplicar_cambios_persistidos(
        self,
        cambios: list[dict[str, Any]],
        intervalo: IntervaloDisciplina | None,
    ) -> None:
        grilla_mutable = {entrada.performance_id: entrada for entrada in self._entradas}
        for cambio in cambios:
            performance_id = UUID(cambio["performance_id"])
            entrada = grilla_mutable[performance_id]
            if cambio["campo"] == "posicion":
                grilla_mutable[performance_id] = EntradaGrilla(
                    performance_id=entrada.performance_id,
                    atleta_id=entrada.atleta_id,
                    posicion=cambio["valor_nuevo"],
                    andarivel=entrada.andarivel,
                    ot_programado=entrada.ot_programado,
                )
            else:
                grilla_mutable[performance_id] = EntradaGrilla(
                    performance_id=entrada.performance_id,
                    atleta_id=entrada.atleta_id,
                    posicion=entrada.posicion,
                    andarivel=cambio["valor_nuevo"],
                    ot_programado=entrada.ot_programado,
                )

        nueva_grilla = sorted(grilla_mutable.values(), key=lambda entrada: entrada.posicion)
        if any(cambio["campo"] == "posicion" for cambio in cambios) and intervalo is not None:
            nueva_grilla = self._recalcular_ots(nueva_grilla, intervalo)

        self._entradas = nueva_grilla

    def _recalcular_ots(
        self,
        entradas: list[EntradaGrilla],
        intervalo: IntervaloDisciplina,
    ) -> list[EntradaGrilla]:
        ot_inicio = min(entrada.ot_programado for entrada in self._entradas)
        return [
            EntradaGrilla(
                performance_id=entrada.performance_id,
                atleta_id=entrada.atleta_id,
                posicion=entrada.posicion,
                andarivel=entrada.andarivel,
                ot_programado=ot_inicio + timedelta(minutes=(entrada.posicion - 1) * intervalo.minutos),
            )
            for entrada in entradas
        ]
