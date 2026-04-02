Feature: Politica P-09 - calculo automatico del overall
  # US-3.5.2 | INV-P09-01 | INV-P09-02 | INV-P09-03 | INV-P09-04 | INV-P09-05
  # Como sistema, quiero calcular automaticamente el overall cuando
  # finaliza la ultima disciplina de un torneo.

  Scenario: torneo de una sola disciplina dispara ranking y overall al finalizar
    Given un torneo con una sola disciplina STA y competencia asociada
    When la competencia STA finaliza
    Then P-08 calcula el ranking de STA
    And P-09 calcula el overall del torneo

  Scenario: la primera disciplina finalizada no dispara overall si faltan disciplinas
    Given un torneo con disciplinas STA y DNF
    And la disciplina DNF aun no finalizo
    When la competencia STA finaliza
    Then P-08 calcula el ranking de STA
    And P-09 no calcula el overall del torneo

  Scenario: la ultima disciplina pendiente dispara el overall
    Given un torneo con disciplinas STA y DNF
    And la disciplina STA ya finalizo con ranking calculado
    When la competencia DNF finaliza
    Then P-08 calcula el ranking de DNF
    And P-09 calcula el overall del torneo

  Scenario: competencia sin torneo_id no activa P-09
    Given una competencia standalone sin torneo_id
    When la competencia finaliza
    Then P-08 calcula el ranking de la competencia
    And P-09 no se activa

  Scenario: recalculo sobre torneo ya resuelto no duplica el overall
    Given un torneo cuyo overall ya fue calculado
    When se recibe otra finalizacion para una disciplina del mismo torneo
    Then no se persiste un segundo evento de ranking overall calculado
