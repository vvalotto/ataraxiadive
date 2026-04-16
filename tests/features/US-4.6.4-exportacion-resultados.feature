Feature: US-4.6.4 - Exportacion de resultados CSV y JSON

  Background:
    Given existe el torneo "trn-001" con disciplinas DNF y STA
    And el usuario esta autenticado como organizador

  Scenario: exportar en formato JSON
    When hace GET /resultados/trn-001/export?format=json
    Then la respuesta es 200 OK
    And el Content-Type es "application/json"
    And el header Content-Disposition contiene "resultados-trn-001.json"
    And el cuerpo contiene las secciones "disciplinas" y "overall"

  Scenario: exportar en formato CSV
    When hace GET /resultados/trn-001/export?format=csv
    Then la respuesta es 200 OK
    And el Content-Type es "text/csv; charset=utf-8"
    And el header Content-Disposition contiene "resultados-trn-001.csv"
    And la primera linea es el encabezado separado por punto y coma

  Scenario: format invalido devuelve 400
    When hace GET /resultados/trn-001/export?format=xlsx
    Then la respuesta es 400 Bad Request
    And el mensaje de error menciona "csv" y "json"

  Scenario: torneo inexistente devuelve 404
    When hace GET /resultados/00000000-0000-0000-0000-000000000999/export?format=json
    Then la respuesta es 404 Not Found

  Scenario: juez no puede exportar
    Given el usuario autenticado tiene rol juez
    When hace GET /resultados/trn-001/export?format=json
    Then la respuesta es 403 Forbidden

  Scenario: disciplina en ejecucion se exporta con resultados parciales y sin hash
    Given la disciplina STA esta en estado "EnEjecucion"
    When el organizador exporta en JSON
    Then la disciplina STA aparece en la exportacion
    And el campo "hash_sha256" de STA no aparece

  Scenario: disciplina cerrada incluye hash SHA-256
    Given la disciplina DNF esta finalizada con hash "a3f7c2d1"
    When el organizador exporta en JSON
    Then la disciplina DNF incluye el campo "hash_sha256"
