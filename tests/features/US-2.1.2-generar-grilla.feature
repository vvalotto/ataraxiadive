# US-2.1.2: Generar / Regenerar Grilla de Salida
# BC: competencia | Incremento: Inc 2.1 — La Grilla de Salida
# Invariantes: INV-C-01 | Políticas: P-01, P-02, P-05

@US-2.1.2
Feature: Generar Grilla de Salida

  Background:
    Given una competencia "C001" con disciplina "STA" en estado "Preparacion"
    And el intervalo OT está configurado en 9 minutos
    And OT de inicio es "10:00:00"

  @US-2.1.2 @happy_path
  Scenario: Grilla generada con orden correcto para STA (tiempo mayor→menor)
    Given los siguientes APs registrados para STA:
      | atletaId | valorAP_segundos |
      | A001     | 330              |
      | A002     | 360              |
      | A003     | 285              |
    When el organizador genera la grilla
    Then la grilla tiene 3 atletas
    And la posicion 1 corresponde al atleta "A002" con OT "10:00:00"
    And la posicion 2 corresponde al atleta "A001" con OT "10:09:00"
    And la posicion 3 corresponde al atleta "A003" con OT "10:18:00"
    And el evento GrillaDeSalidaGenerada persiste en el stream

  @US-2.1.2 @happy_path
  Scenario: Atleta sin AP no aparece en la grilla (RF-PR-04)
    Given los siguientes APs registrados para STA:
      | atletaId | valorAP_segundos |
      | A001     | 330              |
      | A002     | 360              |
    When el organizador genera la grilla
    Then la grilla tiene 2 atletas
    And "A001" aparece en la grilla
    And "A002" aparece en la grilla

  @US-2.1.2 @happy_path
  Scenario: Regenerar grilla antes de confirmar
    Given los siguientes APs registrados para STA:
      | atletaId | valorAP_segundos |
      | A001     | 330              |
    And la grilla ya fue generada previamente
    When el organizador regenera la grilla
    Then se emite un nuevo GrillaDeSalidaGenerada
    And hay 2 eventos GrillaDeSalidaGenerada en el stream

  @US-2.1.2 @error_case
  Scenario: Rechazo — intervalo no configurado
    Given una competencia "C003" sin intervalo OT configurado
    When el organizador intenta generar la grilla sin intervalo
    Then el sistema rechaza con error "IntervaloNoConfigurado"

  @US-2.1.2 @error_case
  Scenario: Rechazo — grilla ya confirmada
    Given los siguientes APs registrados para STA:
      | atletaId | valorAP_segundos |
      | A001     | 330              |
    And la grilla ya fue confirmada
    When el organizador intenta regenerar la grilla
    Then el sistema rechaza con error "GrillaYaConfirmada"

  @US-2.1.2 @happy_path
  Scenario: Grilla DNF (distancia menor→mayor)
    Given una competencia "C002" con disciplina "DNF" e intervalo 10 minutos
    And los siguientes APs registrados para DNF:
      | atletaId | valorAP_metros |
      | A001     | 80             |
      | A002     | 60             |
      | A003     | 100            |
    When se genera la grilla con OT inicio "09:00:00"
    Then la posicion 1 corresponde al atleta "A002"
    And la posicion 2 corresponde al atleta "A001"
    And la posicion 3 corresponde al atleta "A003"
