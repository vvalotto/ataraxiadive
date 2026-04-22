# Plan de Implementacion: US-ADJ-8.3 — Fortalecer cancelacion de torneo

| Campo | Valor |
|-------|-------|
| **Sprint** | SP-ADJ-08 |
| **Tipo** | Hardening UX frontend |
| **Branch** | `feature/US-ADJ-8.3-cancelacion-fuerte` |
| **BC** | frontend organizador |
| **Estimacion** | 1 h |
| **Estado** | Implementada |

---

## Alcance

Separar `Cancelar torneo` de las acciones normales y exigir confirmacion fuerte
escribiendo exactamente el nombre del torneo.

## Tareas

- [x] Separar zona de peligro en `AccionesPanel`.
- [x] Agregar input de confirmacion exacta por nombre.
- [x] Mantener boton final deshabilitado hasta coincidencia exacta.
- [x] Validar con `npm run lint` y `npm run build`.
- [x] Actualizar documentacion y reporte.

## Fases acotadas

- Sin tests automatizados UI por falta de harness React.
- BDD creado como especificacion.

---

*Creado: 2026-04-22 — Fase 2 para UAT-5.2 accion destructiva*
