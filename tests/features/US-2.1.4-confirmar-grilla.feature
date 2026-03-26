# US-2.1.4: Confirmar Grilla + Iniciar Competencia
# BC: competencia | Incremento: Inc 2.1 — La Grilla de Salida
# Invariantes: INV-C-02 (completo), INV-C-03 | Políticas: P-04, P-06

@US-2.1.4
Feature: Confirmar Grilla e Iniciar Competencia

  Background:
    Given la competencia "C001" tiene grilla generada y lista para confirmar

  @US-2.1.4 @happy_path
  Scenario: Confirmar grilla exitosamente
    When el organizador confirma la grilla de "C001"
    Then el evento GrillaConfirmada persiste en el stream de "C001"
    And la competencia "C001" está en estado "Confirmada"
    And GenerarGrilla queda bloqueado para "C001"

  @US-2.1.4 @error_case
  Scenario: Rechazo — confirmar sin grilla generada
    Given la competencia "C002" no tiene grilla generada
    When el organizador intenta confirmar la grilla de "C002"
    Then la confirmación de "C002" es rechazada con "GrillaNoGenerada"

  @US-2.1.4 @error_case
  Scenario: Rechazo — confirmar grilla ya confirmada
    Given la grilla de "C001" ya fue confirmada previamente
    When el organizador intenta confirmar la grilla de "C001" de nuevo
    Then la confirmación de "C001" es rechazada con "GrillaYaConfirmada"

  @US-2.1.4 @happy_path
  Scenario: Iniciar competencia exitosamente
    Given la grilla de "C001" ya fue confirmada previamente
    When el juez inicia la competencia "C001"
    Then el evento CompetenciaIniciada persiste en el stream de "C001"
    And la competencia "C001" está en estado "EnEjecucion"

  @US-2.1.4 @error_case
  Scenario: Rechazo — iniciar sin grilla confirmada (INV-C-03)
    When el juez intenta iniciar la competencia "C001" sin confirmar
    Then el inicio de "C001" es rechazado con "CompetenciaNoConfirmada"

  @US-2.1.4 @happy_path
  Scenario: CompetenciaEstadoAdapter real — is_grilla_confirmada
    Given la grilla de "C001" ya fue confirmada previamente
    When se consulta is_grilla_confirmada para "C001"
    Then el adaptador retorna True

  @US-2.1.4 @happy_path
  Scenario: CompetenciaEstadoAdapter real — is_en_ejecucion
    Given la competencia "C001" fue iniciada
    When se consulta is_en_ejecucion para "C001"
    Then el adaptador retorna True
