"""Tests unitarios de AlgoritmoPuntajeFAAS [US-5.6.1]."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from resultados.domain.ports.resultados_competencia_port import ResultadoFinal
from resultados.domain.services.algoritmo_faas import AlgoritmoPuntajeFAAS
from shared.domain.value_objects.disciplina import Disciplina

ANA = uuid4()
LUIS = uuid4()
PEDRO = uuid4()


def _resultado(
    atleta_id: UUID, rp: float | None, tarjeta: str | None, es_dns: bool = False
) -> ResultadoFinal:
    return ResultadoFinal(
        atleta_id=atleta_id,
        rp=Decimal(str(rp)) if rp is not None else None,
        unidad="Metros" if rp is not None else None,
        tarjeta=tarjeta,
        es_dns=es_dns,
    )


@pytest.fixture
def faas() -> AlgoritmoPuntajeFAAS:
    return AlgoritmoPuntajeFAAS()


class TestDistancia:
    def test_proporcional_al_maximo(self, faas: AlgoritmoPuntajeFAAS) -> None:
        resultados = [_resultado(ANA, 70.0, "Blanca"), _resultado(LUIS, 56.0, "Blanca")]
        puntos = faas.calcular(resultados, Disciplina.DNF)
        assert puntos[ANA] == Decimal("100.00")
        assert puntos[LUIS] == Decimal("80.00")

    def test_tres_atletas_proporcional(self, faas: AlgoritmoPuntajeFAAS) -> None:
        resultados = [
            _resultado(ANA, 100.0, "Blanca"),
            _resultado(LUIS, 75.0, "Blanca"),
            _resultado(PEDRO, 50.0, "Blanca"),
        ]
        puntos = faas.calcular(resultados, Disciplina.DNF)
        assert puntos[ANA] == Decimal("100.00")
        assert puntos[LUIS] == Decimal("75.00")
        assert puntos[PEDRO] == Decimal("50.00")

    def test_dns_recibe_cero_y_no_altera_d_max(self, faas: AlgoritmoPuntajeFAAS) -> None:
        resultados = [_resultado(ANA, 70.0, "Blanca"), _resultado(PEDRO, None, None, es_dns=True)]
        puntos = faas.calcular(resultados, Disciplina.DNF)
        assert puntos[ANA] == Decimal("100.00")
        assert puntos[PEDRO] == Decimal("0.00")

    def test_roja_recibe_cero_y_no_altera_d_max(self, faas: AlgoritmoPuntajeFAAS) -> None:
        resultados = [_resultado(ANA, 70.0, "Blanca"), _resultado(LUIS, 60.0, "Roja")]
        puntos = faas.calcular(resultados, Disciplina.DNF)
        assert puntos[ANA] == Decimal("100.00")
        assert puntos[LUIS] == Decimal("0.00")

    def test_todos_invalidos_reciben_cero(self, faas: AlgoritmoPuntajeFAAS) -> None:
        resultados = [
            _resultado(ANA, None, None, es_dns=True),
            _resultado(LUIS, 60.0, "Roja"),
        ]
        puntos = faas.calcular(resultados, Disciplina.DNF)
        assert puntos[ANA] == Decimal("0.00")
        assert puntos[LUIS] == Decimal("0.00")

    def test_dyn_disciplina_distancia(self, faas: AlgoritmoPuntajeFAAS) -> None:
        resultados = [_resultado(ANA, 80.0, "Blanca"), _resultado(LUIS, 40.0, "Blanca")]
        puntos = faas.calcular(resultados, Disciplina.DYN)
        assert puntos[ANA] == Decimal("100.00")
        assert puntos[LUIS] == Decimal("50.00")


class TestTiempo:
    def test_sta_mayor_tiempo_recibe_100(self, faas: AlgoritmoPuntajeFAAS) -> None:
        # STA: mayor tiempo = mejor → ANA(270s) → 100 pts, LUIS(190s) → 0 pts
        resultados = [_resultado(LUIS, 190.0, "Blanca"), _resultado(ANA, 270.0, "Blanca")]
        puntos = faas.calcular(resultados, Disciplina.STA)
        assert puntos[ANA] == Decimal("100.00")
        assert puntos[LUIS] == Decimal("0.00")

    def test_sta_intermedio_proporcional(self, faas: AlgoritmoPuntajeFAAS) -> None:
        # t_min=100, t_max=200. Pedro=150 → (150-100)/(200-100)×100 = 50
        resultados = [
            _resultado(ANA, 100.0, "Blanca"),
            _resultado(LUIS, 200.0, "Blanca"),
            _resultado(PEDRO, 150.0, "Blanca"),
        ]
        puntos = faas.calcular(resultados, Disciplina.STA)
        assert puntos[LUIS] == Decimal("100.00")
        assert puntos[ANA] == Decimal("0.00")
        assert puntos[PEDRO] == Decimal("50.00")

    def test_todos_iguales_reciben_100(self, faas: AlgoritmoPuntajeFAAS) -> None:
        resultados = [_resultado(ANA, 180.0, "Blanca"), _resultado(LUIS, 180.0, "Blanca")]
        puntos = faas.calcular(resultados, Disciplina.STA)
        assert puntos[ANA] == Decimal("100.00")
        assert puntos[LUIS] == Decimal("100.00")

    def test_dns_recibe_cero_en_tiempo(self, faas: AlgoritmoPuntajeFAAS) -> None:
        resultados = [_resultado(ANA, 190.0, "Blanca"), _resultado(PEDRO, None, None, es_dns=True)]
        puntos = faas.calcular(resultados, Disciplina.STA)
        assert puntos[ANA] == Decimal("100.00")
        assert puntos[PEDRO] == Decimal("0.00")

    def test_spe_menor_tiempo_recibe_100(self, faas: AlgoritmoPuntajeFAAS) -> None:
        # SPE: menor tiempo = mejor (velocidad) → ANA(120s) → 100 pts, LUIS(160s) → 0 pts
        resultados = [_resultado(ANA, 120.0, "Blanca"), _resultado(LUIS, 160.0, "Blanca")]
        puntos = faas.calcular(resultados, Disciplina.SPE_4X50)
        assert puntos[ANA] == Decimal("100.00")
        assert puntos[LUIS] == Decimal("0.00")


class TestCasosBorde:
    def test_lista_vacia_retorna_dict_vacio(self, faas: AlgoritmoPuntajeFAAS) -> None:
        puntos = faas.calcular([], Disciplina.DNF)
        assert puntos == {}

    def test_un_solo_atleta_valido_distancia(self, faas: AlgoritmoPuntajeFAAS) -> None:
        resultados = [_resultado(ANA, 50.0, "Blanca")]
        puntos = faas.calcular(resultados, Disciplina.DNF)
        assert puntos[ANA] == Decimal("100.00")

    def test_precision_dos_decimales(self, faas: AlgoritmoPuntajeFAAS) -> None:
        resultados = [_resultado(ANA, 100.0, "Blanca"), _resultado(LUIS, 33.0, "Blanca")]
        puntos = faas.calcular(resultados, Disciplina.DNF)
        # 33/100 × 100 = 33.00
        assert puntos[LUIS] == Decimal("33.00")

    def test_mapa_completo_mismo_tamano_que_input(self, faas: AlgoritmoPuntajeFAAS) -> None:
        resultados = [
            _resultado(ANA, 70.0, "Blanca"),
            _resultado(LUIS, None, None, es_dns=True),
            _resultado(PEDRO, 60.0, "Roja"),
        ]
        puntos = faas.calcular(resultados, Disciplina.DNF)
        assert len(puntos) == 3
        assert ANA in puntos
        assert LUIS in puntos
        assert PEDRO in puntos
