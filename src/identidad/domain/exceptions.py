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


class CampoRequerido(Exception):
    def __init__(self, campo: str) -> None:
        super().__init__(f"El {campo} es requerido")


class RolNoPermitido(Exception):
    def __init__(self) -> None:
        super().__init__("El rol ADMIN no está permitido en el auto-registro")


class PasswordActualIncorrecto(Exception):
    def __init__(self) -> None:
        super().__init__("La contraseña actual es incorrecta")


class TokenInvalido(Exception):
    def __init__(self) -> None:
        super().__init__("Token JWT inválido o expirado")
