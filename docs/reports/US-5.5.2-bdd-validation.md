# US-5.5.2 - Validacion BDD

**Fecha:** 2026-04-26
**Artefacto BDD:** `tests/features/US-5.5.2-organizador-inscriptos-ap.feature`

---

## Cobertura contra criterios de aceptacion

- `organizador ve inscriptos con datos completos`
  - cubierto por endpoint enriquecido y tabla visible con apellido, nombre, categoria y club.

- `organizador distingue AP pendiente y AP declarado`
  - cubierto por `EstadoAPBadge` y por la composicion backend de AP por disciplina.

- `cierre del periodo cambia el estado visible a AP cerrado`
  - cubierto en frontend derivando el estado visible desde `torneo.estado`.

- `inscripciones canceladas no aparecen como operativas`
  - cubierto por `find_active_by_torneo`.

- `acceso con rol atleta es rechazado`
  - cubierto por `OrganizadorDep` y test de integracion 403.

---

## Evidencia ejecutada

- `tests/integration/registro/test_inscriptos_detalle_endpoint.py`
  - verifica inscripciones activas, AP por disciplina y rechazo por rol.

---

## Waiver

- No hay automatizacion browser end-to-end para validar la UX completa del panel organizador.
- La validacion BDD UI queda documentada por feature file + test de integracion API + build frontend.
