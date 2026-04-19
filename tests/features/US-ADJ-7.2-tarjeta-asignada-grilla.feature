@US-ADJ-7.2
Feature: Grilla de competencia expone tarjeta_asignada
  Como organizador
  Quiero ver la tarjeta asignada de cada atleta en la grilla de auditoria
  Para identificar rapidamente resultados validos, penalizados o descalificados

  Scenario: La grilla incluye tarjeta_asignada para atletas ejecutados
    Given una competencia con atletas ejecutados con tarjeta blanca, tarjeta roja y tarjeta con penalizaciones
    When el organizador consulta la grilla de la competencia
    Then la respuesta incluye tarjeta_asignada para cada atleta con tarjeta final

  Scenario: La grilla incluye tarjeta_asignada nula para atletas sin tarjeta final
    Given una competencia con atletas en llamada, resultado registrado, revision y DNS
    When el organizador consulta la grilla de la competencia
    Then la respuesta incluye tarjeta_asignada null para cada atleta sin tarjeta final

  Scenario: La auditoria usa tarjeta_asignada para distinguir visualmente resultados
    Given una grilla de auditoria con tarjetas blanca, blanca con penalizaciones, roja y sin tarjeta
    When el organizador abre la auditoria de competencia
    Then cada atleta se muestra con el estilo correspondiente a su tarjeta_asignada
