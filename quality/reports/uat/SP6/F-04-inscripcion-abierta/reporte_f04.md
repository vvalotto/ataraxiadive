# Reporte Fase F-04: Inscripción Abierta

**Fecha de ejecución:** 2026-05-12  
**Ejecutor:** Victor Valotto  
**Dispositivos usados:** Desktop (organizador, portal público) · Móvil (atleta)

## Métricas

| Métrica | Valor |
|---------|-------|
| Escenarios ejecutados | 6 (S01, S02, S03, S03b, S04, S05) |
| PASS | 6 |
| FAIL | 0 |
| SKIP | 0 |
| Hallazgos 🔴 | 4 (4 resueltos) |
| Hallazgos 🟡 | 1 (1 resuelto) |
| Observaciones 🟡 sin resolver | 1 (M-04-02 — dominio Resend) |
| Mejoras visuales aplicadas | 2 (chips separados, disciplinas disponibles eliminadas) |

## Resumen

La fase validó el ciclo completo de inscripción: portal público, redirect post-login, wizard de inscripción para atletas existentes y nuevos. Se detectaron y resolvieron 4 defectos bloqueantes: edición de AP que no permitía borrar el primer dígito (bug `||` vs `??`), redirect post-login roto en React StrictMode (sessionStorage consumido dos veces), formulario de inscripción que fallaba para usuarios auto-registrados sin perfil en BC Registro, y selector de categoría ausente para usuarios nuevos. Las notificaciones email funcionan a nivel de pipeline (P10 dispara correctamente) pero Resend bloquea envíos a emails externos con el dominio de prueba — requiere dominio verificado para producción.

## Hallazgos resueltos

| ID | Severidad | Descripción | Fix |
|----|-----------|-------------|-----|
| H-04-01 | 🔴 | AP no permitía borrar primer dígito al editar | `AtletaDeclararAPPage.tsx`: `useState<string\|null>(null)` + `??` |
| H-04-02 | 🔴 | Post-login no redirigía al formulario (StrictMode) | `LoginPage.tsx`: lazy `useState` para redirect, captura una sola vez al montar |
| H-04-03 | 🔴 | Formulario fallaba para usuarios sin perfil de atleta | `AtletaInscripcionPage.tsx`: `fetchAtletaMeOrNull()` + `crearAtleta()` en mutation |
| H-04-04 | 🔴 | Sin selector de categoría para usuarios nuevos | `AtletaInscripcionPage.tsx`: selector Junior/Senior/Master compuesto con género |
| H-04-05 | 🟡 | Sin campo Club para usuarios nuevos | `AtletaInscripcionPage.tsx`: campo Club en paso 2 |

## Observaciones diferidas

| ID | Descripción | Acción sugerida |
|----|-------------|-----------------|
| M-04-02 | Notificaciones email: `onboarding@resend.dev` solo permite enviar a `vvalotto@gmail.com` · pipeline P10 funciona | Verificar dominio en resend.com/domains antes de producción |

## Criterio de Salida

- [x] F04-S01: torneo en `INSCRIPCION_ABIERTA` confirmado
- [x] Todos los escenarios 🔴 en PASS
- [x] Guadalupe Fardi inscripta en DYN con AP declarada
- [x] Verificación cruzada organizador: categoría y AP correctos
- [x] 0 hallazgos 🔴 sin resolver

## Estado: ✅ FASE CERRADA
