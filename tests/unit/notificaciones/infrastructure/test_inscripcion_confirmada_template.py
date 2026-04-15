from __future__ import annotations

from notificaciones.application.policies.politica_p10 import InscripcionConfirmada
from notificaciones.infrastructure.templates.inscripcion_confirmada_template import (
    InscripcionConfirmadaTemplate,
)


def test_template_renderiza_datos_de_inscripcion_confirmada() -> None:
    evento = InscripcionConfirmada(
        id="evt-reg-001",
        atleta_id="ath-123",
        atleta_email="garcia@apnea.com",
        atleta_nombre="Martin Garcia",
        torneo_nombre="Open BA 2026",
        torneo_fecha="2026-05-15",
        torneo_sede="Club Nautico",
        disciplinas=("DNF", "STA"),
    )

    contenido = InscripcionConfirmadaTemplate().render(evento)

    assert contenido.asunto == "Inscripcion confirmada - Open BA 2026"
    assert "Martin Garcia" in contenido.cuerpo_texto
    assert "Open BA 2026" in contenido.cuerpo_texto
    assert "2026-05-15" in contenido.cuerpo_texto
    assert "Club Nautico" in contenido.cuerpo_texto
    assert "DNF, STA" in contenido.cuerpo_texto
