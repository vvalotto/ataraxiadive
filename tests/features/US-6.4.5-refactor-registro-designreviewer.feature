Feature: US-6.4.5 - DesignReviewer sin DR-06/DR-07 en registro

  Background:
    Given el bounded context registro existe
    And la especificacion US-6.4.5 esta aprobada

  Scenario: DR-06 se investiga como coordination handler
    Given DeclararAPInscripcionHandler solo ejecuta load, domain method y save
    When se revisa la responsabilidad del handler
    Then DR-06 queda documentado como falso positivo estructural
    And el handler no incorpora logica de dominio nueva

  Scenario: SQLiteInscripcionRepository delega reconstitucion al aggregate
    Given una fila SQLite de inscripcion con disciplinas y AP declarados
    When el repositorio reconstruye la inscripcion
    Then llama a Inscripcion.from_row con los datos planos de la fila
    And el repositorio no importa APDeclarado, Disciplina ni UnidadMedida

  Scenario: La reconstitucion preserva adjuntos
    Given una inscripcion persistida con apto medico y constancia de pago
    When se consulta por id desde SQLiteInscripcionRepository
    Then la inscripcion retornada conserva apto_medico_path
    And la inscripcion retornada conserva constancia_pago_path

  Scenario: La reconstitucion preserva AP por disciplina
    Given una inscripcion persistida con AP declarado para una disciplina
    When se consulta por id desde SQLiteInscripcionRepository
    Then la inscripcion retornada conserva el valor AP
    And la inscripcion retornada conserva la unidad AP

  Scenario: Quality gates de registro pasan
    Given los cambios de US-6.4.5 aplicados
    When se ejecutan tests unitarios e integracion de registro
    Then todos los tests pasan
    And DesignReviewer no reporta DR-07 en SQLiteInscripcionRepository
