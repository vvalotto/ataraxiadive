Feature: US-5.1.4 - Generacion y ajuste de grilla desde el panel organizador

  Background:
    Given el organizador "org@ataraxia.com" esta autenticado con rol ORGANIZADOR
    And el torneo "BA 2026" con id "T1" esta en estado Preparacion
    And la disciplina "DNF" tiene 3 atletas con AP registrado

  Scenario: crear y visualizar grilla automatica
    Given no existe competencia para "DNF" en el torneo "T1"
    When el organizador accede al tab "Grilla" del torneo "T1"
    And selecciona la disciplina "DNF"
    And completa intervalo OT "8" minutos y primer OT "09:00"
    And toca "Generar grilla"
    Then el backend recibe POST "/competencia" con disciplina "DNF", intervalo "8" y torneo_id "T1"
    And la tabla muestra 3 atletas ordenados por posicion
    And los OT visibles son "09:00", "09:08" y "09:16"

  Scenario: reordenar posiciones de la grilla
    Given existe competencia "C1" para "DNF" en estado Configurada
    And la grilla tiene "Garcia" posicion 1, "Lopez" posicion 2 y "Ruiz" posicion 3
    When el organizador mueve la fila de "Ruiz" a la posicion 1
    Then el backend recibe POST "/competencia/C1/ajustar-grilla" con cambios de posicion
    And la tabla se actualiza con "Ruiz" posicion 1, "Lopez" posicion 2 y "Garcia" posicion 3
    And los OT visibles son "09:00", "09:08" y "09:16"

  Scenario: confirmar grilla
    Given existe competencia "C1" para "DNF" en estado Configurada con 3 atletas
    When el organizador toca "Confirmar grilla"
    Then el backend recibe POST "/competencia/C1/confirmar-grilla"
    And la tabla pasa a modo solo lectura
    And el estado de la competencia muestra "Grilla confirmada"

  Scenario: grilla confirmada es solo lectura
    Given existe competencia "C1" para "DNF" en estado GrillaConfirmada
    When el organizador accede al tab "Grilla"
    And selecciona la disciplina "DNF"
    Then ve la grilla sin controles de reordenamiento
    And el boton "Confirmar grilla" no aparece

  Scenario: sin atletas en grilla el boton confirmar esta deshabilitado
    Given existe competencia "C1" para "DNF" en estado Configurada sin atletas
    When el organizador accede al tab "Grilla"
    And selecciona la disciplina "DNF"
    Then el boton "Confirmar grilla" esta deshabilitado
