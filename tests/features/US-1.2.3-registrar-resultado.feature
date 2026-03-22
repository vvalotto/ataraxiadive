# language: es
@US-1.2.3
Feature: Registrar Resultado
  Como juez,
  quiero registrar el resultado efectivo de un atleta una vez que completa su performance
  para documentar el RP (Realized Performance) que luego determinará la tarjeta a asignar.

  Background:
    Given una competencia activa con id "C001" en estado "EnEjecucion"
    And un atleta con id "P001" en disciplina "DNF"
    And la performance del atleta tiene AP registrado de 50 metros
    And la performance está en estado "Llamada"

  Scenario: Juez registra el resultado exitosamente
    When el juez registra el resultado con valorRP=50.5 metros y registrado_por="juez-001"
    Then la performance pasa al estado "ResultadoRegistrado"
    And el evento ResultadoRegistrado persiste en el event stream
    And el evento contiene valorRP="50.5", unidad="Metros" y registradoPor="juez-001"

  Scenario: Rechazo — performance no está en estado Llamada (AnunciadaAP)
    Given la performance del atleta está en estado "AnunciadaAP"
    When el juez intenta registrar el resultado con valorRP=40.0 metros
    Then el sistema rechaza la operación con error "EstadoInvalidoParaRegistrarResultado"
    And la performance permanece en estado "AnunciadaAP"

  Scenario: Rechazo — performance ya está en estado DNS
    Given la performance del atleta está en estado "DNS"
    When el juez intenta registrar el resultado con valorRP=40.0 metros
    Then el sistema rechaza la operación con error "EstadoInvalidoParaRegistrarResultado"
    And la performance permanece en estado "DNS"
