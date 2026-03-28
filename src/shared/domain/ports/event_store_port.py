"""Puerto EventStore — contrato de persistencia de eventos (cross-BC)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class EventStorePort(ABC):
    """Puerto de persistencia de eventos.

    Contrato que define las operaciones de lectura y escritura del Event Store.
    La infraestructura provee la implementación concreta (SQLiteEventStore).
    """

    @abstractmethod
    async def append(
        self,
        stream_id: str,
        event_type: str,
        payload: dict[str, Any],
        expected_version: int | None = None,
    ) -> None:
        """Agrega un evento al stream indicado.

        Args:
            stream_id: Identificador del stream (ej: "performance-<uuid>").
            event_type: Nombre del tipo de evento (ej: "APRegistrado").
            payload: Datos del evento serializables a JSON.
            expected_version: Versión esperada para control de concurrencia optimista.
                Si se provee y no coincide con la versión actual, lanza ConcurrencyError.
        """

    @abstractmethod
    async def load(self, stream_id: str) -> list[dict[str, Any]]:
        """Carga todos los eventos de un stream en orden cronológico.

        Args:
            stream_id: Identificador del stream.

        Returns:
            Lista de eventos con claves: event_type, payload, version, occurred_at.
        """

    @abstractmethod
    async def load_from(
        self, stream_id: str, from_version: int
    ) -> list[dict[str, Any]]:
        """Carga eventos de un stream a partir de una versión dada.

        Args:
            stream_id: Identificador del stream.
            from_version: Versión a partir de la cual cargar (inclusive).

        Returns:
            Lista de eventos desde from_version en adelante.
        """

    @abstractmethod
    async def load_all_streams_with_prefix(
        self, prefix: str
    ) -> list[list[dict[str, Any]]]:
        """Carga todos los streams cuyo stream_id comienza con prefix.

        Usado por los query handlers para proyectar read models de una
        competencia completa sin conocer los stream_ids individuales.

        Args:
            prefix: Prefijo del stream_id (ej: "performance-{competencia_id}-").

        Returns:
            Lista de streams; cada stream es una lista de eventos ordenados
            por version ASC. Streams vacíos no se incluyen.
        """

    @abstractmethod
    async def load_all_events_ordered(self, prefix: str) -> list[dict[str, Any]]:
        """Carga todos los eventos de streams con el prefijo dado, en orden de inserción global.

        A diferencia de load_all_streams_with_prefix, retorna una lista plana
        ordenada por el id autoincrement de la tabla (orden real de inserción),
        incluyendo el stream_id de cada evento para identificar la performance.

        Args:
            prefix: Prefijo del stream_id (ej: "performance-{competencia_id}-").

        Returns:
            Lista plana de eventos con claves: sequence, stream_id, event_type,
            payload, occurred_at. Ordenados por sequence (id) ASC.
        """
