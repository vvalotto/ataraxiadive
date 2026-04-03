"""Dependencias FastAPI transversales reutilizadas entre BCs."""

from identidad.api.dependencies import AtletaDep, JuezDep, OrganizadorDep

__all__ = ["AtletaDep", "JuezDep", "OrganizadorDep"]
