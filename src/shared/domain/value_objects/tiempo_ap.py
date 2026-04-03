"""Value Object TiempoAP — parsing de APs en formato MM:SS a segundos."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class TiempoAP:
    """AP expresado en tiempo, normalizado a segundos."""

    segundos: Decimal

    @classmethod
    def desde_mmss(cls, texto: str) -> "TiempoAP":
        """Parsea MM:SS o HH:MM:SS a segundos."""
        partes = texto.strip().split(":")
        if len(partes) not in (2, 3):
            raise ValueError("FormatoTiempoInvalido: usar MM:SS o HH:MM:SS")
        if any(not parte.isdigit() for parte in partes):
            raise ValueError("FormatoTiempoInvalido: solo se permiten numeros y ':'")

        valores = [int(parte) for parte in partes]
        if len(valores) == 2:
            horas = 0
            minutos, segundos = valores
        else:
            horas, minutos, segundos = valores

        if segundos > 59 or minutos > 59 and len(valores) == 3:
            raise ValueError("FormatoTiempoInvalido: minutos/segundos fuera de rango")

        total = (horas * 3600) + (minutos * 60) + segundos
        return cls.desde_segundos(Decimal(total))

    @classmethod
    def desde_segundos(cls, valor: Decimal) -> "TiempoAP":
        """Construye el VO desde segundos ya normalizados."""
        if valor <= 0:
            raise ValueError("ValorTiempoInvalido: los segundos deben ser > 0")
        return cls(segundos=valor)
