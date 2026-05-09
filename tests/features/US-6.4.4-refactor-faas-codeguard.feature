Feature: US-6.4.4 - AlgoritmoPuntajeFAAS refactorizado y CodeGuard limpio

  Scenario: DesignReviewer no reporta DR-02 en AlgoritmoPuntajeFAAS
    Given los cambios de US-6.4.4 aplicados
    When se ejecuta DesignReviewer sobre resultados/domain/services/algoritmo_faas.py
    Then no hay hallazgos LCOM elevados para AlgoritmoPuntajeFAAS

  Scenario: Calculo de distancia conserva resultados numericos
    Given un conjunto de resultados validos e invalidos para DYN
    When se calcula el puntaje con AlgoritmoPuntajeFAAS
    Then los puntos por atleta son identicos al comportamiento previo

  Scenario: Calculo de tiempo conserva resultados numericos
    Given un conjunto de resultados validos e invalidos para STA
    When se calcula el puntaje con AlgoritmoPuntajeFAAS
    Then los puntos por atleta son identicos al comportamiento previo

  Scenario: CodeGuard no reporta E501 ni imports huerfanos
    Given los cambios de US-6.4.4 aplicados
    When se ejecuta CodeGuard sobre src/
    Then no hay hallazgos E501 ni imports sin uso asociados a CG-01/03/04/05

  Scenario: Formato e imports quedan estables
    Given los cambios de US-6.4.4 aplicados
    When se ejecutan black --check e isort --check sobre src/ y tests/
    Then ambas verificaciones finalizan sin cambios pendientes
