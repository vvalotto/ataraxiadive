# PLAN-SP-ADJ-13 — Ejecución en producción, capturas faltantes y ajustes

| Campo | Valor |
|-------|-------|
| **Sprint** | SP-ADJ-13 |
| **Contexto** | Ejecución completa del prototipo en producción para capturar screenshots faltantes del manual e identificar ajustes necesarios |
| **Fuentes** | Sesión de validación en https://ataraxiadive.fly.dev |
| **Incremento asociado** | INC-7.2 (manual de usuario — capturas pendientes) |
| **Branch base** | `develop` (fixes) · `feature/sp-adj-13-capturas-manual` (capturas) |
| **Estado** | ✅ Cerrado 2026-05-30 · tag `v1.0.5` |

---

## Contexto

Al cerrar INC-7.2 quedaron capturas pendientes que requieren un torneo real en ejecución en
producción. Adicionalmente, la ejecución end-to-end en producción puede revelar bugs o
inconsistencias que necesiten ajuste.

**Screenshots conocidos como faltantes:**
- `tu-cuenta/roles.md` — sección "Cómo activar o desactivar roles" (panel Mis Roles en Mis Datos)
- `portal-organizador/podios.md` — requiere torneo en estado CERRADO con podios calculados

**Screenshots potencialmente desactualizados o incompletos:**
- A relevar durante la ejecución en producción

---

## US planificadas

### US-ADJ-13.1 — Ejecución ciclo organizador en producción + capturas

**Tipo:** documentación (capturas) + fixes eventuales
**Flujo a ejecutar:**
1. Login como organizador
2. Crear torneo con disciplinas
3. Gestionar inscripciones (aceptar/rechazar atletas)
4. Asignar jueces
5. Iniciar ejecución de disciplina
6. Cierre del torneo → podios

**Capturas objetivo:**
- Panel de roles en Mis Datos (Activar/Desactivar) → `tu-cuenta/roles.md`
- Podios con resultados finales → `portal-organizador/podios.md`
- Cualquier pantalla desactualizada que se detecte

---

### US-ADJ-13.2 — Ejecución ciclo juez y atleta en producción + capturas

**Tipo:** documentación (capturas) + fixes eventuales
**Flujo a ejecutar:**
1. Login como juez → registrar performances en la disciplina creada en 13.1
2. Login como atleta → inscripción, declarar AP, consultar resultados

**Capturas objetivo:**
- Cualquier pantalla del portal juez o atleta desactualizada respecto al estado actual de producción

---

### US-ADJ-13.X — Fixes detectados durante ejecución *(TBD)*

Se agregan US adicionales a medida que se identifican bugs o inconsistencias durante la
ejecución de 13.1 y 13.2. Seguimiento en esta sección.

| US | Descripción | Estado |
|----|-------------|--------|
| — | *A completar durante la sesión de ejecución* | — |

---

## Secuencia de ejecución

```
US-ADJ-13.1  Ciclo organizador en producción + capturas
  │
  └── US-ADJ-13.2  Ciclo juez + atleta en producción + capturas
        │
        └── US-ADJ-13.X  Fixes detectados (según emerjan)
```

---

## Criterio de cierre de SP-ADJ-13

- [x] `tu-cuenta/roles.md` con screenshots reales de producción
- [x] `portal-organizador/podios.md` con screenshots reales de producción
- [x] Capturas desactualizadas detectadas en ejecución reemplazadas (público, organizador, atleta)
- [x] Fixes de producción detectados implementados y pusheados (#213–#216, PR #217, v1.0.4)
- [x] `mkdocs build --strict` verde post-integración
- [x] DesignReviewer 0 CRITICAL (los fixes de código ya pasaron el gate en v1.0.4; el manual es solo documentación)

---

## Items fuera de alcance

- Nuevas funcionalidades no detectadas en la ejecución
- Cambios de diseño o UX más allá de los bugs observados

---

*Creado: 2026-05-30 — post-cierre INC-7.2 · capturas de producción pendientes*
*Cerrado: 2026-05-30 — fixes UI #213–#216 (v1.0.4) · manual revisado contra producción (PR #218) · tag `v1.0.5` · manual publicado en GitHub Pages*
