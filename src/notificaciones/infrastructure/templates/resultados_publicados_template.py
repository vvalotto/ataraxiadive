from __future__ import annotations

from typing import Protocol

from notificaciones.domain.value_objects.contenido_email import ContenidoEmail


class ResultadoPublicadoLike(Protocol):
    atleta_nombre: str
    posicion: int | None
    rp: str
    tarjeta: str | None


class PodioPublicadoLike(Protocol):
    posicion: int
    atleta_nombre: str
    rp: str


class ResultadosPublicadosLike(Protocol):
    torneo_id: str | None
    torneo_nombre: str
    disciplina: str
    podio: tuple[PodioPublicadoLike, ...]


class ResultadosPublicadosTemplate:
    def render(
        self,
        *,
        evento: ResultadosPublicadosLike,
        resultado: ResultadoPublicadoLike,
    ) -> ContenidoEmail:
        asunto = f"Resultados publicados - {evento.disciplina} - {evento.torneo_nombre}"
        posicion = f"#{resultado.posicion}" if resultado.posicion is not None else "-"
        tarjeta = resultado.tarjeta or "-"
        podio = self._render_podio(evento.podio)
        ranking_url = self._ranking_url(evento.torneo_id)

        cuerpo = "\n".join(
            [
                f"Hola {resultado.atleta_nombre},",
                "",
                f"Ya estan disponibles los resultados de la disciplina {evento.disciplina}",
                f"en el torneo {evento.torneo_nombre}.",
                "",
                "Tu resultado:",
                f"  Posicion: {posicion}",
                f"  RP: {resultado.rp}",
                f"  Tarjeta: {tarjeta}",
                "",
                f"Podio {evento.disciplina}:",
                podio,
                "",
                f"Ranking completo: {ranking_url}",
                "",
                "Felicitaciones por tu participacion!",
                "El equipo de AtaraxiaDive",
            ]
        )
        return ContenidoEmail(asunto=asunto, cuerpo_texto=cuerpo)

    def _render_podio(self, podio: tuple[PodioPublicadoLike, ...]) -> str:
        return "\n".join(
            f"  #{item.posicion} {item.atleta_nombre} - {item.rp}"
            for item in podio[:3]
        )

    def _ranking_url(self, torneo_id: str | None) -> str:
        if not torneo_id:
            return "https://ataraxiadive.app/resultados"
        return f"https://ataraxiadive.app/resultados/{torneo_id}"
