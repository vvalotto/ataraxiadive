# Specs — SP6 Validación, Ajustes y Despliegue

> Especificaciones de User Stories para SP6 — v1.0.0

---

## Incremento 6.1 — Ajustes Juez

Foco: **corregir el flujo de competencia** — BUG crítico MUX-04 primero, luego mejoras UX del flujo.

### Stories

| US | Título | Hallazgos | Estado |
|----|--------|-----------|--------|
| [US-6.1.1](./US-6.1.1.md) | Fix BUG canSubmitBko + Corrección Secuencia Tarjeta→Marca | MUX-04 · UI-JUE-02 | Pending |
| [US-6.1.2](./US-6.1.2.md) | Colores Tarjeta + Pantalla Completada Según Resultado | MUX-02 · MUX-05 | Pending |
| [US-6.1.3](./US-6.1.3.md) | Grilla Ordenada por Estado + Keypad Visible en Móvil | MUX-03 · MUX-01 | Pending |
| [US-6.1.4](./US-6.1.4.md) | Rediseño Inicio Juez + STA mm:ss + Tarjeta Amarilla Simplificada | UI-JUE-01 · MUX-08 · MUX-07 | Pending |
| [US-6.1.5](./US-6.1.5.md) | AtletaCard Compacta en Paso 5 | MUX-06 | Pending |

---

## Incremento 6.2 — Ajustes Organizador

Foco: **corregir UX del portal organizador** — torneos ordenados, columnas renombradas, nueva página de Podios.

### Stories

| US | Título | Hallazgos | Estado |
|----|--------|-----------|--------|
| [US-6.2.1](./US-6.2.1.md) | Inicio: Ordenar Torneos por Fecha + Mostrar Fecha | UI-ORG-01 | Pending |
| [US-6.2.2](./US-6.2.2.md) | Inscriptos + Grilla: Categoría Legible + AP → Anuncios | UI-ORG-03 · UI-ORG-04 | Pending |
| [US-6.2.3](./US-6.2.3.md) | Resultados: Quitar PTS FAAS + Andarivel Numérico + AP → Anuncio | UI-ORG-05 | Pending |
| [US-6.2.4](./US-6.2.4.md) | Panel Torneo: Alertas sin "Resolver" + Jueces sin Texto Nombre | UI-ORG-02 · UI-ORG-06 | Done |
| [US-6.2.5](./US-6.2.5.md) | Nuevo Torneo: Selección Categorías JUNIOR/SENIOR/MASTER | UI-ORG-07 | Done |
| [US-6.2.6](./US-6.2.6.md) | Crear Página de Podios | UI-ORG-08 | Done |

### Criterios de Cierre INC-6.2

- [ ] US-6.2.1..6.2.6 especificadas (IEDD completa)
- [ ] DesignReviewer 0 CRITICAL al merge de cada US
- [ ] US-6.2.5 requiere migración SQLite — verificar compatibilidad con datos existentes
- [ ] UAT organizador E2E: inicio, inscriptos, grilla, resultados, podios, nuevo torneo

---

## Incremento 6.3 — Ajustes Atleta

Foco: **corregir el portal atleta y completar inscripción** — inicio más claro,
AP inline en el wizard y persistencia de adjuntos obligatorios.

### Stories

| US | Título | Hallazgos | Estado |
|----|--------|-----------|--------|
| [US-6.3.1](./US-6.3.1.md) | Inicio atleta: en línea en header + sin "Hola" + torneos en curso ordenados | UI-ATL-01 | Done |
| [US-6.3.2](./US-6.3.2.md) | Formulario inscripción: AP inline en wizard + persistir apto médico + constancia de pago | UI-ATL-02 · RF-IN-05 · RF-IN-06 | Implementada |

### Criterios de Cierre INC-6.3

- [x] US-6.3.1..6.3.2 especificadas (IEDD completa)
- [ ] PRs de US-6.3.1..6.3.2 mergeados a `develop`
- [ ] UAT atleta E2E: inicio, torneos, inscripción, mis inscripciones, grilla, resultados

---

## Dependencias y Bloqueantes

- **US-6.1.1** debe completarse **antes de cualquier UAT** del rol juez
  - MUX-04 (BUG crítico) bloquea el flujo
  - UI-JUE-02 (secuencia correcta) es precondición para testing
- **US-6.1.2, 6.1.3, 6.1.4, 6.1.5** pueden ejecutarse en paralelo post-6.1.1

---

## Criterios de Cierre INC-6.1

- [x] US-6.1.1..6.1.5 especificadas (IEDD completa)
- [ ] DesignReviewer 0 CRITICAL al merge de cada US
- [ ] MUX-04 corregido y verificado en móvil + desktop
- [ ] UAT rol juez E2E completada (scenarios T-01, T-02, T-03, T-04)

---

## Referencias

- **Plan**: `docs/plans/sp6/PLAN-SP6.md`
- **Hallazgos UX**: `docs/design/ux/mejoras-ux.md`
- **Fuente de hallazgos SP5**: `.work/AtaraxiaDive - Hallazgos - Validacion.md`

---

*Creado: 2026-05-03*
