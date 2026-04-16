"""Tests unitarios de CalculadorHashCompetencia."""

from __future__ import annotations

from competencia.domain.services.calculador_hash_competencia import CalculadorHashCompetencia


def _evento(sequence: int, event_type: str, payload: dict, occurred_at: str) -> dict:
    return {
        "sequence": sequence,
        "stream_id": "performance-cid-pid-STA",
        "event_type": event_type,
        "payload": payload,
        "occurred_at": occurred_at,
    }


def test_hash_es_determinista_para_misma_secuencia() -> None:
    eventos = [
        _evento(1, "APRegistrado", {"valor_ap": "300"}, "2026-04-16T10:00:00Z"),
        _evento(2, "ResultadoRegistrado", {"valor_rp": "295"}, "2026-04-16T10:05:00Z"),
    ]

    hash_a = CalculadorHashCompetencia.calcular(eventos)
    hash_b = CalculadorHashCompetencia.calcular(eventos)

    assert hash_a == hash_b
    assert len(hash_a) == 64


def test_hash_cambia_si_cambia_payload() -> None:
    eventos = [
        _evento(1, "APRegistrado", {"valor_ap": "300"}, "2026-04-16T10:00:00Z"),
    ]
    eventos_modificados = [
        _evento(1, "APRegistrado", {"valor_ap": "301"}, "2026-04-16T10:00:00Z"),
    ]

    assert CalculadorHashCompetencia.calcular(eventos) != CalculadorHashCompetencia.calcular(
        eventos_modificados
    )


def test_hash_conjunto_vacio_es_sha256_de_cadena_vacia() -> None:
    assert (
        CalculadorHashCompetencia.calcular([])
        == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )
