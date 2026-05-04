# Revisión UX — Portal del Atleta
## Gaps entre especificación (INC-4.0) e implementación actual

**Fecha:** 2026-04-25
**Artefactos de referencia:**
- `docs/design/ux/wireframes-atleta.md` — especificación formal S-00..S-08
- `docs/design/ux/prototipos/prototipo-atleta.html` — prototipo validado INC-4.0
- `frontend/src/pages/atleta/AtletaDashboardPage.tsx` — implementación actual

---

## Resumen ejecutivo

El portal del atleta fue implementado como una **única página de dashboard** (desktop-first,
tema claro) mientras que la especificación UX define **8 pantallas** (S-00..S-08) con
navegación por rutas, shell móvil dark (max 430 px) y tab bar inferior persistente.

El flujo de inscripción (S-04) es el gap más crítico: la spec define un wizard de 3 pasos
con verificación de datos personales y adjunto de requisitos; la implementación actual es
un panel inline con selección de disciplinas solamente.

---

## Hallazgos detallados

| ID | Área | Gap | Severidad | INV violado |
|----|------|-----|-----------|-------------|
| UX-ATL-01 | Shell / Layout | Tema claro (light) vs. dark (`#0f172a`) especificado | Alta | — |
| UX-ATL-02 | Shell / Layout | No hay bottom tab bar de 4 tabs (Inicio · Torneos · Mis inscr. · Resultados) | Alta | — |
| UX-ATL-03 | Shell / Layout | Single-page vs. navegación por rutas entre S-01..S-08 | Alta | — |
| UX-ATL-04 | S-01 Dashboard | No hay `hero-card` con nombre, categoría y club del atleta | Media | — |
| UX-ATL-05 | S-01 Dashboard | No hay card "Tu próximo OT" con hora, andarivel y AP | Media | — |
| UX-ATL-06 | S-02 Torneos | No existe pantalla de discovery separada (S-02) | Media | — |
| UX-ATL-07 | S-03 Detalle | No existe pantalla de detalle del torneo antes del CTA de inscripción | Media | — |
| **UX-ATL-08** | **S-04 Inscripción** | **Wizard de 3 pasos no implementado: Personales → Competencia → Requisitos** | **Crítica** | INV-ATL-02 · INV-ATL-07 · INV-ATL-08 |
| UX-ATL-09 | S-04 Paso 1 | No se verifica ni completa nombre, apellido, fecha de nacimiento, género, documento, teléfono | Alta | INV-ATL-07 |
| UX-ATL-10 | S-04 Paso 3 | No hay adjunto de certificado médico ni comprobante de pago | Alta | INV-ATL-08 |
| UX-ATL-11 | S-05 Mis inscr. | No existe pantalla dedicada "Mis inscripciones" con estado por torneo/disciplina | Media | — |
| UX-ATL-12 | S-06 Declarar AP | AP se declara inline junto al torneo; spec define pantalla dedicada con deadline banner | Media | INV-ATL-01 |
| UX-ATL-13 | S-07 Mi grilla | No existe pantalla "Mi grilla" con OT hero, posición y grilla completa | Media | INV-ATL-03 · INV-ATL-04 |
| UX-ATL-14 | S-08 Resultados | No existe pantalla de resultados del atleta por disciplina + ranking | Media | INV-ATL-05 · INV-ATL-06 |

---

## Detalle del gap crítico — UX-ATL-08: Wizard de inscripción

**Especificación (S-04):**

```
Paso 1 — Datos Personales
  - Email (readonly)
  - Nombre y Apellido *
  - Fecha de nacimiento *
  - Género * (radio)
  - Documento (tipo + número) *
  - Teléfono *
  - [Siguiente →]

Paso 2 — Datos de la Competencia
  - Selector múltiple de disciplinas (DisciplinaToggleCard)
  - Categoría calculada / revisable
  - Nº Brevet FAAS (opcional)
  - [← Anterior] [Siguiente →]

Paso 3 — Requisitos
  - UploadArea: Certificado médico *
  - UploadArea: Comprobante de pago *
  - [← Anterior] [Enviar inscripción] [Cancelar]
```

**Implementación actual (InscripcionPanel):**

```
[Inscribirme] → expande panel inline
  - Checkboxes de disciplinas disponibles
  - [Confirmar inscripcion]
```

**Invariantes violados:**
- `INV-ATL-02`: "Una inscripción enviada con requisitos pendientes queda en estado de
  verificación" — no se capturan requisitos
- `INV-ATL-07`: "La categoría competitiva se deriva de la fecha de nacimiento y debe poder
  revisarse antes del envío" — no hay paso de revisión de categoría
- `INV-ATL-08`: "Certificado médico y comprobante de pago son obligatorios para completar
  la inscripción" — no hay upload de ningún tipo

---

## Análisis de causa raíz

El portal del atleta fue implementado como MVP funcional durante SP4 para verificar
la integración end-to-end del BC Registro (inscripcion + AP). La especificación UX de
INC-4.0 fue validada como prototipo HTML pero no fue implementada en React.

Las pantallas S-03, S-04 (wizard completo), S-05, S-06, S-07 y S-08 no tienen
componente React correspondiente. El tab bar y el dark shell tampoco están implementados.

---

## Clasificación

**Track formal requerido** — la corrección de UX-ATL-08 (wizard S-04) y del dark shell
tocan múltiples archivos de `frontend/src/` y requieren US-IEDD.

**Propuesta de agrupamiento:**
- `UX-ATL-01..03` (shell dark + tab bar + rutas) → 1 US (fundación de shell móvil)
- `UX-ATL-04..07` (S-01 hero, S-02 discovery, S-03 detalle) → 1 US por pantalla o agrupado
- `UX-ATL-08..10` (wizard S-04 completo) → 1 US crítica (bloquea INV-ATL-08)
- `UX-ATL-11..14` (S-05..S-08) → 1 US por pantalla

El gap más urgente para cumplir reglamentariamente es **UX-ATL-08** (requisitos de
inscripción obligatorios) + **UX-ATL-09** (datos personales del atleta, que además
resuelve UAT-5.5-01: nombre/apellido en portal).

---

*Artefacto de revisión SP5 — 2026-04-25*
