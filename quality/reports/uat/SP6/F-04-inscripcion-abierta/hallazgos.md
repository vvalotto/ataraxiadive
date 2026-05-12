# Hallazgos — Fase F-04: Inscripción Abierta

## Defectos

| ID | Escenario | Descripción | Severidad | Pasos para reproducir | Estado | Fix |
|----|-----------|-------------|-----------|----------------------|--------|-----|
| H-04-01 | F04-S04 | Campo AP editable no permitía borrar el primer dígito al editar (useState `''` con `\|\|` en lugar de `null` con `??`) | 🔴 | 1. Ir a "Editar AP" en Mis Inscripciones 2. Intentar borrar primer dígito | Resuelto | `AtletaDeclararAPPage.tsx`: `useState<string\|null>(null)` + `??` |
| H-04-02 | F04-S03 | Post-login no redirigía al formulario de inscripción (React StrictMode consumía sessionStorage dos veces en el render) | 🔴 | 1. Click "Inscribirse" sin login 2. Hacer login 3. Llega a portal atleta en vez del formulario | Resuelto | `LoginPage.tsx`: lazy `useState` para capturar redirect una sola vez al montar |
| H-04-03 | F04-S03b | Formulario de inscripción fallaba para usuarios auto-registrados sin perfil de atleta en BC Registro | 🔴 | 1. Registrar nuevo usuario via `/registro` 2. Intentar inscribirse en un torneo | Resuelto | `AtletaInscripcionPage.tsx`: `fetchAtletaMeOrNull()` + `crearAtleta()` en mutation si perfil no existe |
| H-04-04 | F04-S03b | Formulario de inscripción sin selector de categoría para usuarios nuevos (campo read-only con valor vacío) | 🔴 | 1. Nuevo usuario sin perfil 2. Paso 2 del wizard — categoría vacía sin opción de selección | Resuelto | `AtletaInscripcionPage.tsx`: selector Junior/Senior/Master cuando `categoriaValue` es vacío; género del paso 1 compone el código completo |
| H-04-05 | F04-S03b | Formulario de inscripción sin campo Club para usuarios nuevos | 🟡 | 1. Nuevo usuario — paso 2 del wizard sin campo club | Resuelto | `AtletaInscripcionPage.tsx`: campo Club agregado en paso 2 |

## Mejoras (fuera de scope UAT)

| ID | Origen | Descripción | Prioridad sugerida |
|----|--------|-------------|-------------------|
| M-04-01 | F04-S02 | Chips de disciplinas y categorías en portal público sin separación visual por tipo | Baja |
| M-04-02 | F04-S03b | Notificaciones email fallan para destinatarios externos — `onboarding@resend.dev` solo permite enviar a `vvalotto@gmail.com` · pipeline P10 funciona correctamente · requiere dominio verificado en Resend para producción | Alta |
