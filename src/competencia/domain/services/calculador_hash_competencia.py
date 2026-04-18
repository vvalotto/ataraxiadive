"""Servicio de dominio para calcular hash SHA-256 de una disciplina."""

from __future__ import annotations

import hashlib
import json
from typing import Any


class CalculadorHashCompetencia:
    """Calcula el hash SHA-256 de una secuencia canónica de eventos."""

    @staticmethod
    def calcular(eventos: list[dict[str, Any]]) -> str:
        """Retorna el hash SHA-256 de la secuencia canónica de eventos."""
        if not eventos:
            return hashlib.sha256(b"").hexdigest()

        jsons_canonicos = [
            json.dumps(CalculadorHashCompetencia._canonizar_evento(evento), sort_keys=True)
            for evento in eventos
        ]
        concatenado = "\n".join(jsons_canonicos).encode("utf-8")
        return hashlib.sha256(concatenado).hexdigest()

    @staticmethod
    def _canonizar_evento(evento: dict[str, Any]) -> dict[str, Any]:
        return {
            "datos": evento["payload"],
            "sequence_number": evento["sequence"],
            "timestamp": evento["occurred_at"],
            "tipo": evento["event_type"],
        }
