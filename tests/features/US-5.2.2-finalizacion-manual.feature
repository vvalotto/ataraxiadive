Feature: US-5.2.2 — Finalizacion manual de prueba por disciplina

  Background:
    Given el organizador "org@ataraxia.com" esta autenticado con rol ORGANIZADOR
    And el torneo "BA 2026" con id T1 esta en estado EJECUCION
    And la disciplina DNF tiene competencia C1 en estado EnEjecucion

  Scenario: finalizar manualmente una disciplina sin pendientes
    Given C1 tiene 10 performances totales
    And 8 performances estan ejecutadas
    And 2 performances estan DNS
    When el organizador selecciona DNF en el tab "Ejecucion"
    Then ve la accion "Finalizar prueba" habilitada
    When toca "Finalizar prueba"
    Then el frontend envia POST /competencia/C1/finalizar con disciplina DNF
    And la competencia C1 queda en estado Finalizada
    And se registra CompetenciaFinalizada con origen "manual"

  Scenario: no se puede finalizar si quedan performances pendientes
    Given C1 tiene 10 performances totales
    And 7 performances estan completadas
    And 3 performances estan pendientes
    When el organizador selecciona DNF en el tab "Ejecucion"
    Then la accion "Finalizar prueba" esta deshabilitada
    And el detalle muestra "Quedan 3 performances pendientes"
    And no se envia POST /competencia/C1/finalizar

  Scenario: cierre automatico sigue funcionando
    Given C1 tiene 10 performances totales
    And 9 performances ya estan cerradas
    When el juez asigna la tarjeta final de la ultima performance
    Then P-08 emite CompetenciaFinalizada automaticamente
    And el evento queda registrado con origen "automatico"
