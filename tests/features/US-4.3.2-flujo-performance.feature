Feature: US-4.3.2 - Flujo de performance del juez conectado al backend

  Background:
    Given el juez "juez@ataraxia.com" esta autenticado
    And la competencia C1 de disciplina DNF esta en estado EnEjecucion
    And el atleta "Garcia, Ana" tiene AP 75m en AnunciadaAP

  Scenario: flujo completo exitoso con tarjeta blanca
    Given el juez esta en la grilla de la competencia C1
    When toca la fila de "Garcia, Ana" en estado PENDIENTE
    Then ve el Paso 1 con el boton "LLAMAR ATLETA"
    When toca "LLAMAR ATLETA"
    Then el backend recibe POST /competencia/C1/llamar para la performance seleccionada
    And la UI avanza al Paso 2
    When confirma presencia y avanza hasta el Paso 5
    And ingresa 72m 00cm
    And toca "CONFIRMAR MARCA"
    Then el backend recibe POST /competencia/C1/registrar-resultado con valor_rp 72.00
    When en el Paso 6 toca "TARJETA BLANCA"
    Then el backend recibe POST /competencia/C1/asignar-tarjeta con tipo Blanca
    And ve la pantalla final de performance completada
    When toca "SIGUIENTE ATLETA"
    Then regresa a la grilla S-02

  Scenario: la grilla muestra estados visibles segun la performance
    Given la grilla tiene performances en estados AnunciadaAP, Llamada y TarjetaAsignada
    When el juez accede a /juez/grilla
    Then la performance TarjetaAsignada aparece deshabilitada
    And la performance Llamada aparece destacada como en curso
    And la performance AnunciadaAP aparece disponible para iniciar

  Scenario: boton confirmar marca deshabilitado sin RP ingresado
    Given el juez esta en el Paso 5
    When no ingresa metros ni centimetros
    Then el boton "CONFIRMAR MARCA" esta deshabilitado

  Scenario: error del backend se muestra inline y no rompe el flujo
    Given el juez intenta llamar una performance que ya no esta en AnunciadaAP
    When el backend responde 409
    Then la pantalla muestra "No se puede ejecutar esta accion en el estado actual"
    And el juez permanece en el paso actual
