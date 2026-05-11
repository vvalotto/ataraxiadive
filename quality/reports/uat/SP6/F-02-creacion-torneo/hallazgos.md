# Hallazgos — Fase F-02: Creación del Torneo

## Defectos

| ID | Escenario | Descripción | Severidad | Pasos para reproducir | Estado | Fix |
|----|-----------|-------------|-----------|----------------------|--------|-----|
| H-02-01 | F02-S01 | El formulario pre-seleccionaba solo SENIOR — daba la sensación de que categorías era opcional | 🟡 | 1. Abrir "Nuevo torneo" · 2. Ver que solo SENIOR aparece activo | ✅ Resuelto | Default cambiado a las 3 categorías (JUNIOR · SENIOR · MASTER) pre-seleccionadas |
| H-02-02 | F02-S01 | El campo se llamaba "Grupos etarios" — el lenguaje ubicuo del dominio usa "Categoría" | 🟡 | 1. Abrir "Nuevo torneo" · 2. Ver etiqueta del selector | ✅ Resuelto | `<legend>` y mensaje de error renombrados a "Categorías" / "categoría" |
| H-02-03 | F02-S01 | El formulario impedía crear el torneo sin disciplinas seleccionadas — las disciplinas son opcionales al crear, se configuran después | 🟡 | 1. Abrir "Nuevo torneo" · 2. No seleccionar disciplinas · 3. El formulario bloqueaba el submit | ✅ Resuelto | Eliminada validación de disciplinas en `validate()` · submit condicional a `asignarDisciplinas` solo si `disciplinas.length > 0` |
| H-02-04 | F02-S02 | El dataset BA2025 usa `SPE` (legacy) pero la plataforma solo tiene SPE_2X50/4X50/8X50/16X50 — Seed-B fallaba con DisciplinaNoDisponible | 🔴 | Ejecutar Seed-B con torneo que tiene SPE_2X50 · el seed enviaba "SPE" | ✅ Resuelto | `DISCIPLINA_MAP = {"SPE": "SPE_2X50"}` agregado en `seed_ba2025_inscripciones.py` · el organizador selecciona SPE_2X50 en el formulario |

| H-02-05 | F02-S05 | Lista de torneos del organizador ordenada descendente (más lejano primero) — debe ser ascendente (más próximo primero) | 🟡 | 1. Crear 2+ torneos con fechas distintas · 2. Ver lista en portal organizador | ✅ Resuelto | `b.localeCompare(a)` → `a.localeCompare(b)` en `DashboardPage.tsx` |

| H-02-06 | F02-S02/S03 | La pantalla de edición dice "Editar disciplinas" y solo permite editar disciplinas — debería decir "Editar torneo" y permitir editar todos los campos incluyendo nombre, sede, fechas y categorías. Confirmado en F02-S03: si el organizador selecciona categorías incorrectas al crear, no tiene forma de corregirlas desde la UI. | 🟡 | 1. Abrir torneo · 2. Click en editar disciplinas · 3. Ver campos deshabilitados y título incorrecto · 4. No hay otra pantalla para editar categorías | Abierto — requiere US-IEDD | Nuevo endpoint `PUT /torneos/{id}` + handler `ActualizarTorneoCommand` + habilitar todos los campos en `CrearTorneoPage` modo edición |

| H-02-07 | F02-S03 | El panel del organizador no mostraba las categorías seleccionadas del torneo en "Datos generales" | 🟡 | 1. Abrir panel de torneo · 2. Ver sección "Datos generales" · 3. No aparecen JUNIOR/SENIOR/MASTER | ✅ Resuelto | Agregado bloque de categorías con chips en `DetalleTorneoPage.tsx` bajo la info de sede/entidad |

## Mejoras (fuera de scope UAT)

| ID | Origen | Descripción | Prioridad sugerida |
|----|--------|-------------|-------------------|
| — | — | — | — |
