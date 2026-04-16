Feature: US-4.6.2 - Hash SHA-256 al cierre de disciplina

  Background:
    Given existe una competencia "comp-abc" con disciplina DNF en estado EnEjecucion
    And todas las performances de la disciplina estan cerradas o en DNS

  Scenario: el cierre persiste hash sha-256 en CompetenciaFinalizada
    When el organizador ejecuta el cierre de la disciplina
    Then la competencia pasa a estado Finalizada
    And el evento "CompetenciaFinalizada" contiene un campo "hash_sha256"
    And el hash tiene 64 caracteres hexadecimales

  Scenario: el hash es determinista para el mismo conjunto de eventos
    Given el conjunto de eventos de la disciplina no cambia
    When el sistema calcula el hash dos veces sobre la misma secuencia canonica
    Then ambos hashes son identicos

  Scenario: una alteracion en cualquier evento cambia el hash
    Given existe un hash original persistido para la disciplina
    When se altera el payload de un evento de la disciplina
    And se recalcula el hash sobre la secuencia modificada
    Then el nuevo hash es diferente del original

  Scenario: no se puede cerrar si quedan performances pendientes
    Given existe una performance en estado "ResultadoRegistrado" sin tarjeta asignada
    When el organizador intenta cerrar la disciplina
    Then el sistema rechaza la operacion por performances pendientes
    And no se emite "CompetenciaFinalizada"

  Scenario: disciplina sin performances genera hash del conjunto vacio
    Given la disciplina no tiene performances registradas
    When el organizador cierra la disciplina
    Then el hash persistido es el SHA-256 de la cadena vacia
