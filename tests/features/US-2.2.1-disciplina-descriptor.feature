# US-2.2.1: DisciplinaDescriptor — VO que encapsula reglas de disciplina
# BC: competencia | Incremento: Inc 2.2 — Dos Mecánicas, un Modelo
# Política: P-01 (orden de grilla)

@US-2.2.1
Feature: DisciplinaDescriptor — VO que encapsula reglas de disciplina

  @US-2.2.1 @happy_path
  Scenario: Descriptor STA retorna unidad Segundos y orden descendente
    Given la disciplina es "STA"
    When se consulta el DisciplinaDescriptorPort
    Then unidad_esperada es "Segundos"
    And orden_ascendente es False

  @US-2.2.1 @happy_path
  Scenario: Descriptor DNF retorna unidad Metros y orden ascendente
    Given la disciplina es "DNF"
    When se consulta el DisciplinaDescriptorPort
    Then unidad_esperada es "Metros"
    And orden_ascendente es True

  @US-2.2.1 @happy_path
  Scenario Outline: Todas las disciplinas de distancia retornan Metros y orden ascendente
    Given la disciplina es "<disciplina>"
    When se consulta el DisciplinaDescriptorPort
    Then unidad_esperada es "Metros"
    And orden_ascendente es True

    Examples:
      | disciplina |
      | DNF        |
      | DYN        |
      | DYNB       |
      | CNF        |
      | CWT        |
      | FIM        |

  @US-2.2.1 @happy_path
  Scenario: GenerarGrilla usa descriptor para ordenar STA — mayor AP primero
    Given una competencia STA con 3 atletas con APs 120s, 300s y 180s
    And el intervalo OT está configurado en 9 minutos
    When se genera la grilla usando el DisciplinaDescriptorPort
    Then el orden de la grilla es posición 1 con AP 300s, posición 2 con AP 180s, posición 3 con AP 120s

  @US-2.2.1 @happy_path
  Scenario: GenerarGrilla usa descriptor para ordenar DNF — menor AP primero
    Given una competencia DNF con 3 atletas con APs 80m, 40m y 60m
    And el intervalo OT está configurado en 9 minutos
    When se genera la grilla usando el DisciplinaDescriptorPort
    Then el orden de la grilla es posición 1 con AP 40m, posición 2 con AP 60m, posición 3 con AP 80m
