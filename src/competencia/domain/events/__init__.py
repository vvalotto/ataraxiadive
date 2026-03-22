"""Domain Events del BC Competencia."""
from competencia.domain.events.ap_registrado import APRegistrado
from competencia.domain.events.atleta_llamado import AtletaLlamado
from competencia.domain.events.resultado_registrado import ResultadoRegistrado
from competencia.domain.events.tarjeta_asignada import TarjetaAsignada

__all__ = ["APRegistrado", "AtletaLlamado", "ResultadoRegistrado", "TarjetaAsignada"]
