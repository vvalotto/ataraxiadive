Feature: US-ADJ-10.4 - Vista post-torneo en portal del atleta

  # Nota: escenarios de UI (Home y Detalle) son validados manualmente.
  # Los escenarios BDD verifican los contratos de API que el frontend consume.

  Background:
    Given el sistema de identidad y registro esta inicializado con DB temporal

  Scenario: El snapshot del portal incluye entradas de torneos CERRADO
    Given un atleta registrado inscripto en un torneo CERRADO con competencia y resultado
    When el atleta solicita su portal snapshot
    Then la respuesta incluye al menos una entrada con estado de torneo "CERRADO"
    And la entrada contiene competenciaId no nulo

  Scenario: El ranking de una competencia CERRADA devuelve resultados del atleta
    Given un torneo en estado CERRADO con una competencia DNF y resultados registrados
    When se consulta el ranking de esa competencia para la disciplina DNF
    Then la respuesta es 200
    And el ranking contiene al menos una entrada con rp no nulo

  Scenario: El overall de un torneo CERRADO es accesible
    Given un torneo en estado CERRADO con puntos FAAS calculados
    When se consulta el overall del torneo
    Then la respuesta es 200

  Scenario: Home no muestra torneos CERRADO en seccion de inscripciones activas (invariante INV-ADJ-10.4-03)
    Given un atleta con un torneo en EJECUCION y otro en CERRADO
    When el frontend carga las inscripciones activas
    Then solo el torneo en EJECUCION aparece en la seccion "inscripciones activas"
    And el torneo CERRADO no aparece mezclado con los activos
