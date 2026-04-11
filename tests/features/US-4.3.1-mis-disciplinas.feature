Feature: US-4.3.1 - Mis disciplinas asignadas al juez

  Background:
    Given el juez "juez@ataraxia.com" esta autenticado con rol juez
    And existe el torneo "BA 2025" en estado EnEjecucion

  Scenario: juez ve sus disciplinas asignadas con estado correcto
    Given el juez tiene asignadas las disciplinas DNF y CWTB
    And la competencia de DNF esta en estado EnEjecucion
    And la competencia de CWTB esta en estado Configurada
    When accede a /juez/disciplinas
    Then ve dos DisciplinaCard: DNF (ACTIVA) y CWTB (PENDIENTE)
    And solo la card DNF es tappable

  Scenario: tap en disciplina activa navega a la grilla
    Given el juez tiene asignada la disciplina DNF en estado ACTIVA
    When toca la card de DNF
    Then navega a /juez/grilla con la competencia de DNF seleccionada
    And useCompetenciaStore.disciplinaActiva es "DNF"

  Scenario: sin torneo activo muestra mensaje de espera
    Given no existe ningun torneo en estado EnEjecucion
    When accede a /juez/disciplinas
    Then ve el mensaje "No hay torneo en curso"

  Scenario: sin disciplinas asignadas muestra mensaje informativo
    Given el juez no tiene disciplinas asignadas en el torneo activo
    When accede a /juez/disciplinas
    Then ve el mensaje "Sin disciplinas asignadas"
