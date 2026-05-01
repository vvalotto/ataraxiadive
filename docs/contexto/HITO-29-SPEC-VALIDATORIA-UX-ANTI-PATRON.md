# HITO-29 — Spec-validatoria: el anti-patrón de especificar desde el código existente

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-29 — Hallazgo metodológico en INC-5.5 (SP5) |
| **Fecha** | 2026-04-26 |
| **Sprint** | SP5 — La Puesta en Marcha |
| **Relacionado** | HITO-18 · `docs/design/ux/wireframes-atleta.md` · `docs/design/ux/prototipos/prototipo-atleta.html` |

---

## Contexto

En SP5, INC-5.5 fue implementado completamente (US-5.5.1 + US-5.5.2, 2 PRs mergeados) y luego revertido íntegramente porque la implementación no respetaba la UX aprobada en INC-4.0.

Las specs originales de US-5.5.1 y US-5.5.2 fueron escritas mirando el código existente:
- US-5.5.1 tomó `AtletaDashboardPage.tsx` como base y agregó una sección inline de APs
- US-5.5.2 tomó `InscriptosPanel.tsx` como base y lo optimizó (N+1 → 1 call)

Ninguno de los artefactos UX aprobados en INC-4.0 fue consultado antes de escribir las specs. Esos documentos existían en el repositorio:

- `docs/design/ux/wireframes-atleta.md` — define 8 pantallas (S-01..S-08)
- `docs/design/ux/flujos-por-rol.md` — define el flujo completo del atleta
- `docs/design/ux/prototipos/prototipo-atleta.html` — prototipo navegable validado

El código en `AtletaDashboardPage.tsx` era un MVP de integración (single-page, desktop-first, tema claro) que nunca implementó el prototipo. Al usarlo como referencia para las specs, la distancia entre diseño aprobado y código quedó invisible hasta el UAT — cuando el hallazgo `UAT-5.5-01` (portal sin nombre/apellido) disparó la revisión UX que reveló 14 gaps críticos.

---

## El anti-patrón identificado

**Spec-validatoria:** la spec se escribe mirando la implementación existente y la valida en lugar de prescribir lo que debería ser.

```
Anti-patrón (lo que ocurrió):
  Código existente (MVP sin UX) → Spec → Implementar lo mismo → "Done"

Cadena correcta (IEDD Capa 3 → Capa 5):
  UX aprobada (wireframes + prototipo) → Spec → Implementación
```

El resultado es un bucle cerrado que nunca consulta los artefactos de diseño. La spec pierde su función de contrato y se convierte en descripción del estado actual, que puede estar incorrecto. La US puede pasar todos sus criterios de aceptación y aun así violar la UX aprobada, porque los criterios fueron escritos mirando el código equivocado.

---

## Causa raíz

Tres factores concurrentes:

**1. INC-4.0 cerrado con deuda oculta.**
El incremento de UX Design fue marcado como Done cuando el prototipo navegable fue aprobado, sin verificar que la implementación React lo siguiera. La distancia entre el prototipo aprobado y el código real quedó invisible en la baseline BL-004.

**2. Sin gate de UX antes de la spec.**
El proceso de elaboración de USs (WORKFLOW §3) no exigía consultar `docs/design/ux/` antes de escribir specs de frontend. El specifier usó lo más accesible: el código existente.

**3. Framing de optimización, no de diseño.**
US-5.5.1 fue encuadrada como "exponer un handler existente y agregar una sección". Ese framing asume que la estructura actual es correcta y excluye la pregunta de si debería ser diferente. Cuando el framing ya impone la arquitectura como dada, nadie pregunta si esa arquitectura es la correcta.

---

## Relación con HITO-18

HITO-18 estableció que, para pantallas con restricciones físicas, se necesita un prototipo navegable validado **antes** de escribir la spec (problema de validación táctil).

HITO-29 identifica el problema simétrico: aunque el prototipo ya exista y esté validado, la spec puede ignorarlo si el proceso no exige consultarlo. La existencia del artefacto no garantiza su uso.

| HITO | Problema | Regla |
|------|----------|-------|
| HITO-18 | La spec existe, pero no fue precedida por un prototipo | Prototipo → Spec → Implementación (no saltear el prototipo) |
| HITO-29 | El prototipo existe, pero la spec lo ignoró | Consultar el prototipo aprobado antes de escribir cualquier spec de frontend |

Son problemas distintos con el mismo origen: la Capa 3 (Spec) desconectada de la Capa 4 (Arquitectura/UX).

---

## Aprendizaje central

> Cuando una US-IEDD toca `frontend/`, la fuente de verdad es la UX aprobada en `docs/design/ux/`, no la implementación existente. El código actual puede ser un MVP que no implementa el diseño. La spec debe derivarse de los artefactos UX, comparar con el código actual, e incorporar los gaps al scope antes de especificar comportamiento nuevo.

---

## Implicancia para IEDD como metodología

La Capa 3 (Especificación) debe derivarse de las Capas 1–4, no de la Capa 5. Para USs de frontend, esto requiere un paso explícito de consulta UX antes de escribir la spec.

Si ese paso no existe en el proceso, la cadena IEDD puede invertirse de forma invisible: el specifier mira el código más que el diseño, y la spec termina siendo un documento que justifica el estado actual en lugar de prescribir el estado correcto.

La regla práctica: la spec de una US de frontend es incorrecta si no menciona los artefactos UX de los que fue derivada. Ese campo vacío es una señal de proceso roto, no de spec completa.

---

## Acción tomada

- [x] HITO-29 registrado
- [x] WORKFLOW-DESARROLLO.md v1.8: §3 — gate de consulta UX obligatorio antes de specs de frontend; campo `Fuente de verdad UX` obligatorio
- [x] WORKFLOW-DESARROLLO.md v1.8: §6 — verificación de prototipo al cerrar INCs que produjeron artefactos UX
- [x] INC-5.5 revertido y redefinido desde la UX aprobada (specs US-5.5.1 y US-5.5.2 refactorizadas)

---

## Pregunta abierta — a conceptualizar al cierre del proyecto

El análisis de este hito abrió una pregunta sobre la posición del UX Design en IEDD:
el modelo actual trata el UX como un bloque global (INC-4.0), pero en proyectos reales
aparecen al menos tres modos de temporalización:

- **UX Discovery** — antes de cualquier backend (valida hipótesis con usuarios rápido)
- **UX Post-Backend** — después de tener el dominio consolidado (lo que hizo AtaraxiaDive)
- **UX Incremental** — por entrega, sincronizado con cada incremento de valor

La hipótesis es que el tercer modo es el más sostenible y debería formalizarse como
un mini-ciclo por incremento: UX Design del INC → aprobación → Specs US-IEDD → Implementación.

**Decisión:** diferido al cierre de SP5. El experimento producirá evidencia empírica de
los tres modos antes de terminar; mejor conceptualizar con datos que con hipótesis.

---

*Registrado al inicio de SP5 INC-5.5 reiniciado — la primera reversión completa de un INC por incompatibilidad con la UX aprobada*
