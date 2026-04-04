Feature: API Disciplina-Aware — validación de unidades y avance por grilla

  Background:
    Given una competencia en estado EnEjecucion con 3 atletas en grilla STA
    And el orden de grilla es posicion 1 con AP 120s, posicion 2 con AP 180s, posicion 3 con AP 300s

  Scenario: Registrar resultado STA con unidad correcta Segundos
    Given el atleta en posicion 1 fue llamado
    When el juez registra resultado de 295 Segundos para STA
    Then el evento ResultadoRegistrado persiste con unidad Segundos

  Scenario: Rechazo al registrar resultado STA con unidad incorrecta Metros
    Given el atleta en posicion 1 fue llamado
    When el juez intenta registrar resultado de 295 Metros para STA
    Then el sistema rechaza con error UnidadIncompatible
    And ningun evento es persistido

  Scenario: Registrar resultado DNF con unidad correcta Metros
    Given una competencia en estado EnEjecucion con disciplina DNF
    And el atleta en posicion 1 fue llamado para DNF
    When el juez registra resultado de 85.50 Metros para DNF
    Then el evento ResultadoRegistrado persiste con valor 85.50 y unidad Metros

  Scenario: Rechazo al registrar AP con unidad incorrecta en STA
    Given una competencia STA en estado Preparacion con un atleta
    When el atleta intenta declarar AP de 300 Metros para STA
    Then el sistema rechaza con error UnidadIncompatible

  Scenario: ProximosAtletas respeta el orden de grilla
    Given el atleta en posicion 1 fue llamado y completo su performance
    When el juez consulta las proximas performances
    Then el primer resultado es el atleta en posicion 2 con AP 180s
    And el segundo resultado es el atleta en posicion 3 con AP 300s

  Scenario: PerformanceActual incluye unidad_esperada para STA
    Given el atleta en posicion 1 esta en estado Llamada para STA
    When el juez consulta la performance actual
    Then la respuesta incluye unidad_esperada Segundos

  Scenario: PerformanceActual incluye unidad_esperada para DNF
    Given una competencia DNF con atleta en estado Llamada
    When el juez consulta la performance actual para DNF
    Then la respuesta incluye unidad_esperada Metros
