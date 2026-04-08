Feature: US-4.1.4 - Orden de grilla reglamentario

  Scenario: grilla DYN ordena menor AP primero
    Given una competencia DYN con APs 80m, 60m y 75m
    When se genera la grilla reglamentaria
    Then el orden de salida es AP 60m, 75m y 80m

  Scenario: grilla STA ordena menor AP primero en segundos
    Given una competencia STA con APs 300s, 180s y 240s
    When se genera la grilla reglamentaria
    Then el orden de salida es AP 180s, 240s y 300s

  Scenario: grilla SPE_4X50 ordena mayor tiempo primero
    Given una competencia SPE_4X50 con APs 180s, 210s y 195s
    When se genera la grilla reglamentaria
    Then el orden de salida es AP 210s, 195s y 180s

  Scenario: grilla SPE_2X50 ordena mayor tiempo primero
    Given una competencia SPE_2X50 con APs 70s, 90s y 80s
    When se genera la grilla reglamentaria
    Then el orden de salida es AP 90s, 80s y 70s

  Scenario: DisciplinaDescriptor para SPE_4X50 tiene orden descendente
    Given el DisciplinaDescriptor para SPE_4X50 en US-4.1.4
    Then orden_ascendente es False en US-4.1.4
    And unidad_esperada es Segundos en US-4.1.4

  Scenario: DisciplinaDescriptor para DNF mantiene orden ascendente
    Given el DisciplinaDescriptor para DNF en US-4.1.4
    Then orden_ascendente es True en US-4.1.4
    And unidad_esperada es Metros en US-4.1.4
