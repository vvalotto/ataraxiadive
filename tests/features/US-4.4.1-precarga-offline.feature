Feature: US-4.4.1 - Precarga de disciplina en cache local

  Background:
    Given el juez "juez@ataraxia.com" esta autenticado
    And existe la competencia C1 para disciplina DNF

  Scenario: abrir grilla online actualiza cache local
    Given el dispositivo esta online
    When el juez abre la grilla de DNF
    Then la grilla se obtiene del servidor
    And la cache local guarda grilla y estado para (C1, DNF)

  Scenario: abrir grilla offline con cache existente
    Given existe cache local para (C1, DNF) de hace 2 horas
    And el dispositivo esta offline
    When el juez abre la grilla de DNF
    Then la grilla se muestra desde cache local
    And se muestra aviso de modo offline

  Scenario: abrir grilla offline sin cache previo
    Given no existe cache local para (C1, DNF)
    And el dispositivo esta offline
    When el juez abre la grilla de DNF
    Then se muestra el mensaje "Sin datos disponibles"
    And se sugiere reconectar para la primera carga

  Scenario: abrir grilla offline con cache expirado
    Given existe cache local para (C1, DNF) con mas de 24 horas
    And el dispositivo esta offline
    When el juez abre la grilla de DNF
    Then la grilla se muestra desde cache local
    And se muestra aviso de posible desactualizacion

