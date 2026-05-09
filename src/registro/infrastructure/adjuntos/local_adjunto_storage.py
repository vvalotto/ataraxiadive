from __future__ import annotations

from pathlib import Path
from uuid import UUID

from registro.domain.ports.adjunto_storage_port import AdjuntoStoragePort


class LocalAdjuntoStorage(AdjuntoStoragePort):
    def __init__(self, base_dir: Path | str = "data/adjuntos") -> None:
        self._base_dir = Path(base_dir)

    def guardar(
        self,
        *,
        inscripcion_id: UUID,
        nombre_archivo: str,
        filename_original: str | None,
        contenido: bytes,
    ) -> str:
        extension = Path(filename_original or "").suffix or ".bin"
        directorio = self._base_dir / str(inscripcion_id)
        directorio.mkdir(parents=True, exist_ok=True)
        ruta = directorio / f"{nombre_archivo}{extension}"
        ruta.write_bytes(contenido)
        return str(ruta)
