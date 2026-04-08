@US-1.2.4
Feature: Asignar Tarjeta
  Como juez,
  quiero asignar la tarjeta (blanca, amarilla o roja) a un atleta una vez registrado su resultado
  para determinar la validez de la performance y cerrar el ciclo de actuación.

  Background:
    Given una competencia activa con id "C001" en estado "EnEjecucion"
    And un atleta con id "P001" en disciplina "DNF"
    And la performance del atleta tiene AP registrado de 50 metros y RP de 50.5 metros
    And la performance está en estado "ResultadoRegistrado"

  Scenario: Juez asigna tarjeta blanca exitosamente
    When el juez asigna tarjeta blanca sin motivo asignada_por="juez-001"
    Then la performance pasa al estado "Ejecutada"
    And el evento TarjetaAsignada persiste en el event stream
    And el evento contiene tipo="Blanca", motivo_dq=null, motivo_texto=null y asignadaPor="juez-001"

  Scenario: Juez asigna tarjeta amarilla con motivo obligatorio
    When el juez asigna tarjeta amarilla con motivo="superficie sin protocolo" asignada_por="juez-001"
    Then la performance pasa al estado "Ejecutada"
    And el evento TarjetaAsignada persiste en el event stream
    And el evento contiene tipo="Amarilla", motivo_texto="superficie sin protocolo" y asignadaPor="juez-001"

  Scenario: Juez asigna tarjeta roja con motivo formal obligatorio
    When el juez asigna tarjeta roja con motivo_dq="PROTOCOLO_SUPERFICIE" asignada_por="juez-001"
    Then la performance pasa al estado "Ejecutada"
    And el evento TarjetaAsignada persiste en el event stream
    And el evento contiene tipo="Roja", motivo_dq="PROTOCOLO_SUPERFICIE" y asignadaPor="juez-001"

  Scenario: Rechazo — tarjeta amarilla sin motivo (INV-P-11)
    When el juez intenta asignar tarjeta amarilla sin motivo asignada_por="juez-001"
    Then el sistema rechaza la operación con error "MotivoObligatorio"
    And la performance permanece en estado "ResultadoRegistrado"

  Scenario: Rechazo — tarjeta roja sin motivo (INV-P-11)
    When el juez intenta asignar tarjeta roja sin motivo asignada_por="juez-001"
    Then el sistema rechaza la operación con error "MotivoDQObligatorio"
    And la performance permanece en estado "ResultadoRegistrado"

  Scenario: Rechazo — performance no está en ResultadoRegistrado (INV-P-07)
    Given la performance del atleta está en estado "Llamada"
    When el juez intenta asignar tarjeta blanca sin motivo asignada_por="juez-001"
    Then el sistema rechaza la operación con error "EstadoInvalidoParaAsignarTarjeta"
    And la performance permanece en estado "Llamada"
