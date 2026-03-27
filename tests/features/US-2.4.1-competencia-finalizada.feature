Feature: Competencia Finalizada — disparo automático por política P-08
  # US-2.4.1 | INV-C-04
  # Como sistema, quiero detectar automáticamente cuando todas las performances
  # de una disciplina han finalizado y emitir CompetenciaFinalizada.

  Background:
    Given una competencia STA en estado EnEjecucion con 3 performances
    And las performances A y B están en estado Ejecutada
    And la performance C está en estado Llamada

  Scenario: Competencia finaliza automáticamente cuando el último atleta recibe tarjeta
    When el juez asigna tarjeta blanca a la performance C
    Then el evento TarjetaAsignada persiste en el stream de C
    And el sistema dispara CompetenciaFinalizada automáticamente
    And la competencia pasa al estado Finalizada

  Scenario: Competencia finaliza automáticamente cuando el último atleta registra DNS
    When el juez registra DNS para la performance C
    Then el evento DNSRegistrado persiste en el stream de C
    And el sistema dispara CompetenciaFinalizada automáticamente

  Scenario: No se finaliza si quedan performances pendientes
    Given una competencia STA con solo performance A en Ejecutada y B y C en Llamada
    When el juez asigna tarjeta blanca a performance B
    Then TarjetaAsignada persiste en el stream de B
    And CompetenciaFinalizada NO es emitido

  Scenario: Rechazo — finalizar manualmente sin que todas estén terminadas
    Given una competencia STA con performance C en estado AnunciadaAP
    When el sistema intenta finalizar la competencia directamente
    Then la operación es rechazada con CompetenciaNoFinalizable

  Scenario: CompetenciaFinalizada persiste en el stream de Competencia
    When el juez asigna tarjeta blanca a la performance C
    And el sistema dispara CompetenciaFinalizada automáticamente
    Then el stream de la Competencia contiene el evento CompetenciaFinalizada
    And el evento incluye competencia_id, disciplina y total_performances
