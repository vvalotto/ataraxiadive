"""Puertos del dominio de Competencia."""
from competencia.domain.ports.competencia_estado_port import CompetenciaEstadoPort
from competencia.domain.ports.event_store_port import EventStorePort

__all__ = ["CompetenciaEstadoPort", "EventStorePort"]
