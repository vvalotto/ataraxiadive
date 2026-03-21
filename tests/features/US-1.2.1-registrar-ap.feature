@US-1.2.1
Feature: Registrar Announced Performance
  Como atleta o sistema,
  quiero declarar mi AP para una disciplina y competencia
  para quedar registrado en la grilla de salida.

  Background:
    Given una competencia activa con id "C001"
    And un participante con id "P001"
    And la disciplina "STA"

  Scenario: Atleta registra AP exitosamente
    Given no existe un AP previo del atleta para esta disciplina y competencia
    And el plazo de AP no ha vencido
    And la grilla no está confirmada
    When el atleta registra un AP de valor "330" unidad "Segundos"
    Then el AP queda registrado exitosamente
    And la performance queda en estado "AnunciadaAP"
    And el evento "APRegistrado" persiste en el event stream

  Scenario: Rechazo por AP ya registrado
    Given ya existe un AP del participante para esta disciplina y competencia
    When el atleta intenta registrar otro AP de valor "360" unidad "Segundos"
    Then el sistema rechaza la operación con error "APYaRegistrado"

  Scenario: Rechazo por valor AP igual a cero
    Given no existe un AP previo del atleta para esta disciplina y competencia
    When el atleta intenta registrar un AP de valor "0" unidad "Segundos"
    Then el sistema rechaza la operación con error "ValorAPInvalido"

  Scenario: Rechazo por valor AP negativo
    Given no existe un AP previo del atleta para esta disciplina y competencia
    When el atleta intenta registrar un AP de valor "-1" unidad "Metros"
    Then el sistema rechaza la operación con error "ValorAPInvalido"

  Scenario: Rechazo por plazo de AP vencido
    Given el plazo de AP ya venció para esta disciplina y competencia
    And no existe un AP previo del atleta para esta disciplina y competencia
    When el atleta intenta registrar un AP de valor "330" unidad "Segundos"
    Then el sistema rechaza la operación con error "PlazoAPVencido"

  Scenario: Rechazo por grilla ya confirmada
    Given la grilla ya fue confirmada para esta competencia
    And no existe un AP previo del atleta para esta disciplina y competencia
    When el atleta intenta registrar un AP de valor "330" unidad "Segundos"
    Then el sistema rechaza la operación con error "GrillaYaConfirmada"
