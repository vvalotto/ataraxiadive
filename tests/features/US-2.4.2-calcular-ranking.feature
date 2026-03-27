Feature: Calcular Ranking al finalizar disciplina
  # US-2.4.2 | RF-PM-03
  # Como organizador, quiero ver el ranking automáticamente al finalizar la
  # competencia, con podio destacado y reglas de empate correctas.

  Background:
    Given una competencia STA finalizada con 4 performances
    And los resultados son: C=310s blanca, A=295s blanca, D=295s blanca, B=DNS

  Scenario: Ranking calculado correctamente — STA mayor tiempo primero
    When el sistema calcula el ranking
    Then el evento ResultadosCalculados persiste
    And el ranking es posición 1 para C con 310s
    And el ranking es posición 2 para A con 295s
    And el ranking es posición 2 para D con 295s
    And B aparece en posición 4 como DNS

  Scenario: Podio destacado en las primeras 3 posiciones
    When el sistema calcula el ranking
    Then C tiene en_podio igual a True
    And A tiene en_podio igual a True
    And D tiene en_podio igual a True
    And B tiene en_podio igual a False

  Scenario: Empate comparte posición y salta la siguiente
    When el sistema calcula el ranking
    Then A y D tienen posición 2
    And no existe entrada con posición 3
    And B tiene posición 4

  Scenario: DNS va al final del ranking sin marca numérica
    When el sistema calcula el ranking
    Then B aparece después de todas las performances válidas
    And B no tiene marca numérica

  Scenario: Tarjeta roja va al final del ranking junto a DNS
    Given además el atleta E recibió tarjeta roja con RP 280s
    When el sistema calcula el ranking
    Then E aparece después de C, A y D
    And E tiene en_podio igual a False

  Scenario: Ranking consultable via endpoint REST
    Given el ranking fue calculado para la competencia
    When se consulta GET /resultados/{id}/ranking con disciplina STA
    Then la respuesta tiene status 200
    And la respuesta incluye posición, atleta_id, rp y tarjeta para cada entrada

  Scenario: Ranking DNF ordena por distancia mayor primero
    Given una competencia DNF finalizada con 3 performances
    And los resultados DNF son: X=85m blanca, Y=92m blanca, Z=DNS
    When el sistema calcula el ranking DNF
    Then el orden DNF es posición 1 para Y con 92m
    And el orden DNF es posición 2 para X con 85m
    And Z aparece en posición 3 como DNS en DNF
