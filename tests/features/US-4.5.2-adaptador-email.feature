Feature: Adaptador email con proveedor gestionado

  Scenario: envio exitoso via proveedor Resend
    When se envia un email via el adaptador Resend al destinatario "juan@example.com"
    Then el adaptador retorna el identificador de proveedor "provider-123"
    And el proveedor recibe el email con asunto "Inscripcion confirmada"

  Scenario: error tecnico del proveedor
    When el proveedor Resend responde con error al enviar email
    Then el adaptador email falla con error tecnico

  Scenario: configuracion incompleta del adaptador
    When se inicializa el adaptador Resend sin api key
    Then el adaptador rechaza la configuracion requerida
