"""Tests unitarios — require_rol() y dependencias de auth [US-3.4.2]"""

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from identidad.api.dependencies import (
    AtletaDep,
    JuezDep,
    OrganizadorDep,
    get_current_user,
    require_rol,
)
from identidad.domain.value_objects.rol import Rol

# ── require_rol() factory ─────────────────────────────────────────────────────


def _app_con_ruta(dep: object, status: int = 200) -> FastAPI:
    """Crea una app minimal con un endpoint protegido por la dependencia dada."""
    app = FastAPI()

    @app.get("/protegido")
    async def _endpoint(_: dep) -> dict:  # type: ignore[valid-type]
        return {"ok": True}

    return app


def _mock_user(rol: str) -> dict:  # type: ignore[type-arg]
    return {"sub": "uid-1", "email": "test@test.com", "rol": rol}


class TestRequireRol:
    def test_rol_correcto_permite_acceso(self) -> None:
        app = _app_con_ruta(OrganizadorDep)
        app.dependency_overrides[get_current_user] = lambda: _mock_user("ORGANIZADOR")
        client = TestClient(app)
        resp = client.get("/protegido")
        assert resp.status_code == 200

    def test_rol_incorrecto_retorna_403(self) -> None:
        app = _app_con_ruta(OrganizadorDep)
        app.dependency_overrides[get_current_user] = lambda: _mock_user("ATLETA")
        client = TestClient(app)
        resp = client.get("/protegido")
        assert resp.status_code == 403

    def test_admin_pasa_cualquier_dep(self) -> None:
        for dep in [OrganizadorDep, JuezDep, AtletaDep]:
            app = _app_con_ruta(dep)
            app.dependency_overrides[get_current_user] = lambda: _mock_user("ADMIN")
            resp = TestClient(app).get("/protegido")
            assert resp.status_code == 200

    def test_juez_pasa_juezdep_y_organizadordep(self) -> None:
        for dep in [JuezDep, OrganizadorDep]:
            app = _app_con_ruta(dep)
            app.dependency_overrides[get_current_user] = lambda: _mock_user("JUEZ")
            # JuezDep permite JUEZ; OrganizadorDep NO permite JUEZ
            resp = TestClient(app).get("/protegido")
            if dep is JuezDep:
                assert resp.status_code == 200
            else:
                assert resp.status_code == 403

    def test_atleta_solo_pasa_atletadep(self) -> None:
        for dep, expected in [(AtletaDep, 200), (OrganizadorDep, 403), (JuezDep, 403)]:
            app = _app_con_ruta(dep)
            app.dependency_overrides[get_current_user] = lambda: _mock_user("ATLETA")
            resp = TestClient(app).get("/protegido")
            assert resp.status_code == expected

    def test_sin_token_retorna_401(self) -> None:
        """Sin override de get_current_user, el OAuth2 scheme exige token."""
        app = _app_con_ruta(OrganizadorDep)
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/protegido")
        assert resp.status_code == 401


class TestOrganizadorDep:
    def test_organizador_puede_crear_torneo(self) -> None:
        """Verifica integración real: OrganizadorDep en el router de Torneo."""
        import os, tempfile
        from fastapi import FastAPI
        from torneo.api.router import router

        db = tempfile.mktemp(suffix=".db")
        os.environ["TORNEO_DB_PATH"] = db
        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_current_user] = lambda: _mock_user("ORGANIZADOR")
        client = TestClient(app)
        resp = client.post(
            "/torneos",
            json={
                "nombre": "Test",
                "descripcion": "D",
                "fecha_inicio": "2026-06-01",
                "fecha_fin": "2026-06-03",
                "sede": {"nombre": "P", "ciudad": "C", "pais": "AR"},
                "entidad_organizadora": {"nombre": "E", "tipo": "club"},
            },
        )
        assert resp.status_code == 201

    def test_atleta_no_puede_crear_torneo(self) -> None:
        import os, tempfile
        from fastapi import FastAPI
        from torneo.api.router import router

        db = tempfile.mktemp(suffix=".db")
        os.environ["TORNEO_DB_PATH"] = db
        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_current_user] = lambda: _mock_user("ATLETA")
        client = TestClient(app)
        resp = client.post(
            "/torneos",
            json={
                "nombre": "Test",
                "descripcion": "D",
                "fecha_inicio": "2026-06-01",
                "fecha_fin": "2026-06-03",
                "sede": {"nombre": "P", "ciudad": "C", "pais": "AR"},
                "entidad_organizadora": {"nombre": "E", "tipo": "club"},
            },
        )
        assert resp.status_code == 403

    def test_get_torneos_es_publico(self) -> None:
        import os, tempfile
        from fastapi import FastAPI
        from torneo.api.router import router

        db = tempfile.mktemp(suffix=".db")
        os.environ["TORNEO_DB_PATH"] = db
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        resp = client.get("/torneos")
        assert resp.status_code == 200
