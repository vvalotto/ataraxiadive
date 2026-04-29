Feature: US-ADJ-9.7 - AP declarados durante inscripcion como requisito de preparacion

  Background:
    Given existe el torneo "BA Open 2026" en fase "INSCRIPCION_ABIERTA"
    And el organizador esta autenticado
    And hay inscripciones activas por disciplina en el torneo

  Scenario: organizador ve estado AP por atleta y disciplina en inscriptos
    Given Ana declaro AP para DNF
    And Carlos todavia no declaro AP para DYN
    When el organizador abre la seccion Inscriptos
    Then Ana aparece con estado "AP declarado" en DNF
    And Carlos aparece con estado "AP pendiente" en DYN

  Scenario: no se puede cerrar inscripcion con AP faltantes
    Given existe al menos una inscripcion activa sin AP requerido
    When el organizador intenta cerrar la inscripcion
    Then el sistema rechaza la transicion a "PREPARACION"
    And informa que faltan AP por completar

  Scenario: se puede cerrar inscripcion cuando todos los AP estan completos
    Given todas las inscripciones activas tienen AP valido
    When el organizador cierra la inscripcion
    Then el torneo pasa a fase "PREPARACION"

  Scenario: la grilla usa AP declarados desde inscripcion
    Given el torneo esta en fase "PREPARACION"
    And existen inscripciones activas con AP declarado para la disciplina
    When el organizador genera la grilla
    Then la grilla se calcula usando los AP declarados en inscripcion
    And no requiere performances preexistentes cargadas manualmente
