"""Domain Events del BC Competencia."""

from competencia.domain.events.ap_registrado import APRegistrado
from competencia.domain.events.atleta_llamado import AtletaLlamado
from competencia.domain.events.dns_registrado import DNSRegistrado
from competencia.domain.events.grilla_de_salida_generada import GrillaDeSalidaGenerada
from competencia.domain.events.intervalo_ot_configurado import IntervaloOTConfigurado
from competencia.domain.events.resultado_corregido import ResultadoCorregido
from competencia.domain.events.resultado_registrado import ResultadoRegistrado
from competencia.domain.events.tarjeta_asignada import TarjetaAsignada

__all__ = [
    "APRegistrado",
    "AtletaLlamado",
    "DNSRegistrado",
    "GrillaDeSalidaGenerada",
    "IntervaloOTConfigurado",
    "ResultadoCorregido",
    "ResultadoRegistrado",
    "TarjetaAsignada",
]
