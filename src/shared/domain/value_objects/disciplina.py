"""Value Object Disciplina — modalidades de apnea competitiva."""

from __future__ import annotations

from enum import StrEnum


class Disciplina(StrEnum):
    """Disciplinas de apnea reconocidas por AIDA/CMAS.

    Valores de tiempo (segundos): STA
    Valores de distancia (metros): DNF, DYN, DBF, SPE, CNF, CWT, FIM, VWT
    """

    STA = "STA"  # Static Apnea — tiempo
    DNF = "DNF"  # Dynamic No Fins — distancia
    DYN = "DYN"  # Dynamic With Fins — distancia
    DBF = "DBF"  # Dynamic Bi-Fins — distancia (acrónimo oficial AIDA)
    SPE = "SPE"  # Speed Endurance — distancia (acrónimo oficial AIDA)
    CNF = "CNF"  # Constant No Fins — distancia
    CWT = "CWT"  # Constant Weight — distancia
    FIM = "FIM"  # Free Immersion — distancia
    VWT = "VWT"  # Variable Weight — distancia

    def es_tiempo(self) -> bool:
        """Retorna True si la disciplina se mide en segundos."""
        return self == Disciplina.STA

    def es_distancia(self) -> bool:
        """Retorna True si la disciplina se mide en metros."""
        return not self.es_tiempo()
