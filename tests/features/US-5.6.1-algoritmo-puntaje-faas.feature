Feature: US-5.6.1 — Algoritmo de puntaje FAAS

  Background:
    Given atletas identificados por UUIDs conocidos

  Scenario: distancia — puntuacion proporcional al maximo
    Given una disciplina de tipo distancia DNF
    And los resultados son: Ana 70 metros Blanca, Luis 56 metros Blanca
    When se calcula el puntaje FAAS
    Then Ana recibe 100.00 puntos
    And Luis recibe 80.00 puntos

  Scenario: tiempo — el mas rapido recibe 100 puntos
    Given una disciplina de tipo tiempo SPE_2X50
    And los resultados son: Luis 190 segundos Blanca, Ana 270 segundos Blanca
    When se calcula el puntaje FAAS
    Then Luis recibe 100.00 puntos
    And Ana recibe 0.00 puntos

  Scenario: DNS recibe 0 y no altera el denominador de distancia
    Given una disciplina de tipo distancia DNF
    And los resultados son: Ana 70 metros Blanca, Pedro DNS
    When se calcula el puntaje FAAS
    Then Ana recibe 100.00 puntos
    And Pedro recibe 0.00 puntos

  Scenario: tarjeta roja recibe 0 y no altera el denominador
    Given una disciplina de tipo distancia DNF
    And los resultados son: Ana 70 metros Blanca, Luis 60 metros Roja
    When se calcula el puntaje FAAS
    Then Ana recibe 100.00 puntos
    And Luis recibe 0.00 puntos

  Scenario: caso borde tiempo — todos iguales reciben 100
    Given una disciplina de tipo tiempo STA
    And los resultados son: Ana 180 segundos Blanca, Luis 180 segundos Blanca
    When se calcula el puntaje FAAS
    Then Ana recibe 100.00 puntos
    And Luis recibe 100.00 puntos

  Scenario: todos invalidos — todos reciben 0
    Given una disciplina de tipo distancia DNF
    And los resultados son: Ana DNS, Luis Roja
    When se calcula el puntaje FAAS
    Then Ana recibe 0.00 puntos
    And Luis recibe 0.00 puntos

  Scenario: resultado vacio retorna dict vacio
    Given una disciplina de tipo distancia DNF
    And no hay resultados
    When se calcula el puntaje FAAS
    Then el resultado es un diccionario vacio

  Scenario: distancia con multiples atletas — proporcional correcto
    Given una disciplina de tipo distancia DNF
    And los resultados son: Ana 100 metros Blanca, Luis 75 metros Blanca, Pedro 50 metros Blanca
    When se calcula el puntaje FAAS
    Then Ana recibe 100.00 puntos
    And Luis recibe 75.00 puntos
    And Pedro recibe 50.00 puntos
