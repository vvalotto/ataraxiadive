"""Arquitectura US-6.4.3: routers sin infraestructura cross-BC."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_resultados_router_no_importa_infraestructura_cross_bc() -> None:
    source = _read("src/resultados/api/router.py")

    assert "competencia.infrastructure" not in source
    assert "torneo.infrastructure" not in source


def test_competencia_router_no_importa_infraestructura_de_registro() -> None:
    source = _read("src/competencia/api/router.py")

    assert "registro.infrastructure" not in source


def test_registro_upload_no_se_propaga_a_domain_ni_application() -> None:
    forbidden = ("UploadFile", "fastapi.UploadFile", "pathlib.Path")
    files = [
        path
        for package in ("src/registro/domain", "src/registro/application")
        for path in (ROOT / package).rglob("*.py")
    ]

    for path in files:
        source = path.read_text(encoding="utf-8")
        assert not any(token in source for token in forbidden), path
