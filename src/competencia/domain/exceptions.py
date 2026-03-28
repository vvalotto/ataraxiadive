"""Excepciones de dominio del BC Competencia.

Jerarquía (ADR-013):
    DomainError
    ├── Performance
    │   ├── EstadoInvalidoParaLlamar
    │   ├── EstadoInvalidoParaRegistrarResultado
    │   ├── EstadoInvalidoParaRegistrarDNS
    │   ├── EstadoInvalidoParaAsignarTarjeta
    │   ├── EstadoInvalidoParaCorregirResultado
    │   ├── MotivoObligatorio
    │   └── DistanciaBlackoutObligatoria
    └── Competencia
        ├── IntervaloNoConfigurado
        ├── GrillaYaConfirmada
        ├── GrillaNoGenerada
        ├── PerformanceNoEncontrada
        ├── CompetenciaNoConfirmada
        └── EstadoInvalidoParaGenerarGrilla
"""
from __future__ import annotations


class DomainError(Exception):
    """Base de todas las excepciones de dominio del BC Competencia.

    Permite al API layer capturar cualquier error de dominio con un
    handler genérico sin conocer cada subclase (ADR-012, ADR-013).
    """


# ── Performance ───────────────────────────────────────────────────────────────


class EstadoInvalidoParaLlamar(DomainError):
    """Performance no está en estado AnunciadaAP — no se puede llamar al atleta."""


class EstadoInvalidoParaRegistrarResultado(DomainError):
    """Performance no está en estado Llamada — no se puede registrar el resultado."""


class EstadoInvalidoParaRegistrarDNS(DomainError):
    """Performance no está en estado Llamada — no se puede registrar DNS (INV-P-08)."""


class EstadoInvalidoParaAsignarTarjeta(DomainError):
    """Performance no está en estado ResultadoRegistrado — no se puede asignar tarjeta."""


class EstadoInvalidoParaCorregirResultado(DomainError):
    """Performance no está en estado Ejecutada — no se puede corregir el resultado (INV-P-12/13)."""


class MotivoObligatorio(DomainError):
    """Tarjeta amarilla o roja requieren motivo obligatorio (INV-P-11).
    También aplica a la corrección de resultado (INV-P-12).
    """


class DistanciaBlackoutObligatoria(DomainError):
    """Tarjeta roja con motivo black-out requiere distancia_blackout > 0 (RF-EJ-07)."""


# ── Competencia ───────────────────────────────────────────────────────────────


class IntervaloNoConfigurado(DomainError):
    """Intervalo OT no configurado — no se puede generar la grilla (INV-C-01)."""


class GrillaYaConfirmada(DomainError):
    """La grilla ya fue confirmada — operación no permitida sobre grilla congelada."""


class GrillaNoGenerada(DomainError):
    """La grilla no fue generada aún — ajuste no permitido antes de GenerarGrilla."""


class PerformanceNoEncontrada(DomainError):
    """Performance no encontrada en la grilla — el performanceId no corresponde a ninguna entrada."""


class CompetenciaNoConfirmada(DomainError):
    """Competencia no está en estado Confirmada — no se puede iniciar (INV-C-03)."""


class EstadoInvalidoParaGenerarGrilla(DomainError):
    """Competencia no está en estado válido para generar la grilla."""


class SinPerformancesParaGrilla(DomainError):
    """No hay performances con AP registrado para generar la grilla."""


class CompetenciaNoFinalizable(DomainError):
    """INV-C-04 — no se puede finalizar: quedan performances en AnunciadaAP o Llamada."""
