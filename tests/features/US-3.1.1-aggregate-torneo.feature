Feature: US-3.1.1 — Aggregate Torneo — máquina de estados

  Scenario: crear torneo con datos válidos
    When se instancia un Torneo con los datos válidos
    Then el estado es CREADO
    And el torneo_id es un UUID válido

  Scenario: nombre vacío lanza excepción
    Given un nombre inválido vacío
    When se instancia un Torneo con nombre inválido
    Then se lanza ValueError con mensaje sobre nombre vacío

  Scenario: nombre solo espacios lanza excepción
    Given un nombre inválido de solo espacios
    When se instancia un Torneo con nombre inválido
    Then se lanza ValueError con mensaje sobre nombre vacío

  Scenario: fecha_fin anterior a fecha_inicio lanza excepción
    Given fecha_inicio 2026-06-03 y fecha_fin 2026-06-01
    When se instancia un Torneo con esas fechas
    Then se lanza ValueError con mensaje sobre fechas inválidas

  Scenario: ciclo completo de transiciones
    Given un Torneo en estado CREADO
    When se ejecutan en secuencia abrir_inscripcion, cerrar_inscripcion, iniciar_ejecucion, iniciar_premiacion, cerrar
    Then el estado final es CERRADO

  Scenario: retroceso EJECUCION a PREPARACION
    Given un Torneo en estado EJECUCION
    When se llama volver_a_preparacion
    Then el estado es PREPARACION

  Scenario: cancelar desde estado INSCRIPCION_ABIERTA
    Given un Torneo en estado INSCRIPCION_ABIERTA
    When se llama cancelar
    Then el estado es CANCELADO

  Scenario: cancelar desde estado PREPARACION
    Given un Torneo en estado PREPARACION
    When se llama cancelar
    Then el estado es CANCELADO

  Scenario: cancelar desde estado EJECUCION
    Given un Torneo en estado EJECUCION
    When se llama cancelar
    Then el estado es CANCELADO

  Scenario: no se puede cancelar un torneo CERRADO
    Given un Torneo en estado CERRADO
    When se llama cancelar
    Then se lanza TorneoCerrado

  Scenario: transición inválida desde CREADO a EJECUCION lanza excepción
    Given un Torneo en estado CREADO
    When se llama iniciar_ejecucion directamente
    Then se lanza TransicionEstadoInvalida

  Scenario: transición inválida desde CANCELADO lanza excepción
    Given un Torneo en estado CANCELADO
    When se llama abrir_inscripcion
    Then se lanza TransicionEstadoInvalida

  Scenario: no se puede avanzar desde CERRADO
    Given un Torneo en estado CERRADO
    When se llama abrir_inscripcion
    Then se lanza TorneoCerrado
