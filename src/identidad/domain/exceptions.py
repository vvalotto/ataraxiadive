from __future__ import annotations


class EmailYaRegistrado(Exception):
    def __init__(self, email: str) -> None:
        super().__init__(f"El email '{email}' ya está registrado")


class CredencialesInvalidas(Exception):
    def __init__(self) -> None:
        super().__init__("Email o contraseña incorrectos")


class UsuarioNoEncontrado(Exception):
    def __init__(self, usuario_id: str) -> None:
        super().__init__(f"Usuario '{usuario_id}' no encontrado")


class UsuarioInactivo(Exception):
    def __init__(self, email: str) -> None:
        super().__init__(f"El usuario '{email}' está inactivo")


class PasswordDemasiadoCorto(Exception):
    def __init__(self) -> None:
        super().__init__("La contraseña debe tener al menos 8 caracteres")


class TokenInvalido(Exception):
    def __init__(self) -> None:
        super().__init__("Token JWT inválido o expirado")
