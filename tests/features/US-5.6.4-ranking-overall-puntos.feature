Feature: US-5.6.4 — RankingOverall con puntos acumulados

  Background:
    Given un torneo con dos disciplinas DNF y STA

  Scenario: overall suma puntos de todas las disciplinas
    Given Ana con 100.00 puntos en DNF y 75.00 en STA en SENIOR_FEMENINO
    When se calcula el overall
    Then Ana tiene puntos_overall igual a 175.00

  Scenario: atleta sin participar en una disciplina aporta 0
    Given Luis con 80.00 puntos en DNF y DNS en STA en SENIOR_MASCULINO
    When se calcula el overall
    Then Luis tiene puntos_overall igual a 80.00

  Scenario: empate en overall comparte posicion
    Given Ana con 100.00 puntos en DNF y 75.00 en STA en SENIOR_FEMENINO
    And Maria con 75.00 puntos en DNF y 100.00 en STA en SENIOR_FEMENINO
    When se calcula el overall
    Then Ana y Maria aparecen con posicion 1

  Scenario: overall rechazado si hay disciplinas sin finalizar
    Given solo DNF tiene ranking calculado para el torneo
    When se intenta calcular el overall con DNF y STA
    Then el sistema rechaza la operacion con DisciplinasNoFinalizadas

  Scenario: overall agrupa por categorias
    Given un atleta en SENIOR_MASCULINO con 140.00 puntos totales
    And una atleta en SENIOR_FEMENINO con 175.00 puntos totales
    When se calcula el overall
    Then las entradas estan separadas por categoria
    And el primero de cada categoria tiene la mayor puntuacion
