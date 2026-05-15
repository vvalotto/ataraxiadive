Feature: Edicion de perfil del atleta

  Scenario: El atleta actualiza su nombre y club
    Given el atleta esta autenticado y tiene perfil en registro con nombre "Ana" y club "Poseidon"
    When llama a PATCH /registro/atletas/me con nombre "Juan" y club "Club Atletico"
    Then la respuesta es 200 OK
    And el perfil del atleta tiene nombre "Juan" y club "Club Atletico"

  Scenario: El atleta corrige su categoria
    Given el atleta esta autenticado y tiene perfil en registro con categoria SENIOR_MASCULINO
    When llama a PATCH /registro/atletas/me con categoria MASTER_MASCULINO
    Then la respuesta es 200 OK
    And el perfil del atleta tiene categoria MASTER_MASCULINO

  Scenario: La actualizacion parcial no borra campos no provistos
    Given el atleta esta autenticado y tiene perfil con nombre "Maria" apellido "Gonzalez" categoria SENIOR_FEMENINO y club "Poseidon"
    When llama a PATCH /registro/atletas/me con solo club "Neptuno"
    Then el nombre sigue siendo "Maria"
    And el apellido sigue siendo "Gonzalez"
    And la categoria sigue siendo SENIOR_FEMENINO
    And el club queda como "Neptuno"

  Scenario: Atleta sin perfil recibe 404
    Given el usuario autenticado no tiene perfil de atleta en registro
    When llama a PATCH /registro/atletas/me con nombre "Juan"
    Then la respuesta es 404
