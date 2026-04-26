# US-5.5.1 — Notas de Implementacion

**Fecha:** 2026-04-26
**Fase:** 3 — Implementacion

---

## Enfoque

La prioridad fue alinear la experiencia del atleta con la UX aprobada sin romper
los contratos existentes del sistema. El trabajo se dividio en tres capas:

1. **Identidad visible**
   - nombre/apellido en JWT para evitar una segunda consulta obligatoria solo para render inicial.

2. **Backend minimo faltante**
   - consulta de inscripciones del atleta;
   - endpoint de `registrar-ap` consumible desde frontend;
   - ajuste semantico para permitir modificacion de AP mientras la performance siga anunciada.

3. **Shell y navegacion atleta**
   - rutas dedicadas y composicion movil dark;
   - wizard de inscripcion;
   - pantalla dedicada de AP;
   - vista de `Mis inscripciones`.

---

## Decisiones Tomadas

- Se mantuvo `AtletaDashboardPage.tsx` solo como archivo legacy para no mezclar una remocion amplia en esta regularizacion.
- Se dejo redirect de `/atleta/dashboard` hacia `/atleta` para compatibilidad con rutas previas.
- El estado visible `AP cerrado` se infiere hoy desde `torneo.estado != INSCRIPCION_ABIERTA`.
- La modificacion de AP reutiliza el mismo evento `APRegistrado`; no se agrego un evento nuevo de correccion en esta iteracion.

---

## Desvios Conscientes Respecto de la Spec

- Los adjuntos de `Certificado medico` y `Comprobante de pago` se validan en frontend, pero no se persisten en el backend.
- El `deadline` de anuncios se muestra como regla de negocio visible, no como timestamp real proveniente de API.
- `Mis resultados` queda como placeholder navegable dentro del shell, no como implementacion completa del ranking de la spec.

---

## Verificacion Ejecutada

- `npm run build` en `frontend/` — OK
- `./.venv/bin/pytest tests/unit/competencia/application/test_registrar_ap_handler.py -q` — OK
- `./.venv/bin/pytest tests/unit/identidad/application/test_handlers.py -q -k jwt_generate_y_verify_payload` — OK
