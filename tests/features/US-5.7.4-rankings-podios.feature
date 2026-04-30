Feature: US-5.7.4 - Rankings y podios del atleta
  Como atleta autenticado
  Quiero ver el ranking de mi categoria y el overall
  Para conocer mi posicion respecto al resto de competidores

  Background:
    Given el atleta "ana@email.com" con atleta_id "aaa" y categoria "SENIOR_FEMENINO" esta autenticado
    And existe la competencia DNF con ranking calculado
    And el ranking SENIOR_FEMENINO de DNF tiene Ana pos=1 100pts, Laura pos=2 85pts, Maria pos=3 72pts
    And el torneo NO tiene overall calculado aun

  Scenario: atleta ve ranking de su categoria bajo el ResultHero
    When Ana navega a "/atleta/resultados"
    Then ve la card "Ranking Senior Femenino" bajo el ResultHero de DNF
    And la fila de Ana muestra texto "Vos" y fondo accent tenue
    And las posiciones 1, 2 y 3 tienen distincion visual de top 3
    And al pie de la card aparece "Ranking final"

  Scenario: overall no disponible muestra estado vacio con icono trofeo
    When Ana navega a "/atleta/resultados"
    Then ve la seccion Overall con texto "Disponible al finalizar todas las disciplinas del torneo"
    And no ve filas de ranking en la seccion Overall

  Scenario: overall disponible muestra categoria propia resaltada
    Given el overall fue calculado con Ana pos=2 en SENIOR_FEMENINO con 185 puntos
    When Ana navega a "/atleta/resultados"
    Then ve la seccion "Ranking Overall Senior Femenino"
    And la fila de Ana en overall muestra posicion 2 con fondo accent tenue

  Scenario: ranking parcial muestra pie con advertencia
    Given el ranking de DNF tiene calculado=false
    When Ana navega a "/atleta/resultados"
    Then al pie de la card de DNF aparece "Ranking parcial"

  Scenario: atleta con DNS aparece en el ranking
    Given Ana tiene DNS en DNF con es_dns=true
    When Ana navega a "/atleta/resultados"
    Then la fila de Ana en el ranking muestra chip "DNS"
