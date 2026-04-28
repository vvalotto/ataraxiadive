Feature: US-ADJ-9.5 - Resultados del organizador alineados a S-04

  Background:
    Given existe un usuario autenticado con rol ORGANIZADOR
    And existe al menos un torneo con competencias visibles para el organizador

  Scenario: Resultados vive dentro del shell aprobado
    When el organizador abre la seccion Resultados
    Then ve la pantalla dentro del shell dark del organizador
    And el item Resultados aparece activo en la navbar

  Scenario: La pantalla conserva tabla y podios por disciplina
    Given existe una disciplina finalizada con ranking calculado
    When el organizador abre Resultados
    Then puede ver la tabla de ejecucion de la disciplina seleccionada
    And puede ver los podios por categoria y genero

  Scenario: El overall mantiene su comportamiento de disponibilidad
    Given no todas las disciplinas estan cerradas
    When el organizador ve Resultados
    Then el overall se muestra bloqueado
    Given todas las disciplinas estan cerradas
    Then el overall se muestra disponible

  Scenario: La relacion visual entre disciplina y overall es clara
    Given existe una disciplina activa seleccionada en Resultados
    When el organizador observa la pantalla
    Then distingue claramente el bloque principal de resultados por disciplina
    And distingue el bloque de overall como seccion separada y coherente
