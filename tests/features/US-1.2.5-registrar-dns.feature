@US-1.2.5
Feature: Registrar DNS
  Como juez,
  quiero registrar que un atleta no se presentó a su Official Top (DNS)
  para cerrar el ciclo de actuación sin resultado y sin tarjeta.

  Background:
    Given una competencia activa con id "C001" en estado "EnEjecucion"
    And un atleta con id "P001" en disciplina "DNF"
    And la performance del atleta tiene AP registrado de 50 metros y fue llamada

  Scenario: Juez registra DNS exitosamente desde estado Llamada
    When el juez registra el DNS con registrado_por="juez-001"
    Then la performance pasa al estado "DNS"
    And el evento DNSRegistrado persiste en el event stream
    And el evento contiene registradoPor="juez-001"

  Scenario: Rechazo — performance no está en Llamada (estado AnunciadaAP) (INV-P-08)
    Given la performance del atleta está en estado "AnunciadaAP"
    When el juez intenta registrar DNS con registrado_por="juez-001"
    Then el sistema rechaza la operación con error "EstadoInvalidoParaRegistrarDNS"
    And la performance permanece en estado "AnunciadaAP"

  Scenario: Rechazo — performance ya tiene resultado registrado (INV-P-09)
    Given la performance del atleta tiene RP registrado de 50.5 metros
    When el juez intenta registrar DNS con registrado_por="juez-001"
    Then el sistema rechaza la operación con error "EstadoInvalidoParaRegistrarDNS"
    And la performance permanece en estado "ResultadoRegistrado"
