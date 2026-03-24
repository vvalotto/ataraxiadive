@US-1.2.6
Feature: Corregir Resultado
  Como juez,
  quiero corregir el resultado registrado de un atleta ya ejecutado
  para rectificar un error de registro manteniendo la trazabilidad completa.

  Background:
    Given una competencia activa con id "C001" en estado "EnEjecucion"
    And un atleta con id "P001" en disciplina "DNF"
    And la performance del atleta tiene AP registrado de 50 metros y fue llamada
    And la performance del atleta tiene resultado de 49.5 metros registrado
    And la performance del atleta tiene tarjeta "Blanca" asignada

  Scenario: Juez corrige resultado exitosamente desde estado Ejecutada
    When el juez corrige el resultado a 51.0 metros con motivo="Error de lectura" por "juez-001"
    Then la performance permanece en estado "Ejecutada"
    And el evento ResultadoCorregido persiste en el event stream
    And el evento contiene valorRpNuevo="51.0" y registradoPor="juez-001"

  Scenario: Rechazo — performance no está en Ejecutada (estado DNS) (INV-P-13)
    Given la performance del atleta está en estado "DNS"
    When el juez intenta corregir el resultado a 51.0 metros con motivo="Error" por "juez-001"
    Then el sistema rechaza la operación con error "EstadoInvalidoParaCorregirResultado"

  Scenario: Rechazo — motivo ausente (INV-P-12)
    When el juez intenta corregir el resultado a 51.0 metros sin motivo por "juez-001"
    Then el sistema rechaza la operación con error "MotivoObligatorio"
