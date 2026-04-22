# Plan de Implementacion: US-ADJ-8.1 — Clarificar estados y lenguaje operativo

| Campo | Valor |
|-------|-------|
| **Sprint** | SP-ADJ-08 |
| **Tipo** | Fix UX funcional frontend |
| **Branch** | `feature/US-ADJ-8.1-estados-lenguaje` |
| **BC** | frontend organizador |
| **Estimacion** | 1-2 h |
| **Estado** | Implementada |

---

## Alcance

Corregir mensajes y jerarquia visual del panel organizador sin cambiar reglas de dominio.

Hallazgos cubiertos: `UAT-5.2-01`, `UAT-5.2-03`, `UAT-5.2-04`, `UAT-5.2-06`,
`UAT-5.2-07`.

---

## Decisiones de implementacion

- Mantener la US exclusivamente en frontend.
- No crear harness browser nuevo; BDD queda como especificacion.
- Reutilizar estilos actuales, evitando redisenar el panel completo.
- `Pasar a premiacion` ya quedo implementado en `US-ADJ-8.2`; esta US solo valida y documenta.

---

## Tareas

### 1. Estados vacios/error/loading

- [x] Ajustar estado vacio de inscriptos a `Todavia no hay inscriptos para este torneo`.
- [x] Ajustar error de jueces a `No se pudieron cargar los jueces`.
- [x] Mostrar estado vacio de jueces asignados como `Todavia no hay jueces asignados`.

### 2. Ejecucion por disciplina

- [x] Reforzar seleccion visual de item maestro y detalle.
- [x] Convertir bloqueos tecnicos en mensajes accionables con tab destino.
- [x] Mantener acciones existentes de habilitar/finalizar sin cambios de comportamiento.

### 3. Validacion

- [x] `npm run lint`.
- [x] `npm run build`.
- [x] Registrar BDD UI como omitido por falta de harness.

### 4. Documentacion

- [x] Actualizar spec a `Implementada`.
- [x] Actualizar `PLAN-SP-ADJ-08`.
- [x] Generar reporte final.

---

## Fases omitidas o acotadas

- Fases 4 y 5 sin tests unitarios/integracion nuevos: no hay harness de componentes React.
- Fase 6 sin steps automatizados: feature BDD creado como especificacion.
- Fase 7 usa `npm run lint` y `npm run build`.

---

*Creado: 2026-04-22 — Fase 2 para UAT-5.2 UX*
