Feature: Ejecución Multi-Andarivel — dos atletas simultáneos sin conflicto

  Background:
    Given una competencia STA en estado EnEjecucion con 2 andariveles
    And la grilla tiene pos 1 Atleta A andarivel 1, pos 2 Atleta B andarivel 2, pos 3 Atleta C andarivel 1

  Scenario: Llamar a atletas en andariveles distintos sin conflicto
    When el juez llama a Atleta A en andarivel 1
    And el juez llama a Atleta B en andarivel 2
    Then ambos AtletaLlamado persisten
    And GET andariveles muestra andarivel 1 ocupado por A y andarivel 2 ocupado por B

  Scenario: Rechazo al llamar a atleta en andarivel ya activo (INV-C-05)
    Given Atleta A fue llamado y esta en estado Llamada en andarivel 1
    When el juez intenta llamar a Atleta C en andarivel 1
    Then el sistema rechaza con error AndarivelesConflicto
    And ningun evento es persistido

  Scenario: Llamar al siguiente atleta del mismo andarivel tras finalizar el anterior
    Given Atleta A fue llamado en andarivel 1 y completo con tarjeta blanca
    When el juez llama a Atleta C en andarivel 1
    Then AtletaLlamado de Atleta C persiste
    And GET andariveles muestra andarivel 1 ocupado por C

  Scenario: AndarivelesActivos refleja estado correcto
    Given Atleta A fue llamado en andarivel 1 y esta en Llamada
    When se consulta GET andariveles de la competencia
    Then la respuesta muestra andarivel 1 ocupado con atleta A
    And andarivel 2 libre

  Scenario: GenerarGrilla con 2 andariveles distribuye posiciones correctamente
    Given una competencia STA en estado Preparacion con 4 atletas y 2 andariveles configurados
    When se genera la grilla
    Then las posiciones 1 y 3 quedan en andarivel 1
    And las posiciones 2 y 4 quedan en andarivel 2
