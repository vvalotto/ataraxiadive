# US-2.1.3: Ajustar Grilla Manualmente
# BC: competencia | Incremento: Inc 2.1 — La Grilla de Salida
# Invariantes: INV-C-02 (parcial) | Políticas: P-02

@US-2.1.3
Feature: Ajustar Grilla Manualmente

  Background:
    Given la competencia "C001" tiene grilla generada con 3 atletas STA e intervalo 9 min

  @US-2.1.3 @happy_path
  Scenario: Ajustar posición de un atleta recalcula OTs
    When el organizador ajusta la posicion del atleta "A001" a 1 en "C001"
    Then la grilla de "C001" queda: "A001" en posicion 1, "A002" en posicion 2
    And los OTs de "C001" son: posicion 1 = "10:00:00", posicion 2 = "10:09:00"
    And el evento GrillaDeSalidaAjustada persiste en el stream de "C001"

  @US-2.1.3 @happy_path
  Scenario: Ajustar andarivel de un atleta no afecta los demás
    When el organizador asigna andarivel 2 al atleta "A002" en "C001"
    Then el atleta "A002" en "C001" queda con andarivel 2
    And los atletas "A001" y "A003" de "C001" mantienen andarivel 1
    And el evento GrillaDeSalidaAjustada persiste en el stream de "C001"

  @US-2.1.3 @happy_path
  Scenario: Ajuste acumulativo sobre ajuste previo
    Given ya se aplicó un ajuste previo en "C001" (A001 a posicion 1)
    When el organizador asigna andarivel 2 al atleta "A001" en "C001"
    Then hay 2 eventos GrillaDeSalidaAjustada en el stream de "C001"

  @US-2.1.3 @error_case
  Scenario: Rechazo — grilla no generada aún
    Given la competencia "C002" tiene solo el intervalo configurado (sin grilla)
    When el organizador intenta ajustar la grilla de "C002"
    Then el ajuste de "C002" es rechazado con "GrillaNoGenerada"

  @US-2.1.3 @error_case
  Scenario: Rechazo — grilla ya confirmada (INV-C-02)
    Given la grilla de "C001" está confirmada
    When el organizador intenta ajustar la grilla de "C001"
    Then el ajuste de "C001" es rechazado con "GrillaYaConfirmada"
