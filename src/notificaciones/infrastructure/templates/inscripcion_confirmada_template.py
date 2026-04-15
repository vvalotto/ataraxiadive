from __future__ import annotations

from typing import Protocol

from notificaciones.domain.value_objects.contenido_email import ContenidoEmail


class InscripcionConfirmadaLike(Protocol):
    atleta_nombre: str
    torneo_nombre: str
    torneo_fecha: object
    torneo_sede: str
    disciplinas: tuple[str, ...]


class InscripcionConfirmadaTemplate:
    def render(self, evento: InscripcionConfirmadaLike) -> ContenidoEmail:
        disciplinas = ", ".join(evento.disciplinas)
        asunto = f"Inscripcion confirmada - {evento.torneo_nombre}"
        cuerpo = "\n".join(
            [
                f"Hola {evento.atleta_nombre},",
                "",
                f"Tu inscripcion al torneo {evento.torneo_nombre} ha sido confirmada.",
                "",
                f"Fecha: {evento.torneo_fecha}",
                f"Sede: {evento.torneo_sede}",
                f"Disciplinas inscriptas: {disciplinas}",
                "",
                "Buena suerte!",
                "El equipo de AtaraxiaDive",
            ]
        )
        return ContenidoEmail(asunto=asunto, cuerpo_texto=cuerpo)
