Feature: US-4.6.1 - API audit log de performance

  Background:
    Given existe una competencia "comp-abc" con disciplina DNF
    And el atleta "ath-123" tiene eventos registrados en el event store

  Scenario: organizador consulta audit log exitosamente
    Given el usuario autenticado tiene rol organizador
    When hace GET /competencias/comp-abc/performances/ath-123/audit-log
    Then la respuesta es 200 OK
    And contiene 3 eventos en orden cronologico
    And el primer evento es de tipo "PerformanceRegistrada"

  Scenario: el audit log incluye correcciones historicas
    Given la performance del atleta fue corregida
    And el usuario autenticado tiene rol organizador
    When hace GET /competencias/comp-abc/performances/ath-123/audit-log
    Then la respuesta incluye 4 eventos
    And el ultimo evento es de tipo "ResultadoCorregido"
    And el evento original de resultado no fue eliminado del log

  Scenario: performance inexistente retorna 404
    Given el usuario autenticado tiene rol organizador
    When hace GET /competencias/comp-abc/performances/ath-999/audit-log
    Then la respuesta es 404 Not Found

  Scenario: juez no puede consultar audit log
    Given el usuario autenticado tiene rol juez
    When hace GET /competencias/comp-abc/performances/ath-123/audit-log
    Then la respuesta es 403 Forbidden

  Scenario: los eventos se exponen con sequence estricto
    Given el usuario autenticado tiene rol organizador
    When hace GET /competencias/comp-abc/performances/ath-123/audit-log
    Then los eventos aparecen en orden sequence 1, 2, 3
    And cada evento expone los campos "sequence", "tipo", "timestamp" y "datos"
