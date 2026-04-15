from __future__ import annotations

from notificaciones.application.policies.politica_p11 import (
    PodioPublicado,
    ResultadoPublicadoAtleta,
    ResultadosPublicados,
)
from notificaciones.infrastructure.templates.resultados_publicados_template import (
    ResultadosPublicadosTemplate,
)


def test_template_renderiza_resultado_y_podio() -> None:
    evento = ResultadosPublicados(
        id="evt-res-001",
        torneo_id="torneo-001",
        torneo_nombre="Open BA 2026",
        disciplina="DNF",
        resultados=(),
        podio=(
            PodioPublicado(posicion=1, atleta_nombre="Martin Garcia", rp="96m"),
            PodioPublicado(posicion=2, atleta_nombre="Ana Lopez", rp="88m"),
            PodioPublicado(posicion=3, atleta_nombre="Diego Vega", rp="DNS"),
        ),
    )
    resultado = ResultadoPublicadoAtleta(
        atleta_id="ath-1",
        atleta_email="martin@example.com",
        atleta_nombre="Martin Garcia",
        posicion=1,
        rp="96m",
        tarjeta="Blanca",
    )

    contenido = ResultadosPublicadosTemplate().render(evento=evento, resultado=resultado)

    assert contenido.asunto == "Resultados publicados - DNF - Open BA 2026"
    assert "Posicion: #1" in contenido.cuerpo_texto
    assert "RP: 96m" in contenido.cuerpo_texto
    assert "Tarjeta: Blanca" in contenido.cuerpo_texto
    assert "#1 Martin Garcia - 96m" in contenido.cuerpo_texto
    assert "#2 Ana Lopez - 88m" in contenido.cuerpo_texto
    assert "#3 Diego Vega - DNS" in contenido.cuerpo_texto
    assert "https://ataraxiadive.app/resultados/torneo-001" in contenido.cuerpo_texto


def test_template_conserva_dns() -> None:
    evento = ResultadosPublicados(
        id="evt-res-001",
        torneo_id=None,
        torneo_nombre="Open BA 2026",
        disciplina="DNF",
        resultados=(),
        podio=(PodioPublicado(posicion=1, atleta_nombre="Diego Vega", rp="DNS"),),
    )
    resultado = ResultadoPublicadoAtleta(
        atleta_id="ath-3",
        atleta_email="diego@example.com",
        atleta_nombre="Diego Vega",
        posicion=1,
        rp="DNS",
        tarjeta=None,
        estado="DNS",
    )

    contenido = ResultadosPublicadosTemplate().render(evento=evento, resultado=resultado)

    assert "RP: DNS" in contenido.cuerpo_texto
    assert "#1 Diego Vega - DNS" in contenido.cuerpo_texto
    assert "https://ataraxiadive.app/resultados" in contenido.cuerpo_texto
