Feature: US-4.3.3 — Casos alternativos del flujo de performance

  Background:
    Given el juez "juez@ataraxia.com" está autenticado
    And la competencia C1 de disciplina DNF está en estado EnEjecucion

  Scenario: DNS desde flujo llamado
    Given el juez está en el Paso 2 de García, Ana
    When toca "DNS — No se presenta"
    Then ve la pantalla de confirmación DNS con los datos de García
    When toca "CONFIRMAR DNS"
    Then el backend recibe POST /competencia/C1/registrar-dns con participante_id de García
    And ve el resultado "DNS registrado — No se presentó"
    When toca "SIGUIENTE ATLETA →"
    Then regresa a la grilla con García marcada como DNS

  Scenario: BKO durante la performance — tarjeta roja automática
    Given el juez está en el Paso 4 de García, Ana
    When toca "BKO — Black-out"
    Then ve la pantalla de BKO con selector de distancia obligatorio
    And el botón "CONFIRMAR BKO" está deshabilitado
    When ingresa 62m 50cm
    And selecciona motivo "BKO_SUBACUATICO"
    Then el botón "CONFIRMAR BKO" se habilita
    When toca "CONFIRMAR BKO — TARJETA ROJA"
    Then el backend recibe POST /competencia/C1/registrar-resultado con valor_rp=62.50
    And el backend recibe POST /competencia/C1/asignar-tarjeta con tarjeta=Roja y motivo_dq=BKO_SUBACUATICO
    And ve el resultado "Performance completada — TARJETA ROJA"

  Scenario: tarjeta roja por protocolo de superficie
    Given el juez está en el Paso 6 de García, Ana
    When toca "TARJETA ROJA"
    Then ve el selector de MotivoDQ
    When selecciona "PROTOCOLO_SUPERFICIE"
    And toca "CONFIRMAR ROJA"
    Then el backend recibe POST /competencia/C1/asignar-tarjeta con tarjeta=Roja y motivo_dq=PROTOCOLO_SUPERFICIE

  Scenario: tarjeta blanca con penalizaciones en DNF
    Given el juez está en el Paso 6 de García, Ana con RP=75m registrado
    When toca "TARJETA BLANCA"
    And agrega 2 penalizaciones técnicas
    And toca "CONFIRMAR BLANCA"
    Then el backend recibe POST /competencia/C1/asignar-tarjeta con tipo=BlancaConPenalizaciones y 2 penalizaciones
    And ve el resultado "Performance completada — TARJETA BLANCA"

  Scenario: penalizaciones no permitidas en STA
    Given el juez está en el Paso 6 de un atleta de STA
    When intenta agregar penalizaciones técnicas
    Then el selector de penalizaciones está deshabilitado con mensaje "STA no admite penalizaciones"

  Scenario: motivo BKO requiere distancia obligatoria
    Given el juez está en la pantalla de BKO
    When selecciona motivo "BKO_SUPERFICIE"
    And no ingresa distancia
    Then el botón "CONFIRMAR BKO" permanece deshabilitado
