Feature: US-5.5.1 — Registro de APs del atleta

  Background:
    Given existe el torneo "BA Open 2026" con disciplinas DNF y STA
    And existen competencias creadas para DNF y STA
    And la atleta "ana@email.com" esta inscripta en DNF y STA
    And la grilla de DNF y STA no esta confirmada

  Scenario: atleta registra AP exitosamente
    Given "ana@email.com" esta autenticada con rol ATLETA
    When registra AP con disciplina DNF, valor_ap 70 y unidad Metros
    Then el sistema responde 201
    And existe un Performance en estado AnunciadaAP para ana y DNF

  Scenario: segundo AP para la misma disciplina es rechazado
    Given "ana@email.com" ya registro AP 70 para DNF
    When registra AP con disciplina DNF, valor_ap 65 y unidad Metros
    Then el sistema responde 409
    And el mensaje de error contiene "ya existe un AP"

  Scenario: valor AP cero es rechazado
    Given "ana@email.com" esta autenticada con rol ATLETA
    When registra AP con disciplina DNF, valor_ap 0 y unidad Metros
    Then el sistema responde 422

  Scenario: unidad incompatible con disciplina es rechazada
    Given "ana@email.com" esta autenticada con rol ATLETA
    When registra AP con disciplina DNF, valor_ap 70 y unidad Segundos
    Then el sistema responde 422

  Scenario: AP bloqueado si grilla ya fue confirmada
    Given la grilla de DNF esta confirmada
    When registra AP con disciplina DNF, valor_ap 70 y unidad Metros
    Then el sistema responde 409
