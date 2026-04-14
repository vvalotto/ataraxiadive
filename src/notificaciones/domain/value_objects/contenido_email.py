from __future__ import annotations

from dataclasses import dataclass

from notificaciones.domain.exceptions import ContenidoEmailInvalido


@dataclass(frozen=True)
class ContenidoEmail:
    asunto: str
    cuerpo_texto: str
    cuerpo_html: str | None = None

    def __post_init__(self) -> None:
        if not self.asunto or not self.asunto.strip():
            raise ContenidoEmailInvalido("ContenidoEmail.asunto no puede ser vacío")
        if not self.cuerpo_texto or not self.cuerpo_texto.strip():
            raise ContenidoEmailInvalido("ContenidoEmail.cuerpo_texto no puede ser vacío")
