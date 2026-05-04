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
