"""Value Object Disciplina — modalidades de apnea competitiva."""

from __future__ import annotations

from enum import StrEnum


class Disciplina(StrEnum):
    """Disciplinas de apnea reconocidas por AIDA/CMAS.

    Valores de tiempo (segundos): STA
    Valores de tiempo (segundos): STA, SPE_2X50, SPE_4X50, SPE_8X50, SPE_16X50
    Valores de distancia (metros): DNF, DYN, DBF, SPE, CNF, CWT, FIM, VWT
    """

    STA = "STA"  # Static Apnea — tiempo
    DNF = "DNF"  # Dynamic No Fins — distancia
    DYN = "DYN"  # Dynamic With Fins — distancia
    DBF = "DBF"  # Dynamic Bi-Fins — distancia (acrónimo oficial AIDA)
    SPE = "SPE"  # Speed Endurance legacy — se mantiene para compatibilidad histórica
    SPE_2X50 = "SPE_2X50"  # Speed Endurance 2 x 50m — tiempo
    SPE_4X50 = "SPE_4X50"  # Speed Endurance 4 x 50m — tiempo
    SPE_8X50 = "SPE_8X50"  # Speed Endurance 8 x 50m — tiempo
    SPE_16X50 = "SPE_16X50"  # Speed Endurance 16 x 50m — tiempo
    CNF = "CNF"  # Constant No Fins — distancia
    CWT = "CWT"  # Constant Weight — distancia
    FIM = "FIM"  # Free Immersion — distancia
    VWT = "VWT"  # Variable Weight — distancia

    def es_spe(self) -> bool:
        """Retorna True si la disciplina pertenece a la familia SPE."""
        return self in {
            Disciplina.SPE,
            Disciplina.SPE_2X50,
            Disciplina.SPE_4X50,
            Disciplina.SPE_8X50,
            Disciplina.SPE_16X50,
        }

    def es_tiempo(self) -> bool:
        """Retorna True si la disciplina se mide en segundos."""
        return self in {
            Disciplina.STA,
            Disciplina.SPE_2X50,
            Disciplina.SPE_4X50,
            Disciplina.SPE_8X50,
            Disciplina.SPE_16X50,
        }

    def es_distancia(self) -> bool:
        """Retorna True si la disciplina se mide en metros."""
        return not self.es_tiempo()

    def tiempo_mayor_es_mejor(self) -> bool:
        """Retorna True si en esta disciplina mayor tiempo = mejor resultado (STA)."""
        return self == Disciplina.STA
