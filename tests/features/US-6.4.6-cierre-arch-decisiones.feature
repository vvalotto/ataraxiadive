Feature: US-6.4.6 — Decisiones arquitecturales cerradas y registradas

  Scenario: ARCH-03 cerrado como ACL aceptable sin import cross-BC
    Given el archivo resultados_competencia_adapter.py
    When se buscan imports de "competencia."
    Then no hay coincidencias de imports cross-BC

  Scenario: DR-01 investigado como falso positivo de Event Sourcing
    Given el aggregate RankingCompetencia con LCOM reportado 2/1
    When se analiza la separacion de responsabilidades
    Then los dos grupos de metodos son inherentes al patron ES
    And los helpers de modulo estan extraidos correctamente fuera de la clase

  Scenario: AA-02 registrado en BL-006 sin intervencion en v1.0
    Given identidad D igual a 0.67 tras BL-005
    When se cierra INC-6.4
    Then BL-006 registra la tendencia de identidad con decision de no intervencion

  Scenario: AA-04 registrado en BL-006 sin intervencion en v1.0
    Given shared D igual a 0.63 estable entre BL-004 y BL-005
    When se cierra INC-6.4
    Then BL-006 registra shared con decision de diferir a post-despliegue

  Scenario: DesignReviewer 0 CRITICAL al cierre de INC-6.4
    Given todos los hallazgos de INC-6.4 procesados
    When se ejecuta designreviewer sobre src
    Then el reporte indica should_block igual a false
