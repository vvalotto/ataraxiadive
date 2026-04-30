Feature: US-5.7.2 - Mi Grilla del atleta por disciplina
  Como atleta autenticado
  Quiero ver mi OT, andarivel y orden completo de salida
  Para organizar mi preparacion antes de competir

  Background:
    Given el atleta "ana@email.com" con atleta_id "aaa" esta autenticado
    And existe la competencia DNF con grilla confirmada
    And la grilla tiene a Luis pos 1 OT 14:09, Pedro pos 2 OT 14:18 y Ana pos 3 OT 14:27 andarivel 1

  Scenario: Atleta ve su OT hero destacado
    When Ana navega a "/atleta/grilla/{competenciaId}?disciplina=DNF"
    Then ve el hero card con "14:27" en tipografia grande
    And ve "Andarivel 1 · Posicion 3"
    And ve su AP declarado

  Scenario: Lista completa ordenada por posicion con fila propia resaltada
    When Ana navega a Mi Grilla de DNF
    Then la lista muestra primero a Luis, luego Pedro y luego Ana
    And la fila de Ana tiene el chip "TU" y fondo accent tenue

  Scenario: Grilla provisional muestra aviso
    Given la grilla no esta confirmada
    When Ana navega a Mi Grilla de DNF
    Then ve el aviso "Grilla provisional - puede cambiar antes del inicio"

  Scenario: Grilla no disponible muestra estado vacio
    Given la competencia aun no tiene grilla generada
    When Ana navega a Mi Grilla de DNF
    Then ve el mensaje "La grilla aun no esta disponible para esta disciplina."

  Scenario: Navegacion a resultados desde la grilla
    When Ana presiona "Ver mis resultados"
    Then navega a "/atleta/resultados" con competenciaId y disciplina en params
