Feature: Mis Datos Atleta — campos dni y telefono
  Como atleta registrado,
  quiero poder ingresar y actualizar mi DNI y teléfono en Mis Datos,
  para completar mi perfil con información de contacto real.

  # INV-11.8-01: dni y telefono son opcionales — el formulario no valida su presencia.
  # INV-11.8-02: campo vacío → undefined en el payload (no borra el dato existente).
  # INV-11.8-03: club y categoria ya opcionales — verificar envío como undefined si vacíos.

  Scenario: Atleta carga Mis Datos — ve dni y telefono guardados
    Given el atleta tiene dni="12345678" y telefono="1234567890" guardados
    When accede a /atleta/mis-datos
    Then los campos DNI y Teléfono muestran esos valores

  Scenario: Atleta actualiza su DNI
    Given el atleta está en /atleta/mis-datos
    When ingresa "98765432" en el campo DNI y guarda
    Then el PATCH a /registro/atletas/me incluye dni="98765432"
    And el formulario refleja el valor actualizado

  Scenario: Atleta deja DNI vacío — no se borra el dato existente
    Given el atleta tiene dni="12345678" guardado
    When guarda el formulario sin modificar el campo DNI
    Then el PATCH no incluye el campo dni en el payload

  Scenario: Atleta con dni null — campo queda vacío sin error
    Given el atleta no tiene dni registrado
    When accede a /atleta/mis-datos
    Then el campo DNI aparece vacío sin error
