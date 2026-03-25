# US-2.1.1: Scaffold Aggregate Competencia + ConfigurarIntervaloOT
# BC: competencia | Incremento: Inc 2.1 — La Grilla de Salida
# Invariantes: INV-C-01

@US-2.1.1
Feature: Configurar Intervalo OT de Competencia

  Background:
    Given una competencia con id "C001" en estado "Preparacion"
    And la disciplina es "STA"

  @US-2.1.1 @happy_path
  Scenario: Configurar intervalo exitosamente
    Given no existe un intervalo previo configurado
    When el organizador configura el intervalo en 9 minutos
    Then el intervalo queda registrado en 9 minutos
    And el evento IntervaloOTConfigurado persiste en el stream
    And la competencia sigue en estado "Preparacion"

  @US-2.1.1 @happy_path
  Scenario: Reconfigurar intervalo (repetición permitida)
    Given ya existe un IntervaloOTConfigurado de 7 minutos
    When el organizador reconfigura el intervalo a 10 minutos
    Then el nuevo IntervaloOTConfigurado persiste con valor 10
    And el intervalo activo de la competencia es 10 minutos

  @US-2.1.1 @error_case
  Scenario: Rechazo — intervalo cero o negativo
    When el organizador intenta configurar el intervalo en 0 minutos
    Then el sistema rechaza la operación con error "IntervaloInvalido"

  @US-2.1.1 @error_case
  Scenario: Rechazo — grilla ya confirmada
    Given la grilla ya fue confirmada para esta competencia
    When el organizador intenta reconfigurar el intervalo
    Then el sistema rechaza la operación con error "GrillaYaConfirmada"
