Feature: Ranking Overall por torneo
  # US-3.5.1 | RF-PM-01 | RF-PM-02
  # Como organizador, quiero calcular el ranking general de un torneo
  # a partir de los rankings por disciplina sumando puntos FAAS.

  Scenario: overall con 3 atletas en 2 disciplinas
    Given rankings del torneo con STA: A=1, B=2, C=3
    And rankings del torneo con DNF: A=2, B=1, C=3
    When el sistema calcula el overall del torneo
    Then A tiene puntaje overall 30 y posicion 1
    And B tiene puntaje overall 30 y posicion 1
    And C tiene puntaje overall 10 y posicion 3
    And A y B tienen en_podio overall igual a True

  Scenario: atleta ausente en una disciplina ejecutada
    Given rankings del torneo con STA: A=1, B=2
    And rankings del torneo con DNF: solo B participa con posicion 1
    When el sistema calcula el overall del torneo
    Then A recibe penalizacion por ausencia en DNF
    And A tiene puntaje overall 20 y posicion 1
    And B tiene puntaje overall 20 y posicion 1

  Scenario: disciplinas sin ranking calculado no participan del overall
    Given rankings del torneo con STA: A=1, B=2
    And la disciplina DNF del torneo aun no tiene ranking calculado
    When el sistema calcula el overall solo con STA
    Then el overall se calcula solo con STA
    And A tiene puntaje overall 20 y posicion 1
    And B tiene puntaje overall 10 y posicion 2

  Scenario: torneo sin rankings calculados
    Given un torneo sin rankings calculados
    When el sistema calcula el overall del torneo
    Then el sistema rechaza con DisciplinasNoFinalizadas

  Scenario: empate total conserva la misma posicion
    Given rankings del torneo con STA: A=1, B=2
    And rankings del torneo con DNF: A=2, B=1
    When el sistema calcula el overall del torneo
    Then A y B tienen la misma posicion overall
    And no existe entrada overall con posicion 2
