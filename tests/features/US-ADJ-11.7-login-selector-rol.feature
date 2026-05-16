Feature: Login con selector de rol
  Como usuario con múltiples roles (Atleta, Juez, Organizador),
  quiero poder elegir con qué rol quiero ingresar al iniciar sesión,
  para que la plataforma me muestre el portal correcto desde el primer momento.

  # INV-11.7-01: El selector solo se muestra si el usuario tiene 2 o más roles.
  # INV-11.7-02: El rol ADMIN nunca aparece en el selector visible al usuario.
  # INV-11.7-03: Después de seleccionar un rol, el store refleja ese rol como activo.
  # INV-11.7-04: Si el backend retorna requires_role_selection sin roles, se trata como error.

  Scenario: Login de usuario con un solo rol — sin cambios
    Given el usuario tiene únicamente el rol ATLETA
    When hace login con credenciales correctas
    Then el backend retorna access_token directamente
    And el frontend redirige a /atleta sin mostrar selector

  Scenario: Login de usuario multi-rol — backend retorna requires_role_selection
    Given el usuario tiene roles ATLETA y JUEZ
    When hace login con credenciales correctas
    Then el backend retorna requires_role_selection=true con roles ["ATLETA", "JUEZ"]
    And la LoginPage muestra el selector de rol inline
    When el usuario selecciona JUEZ
    Then el frontend llama a /auth/login con rol_elegido=JUEZ
    And redirige a /juez/disciplinas

  Scenario: Aviso informativo post-registro multi-rol
    Given el usuario fue redirigido desde /registro con state requiresRoleSelection=true
    When la LoginPage carga
    Then muestra el aviso "Tu cuenta tiene varios roles"
    And el formulario de login se muestra normalmente

  Scenario: Selector no aparece para usuario de un solo rol
    Given el usuario tiene únicamente el rol ORGANIZADOR
    When hace login exitoso
    Then redirige directamente a /organizador/torneo sin mostrar selector

  Scenario: requires_role_selection sin roles es error
    Given el backend retorna requires_role_selection=true con lista de roles vacía
    When la LoginPage recibe esa respuesta
    Then muestra un mensaje de error al usuario
    And no muestra el selector de rol
