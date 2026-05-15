Feature: US-5.6.3 — RankingCompetencia con puntos FAAS por categoria

  Background:
    Given un algoritmo FAAS inyectado en el aggregate

  Scenario: ranking incluye puntos FAAS por atleta en DNF
    Given una disciplina DNF con Ana (70m Blanca, SENIOR_FEMENINO) y Luis (56m Blanca, SENIOR_FEMENINO)
    When se calcula el ranking con algoritmo FAAS
    Then Ana tiene puntos = 100.00 en su EntradaRanking
    And Luis tiene puntos = 80.00 en su EntradaRanking

  Scenario: ranking agrupa y ordena por puntos dentro de cada categoria
    Given atletas en tres categorias con resultados DNF
      | atleta | categoria         | rp | tarjeta |
      | A      | SENIOR_MASCULINO  | 80 | Blanca  |
      | B      | SENIOR_MASCULINO  | 60 | Blanca  |
      | C      | SENIOR_FEMENINO   | 70 | Blanca  |
    When se calcula el ranking con algoritmo FAAS
    Then la posicion 1 en SENIOR_MASCULINO corresponde al atleta con mas puntos
    And la posicion 1 en SENIOR_FEMENINO corresponde al atleta con mas puntos

  Scenario: DNS tiene puntos 0.00 y no tiene posicion de podio
    Given Pedro con DNS en DNF categoria SENIOR_MASCULINO
    And Luis con RP 60m Blanca en DNF categoria SENIOR_MASCULINO
    When se calcula el ranking con algoritmo FAAS
    Then Pedro tiene puntos = 0.00
    And Pedro no tiene posicion de podio

  Scenario: evento ResultadosCalculados serializa y reconstituye puntos
    Given un ranking DNF calculado con algoritmo FAAS para Ana (70m) y Luis (56m)
    When se serializa y reconstituye el aggregate desde el event store
    Then el aggregate reconstituido tiene los mismos puntos que el original
    And la reconstitucion no require recalcular
