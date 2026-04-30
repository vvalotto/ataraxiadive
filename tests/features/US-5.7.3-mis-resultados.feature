Feature: US-5.7.3 - Mis resultados por disciplina
  Como atleta autenticado
  Quiero ver mi resultado personal por disciplina
  Para conocer RP, tarjeta y puntos cuando la organizacion publica resultados

  Background:
    Given el atleta "ana@email.com" con atleta_id "aaa" esta autenticado
    And Ana esta inscripta en "BA Open 2026" en DNF y STA
    And la disciplina DNF esta finalizada con ranking calculado
    And Ana obtuvo en DNF RP 70m, tarjeta blanca, 100.00 puntos, en podio y AP 68m
    And la disciplina STA aun no tiene ranking calculado

  Scenario: Resultado propio con tarjeta blanca se muestra en ResultHero
    When Ana navega a "/atleta/resultados"
    Then ve el ResultHero de DNF con estado "BLANCA"
    And ve RP "70 m", AP "68 m", diferencia "+2m" y puntos "100.00"
    And ve el chip "EN PODIO"

  Scenario: Disciplina pendiente muestra estado de espera
    When Ana navega a "/atleta/resultados"
    Then ve la card de STA con chip "PENDIENTE"
    And ve "Resultado disponible al cierre de la disciplina"
    And no ve RP ni puntos calculados para STA

  Scenario: DNS muestra tarjeta gris sin RP
    Given Ana tiene DNS en STA
    When Ana navega a "/atleta/resultados"
    Then el ResultHero de STA muestra chip "DNS"
    And RP es "-" y puntos es "-"

  Scenario: Atleta sin inscripciones ve estado vacio
    Given el atleta no esta inscripto en ningun torneo
    When navega a "/atleta/resultados"
    Then ve el mensaje "Aun no tenes resultados publicados."
