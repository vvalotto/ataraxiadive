Feature: US-4.3.4 - Tarjeta amarilla y resolucion de revision

  Background:
    Given el juez "juez@ataraxia.com" esta autenticado
    And la competencia C1 de disciplina DNF esta en estado EnEjecucion

  Scenario: asignar amarilla y resolver inmediatamente como blanca
    Given el juez esta en el Paso 6 de Garcia, Ana con RP 75.00 ya registrado
    When toca "TARJETA AMARILLA"
    Then el backend recibe POST /competencia/C1/asignar-tarjeta con tipo Amarilla
    And la performance queda en estado EnRevision
    And la UI muestra la pantalla de revision pendiente
    When toca "RESOLVER -> BLANCA"
    Then el backend recibe POST /competencia/C1/resolver-revision con resolucion Blanca
    And ve el resultado final "TARJETA BLANCA"
    And regresa a la grilla con Garcia marcada como finalizada

  Scenario: volver a la grilla con amarilla pendiente
    Given el juez asigno tarjeta amarilla a Garcia, Ana
    When toca "Volver a la grilla"
    Then regresa a la grilla S-02
    And la fila de Garcia muestra estado "REVISION"
    And la fila sigue habilitada para retomarla

  Scenario: resolver amarilla pendiente desde la grilla como roja
    Given Garcia, Ana tiene una revision pendiente en la grilla
    When el juez toca la fila de Garcia
    Then ve la pantalla de resolucion de revision
    When toca "RESOLVER -> ROJA"
    And selecciona motivo "PROTOCOLO_SUPERFICIE"
    Then el backend recibe POST /competencia/C1/resolver-revision con resolucion Roja y motivo_dq PROTOCOLO_SUPERFICIE
    And la grilla actualiza a Garcia como ROJA

  Scenario: resolver roja sin motivo queda bloqueado
    Given el juez esta en la pantalla de revision de Garcia
    When selecciona resolucion Roja sin motivo
    Then el boton de confirmar queda deshabilitado
