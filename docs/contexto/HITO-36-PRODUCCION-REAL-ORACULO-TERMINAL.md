# HITO-36 — Producción real como oráculo terminal — Puerto Madryn 2026

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-36 — Hallazgo de validación en SP-ADJ-13 |
| **Fecha** | 2026-05-30 |
| **Sprint** | SP-ADJ-13 — Correcciones post-producción (Puerto Madryn 2026) |
| **Relacionado** | HITO-9 · HITO-17 · HITO-20 · HITO-28 · BL-007 · `v1.0.4` · `v1.0.5` |

---

## Contexto

SP-ADJ-13 documenta el primer uso del sistema en una competencia real: el torneo de apnea realizado en Puerto Madryn 2026. AtaraxiaDive se usó como sistema oficial de gestión: registro de atletas, administración de la grilla, ejecución de la competencia por parte de los jueces, y publicación de resultados.

El resultado fue una ejecución completa en producción. También fue la validación más exigente del experimento: ningún dataset sintético, ningún UAT controlado, usuarios reales bajo presión de tiempo en una competencia oficial.

---

## Lo que encontró la producción real

El sistema funcionó. Los flujos principales del dominio — registro, grilla, ejecución, tarjetas, resultados — se completaron sin defectos funcionales. Todos los invariantes de dominio validados en UAT se mantuvieron.

Sin embargo, la producción real reveló cuatro categorías de problemas que el UAT con dataset sintético no detectó:

**1. Navegación móvil incompleta (PR #217, v1.0.4)**
El portal del juez se usa desde el celular durante la competencia. La navegación entre vistas asumía un patrón de interacción de escritorio (menú lateral siempre visible) que en móvil requiere un flujo explícito de apertura/cierre. Los jueces en Puerto Madryn no pudieron navegar fluidamente entre disciplinas asignadas. Fix: nav móvil rediseñada con comportamiento contextual.

**2. Inconsistencias de texto y etiquetas en contexto real (#213–#216)**
Campos y etiquetas que en UAT eran comprensibles resultaron ambiguos para usuarios que no participaron del desarrollo. El contexto de una competencia real — presión de tiempo, terminología específica del deporte, múltiples roles operando simultáneamente — hizo visible ambigüedad que el equipo de desarrollo había normalizado.

**3. Manual desalineado con el flujo real (PR #218, v1.0.5)**
INC-7.2 produjo el manual sobre el sistema en staging. Puerto Madryn expuso diferencias menores entre el sistema documentado y el sistema en producción bajo carga real. El manual fue revisado y republicado contra el flujo real.

**4. Ausencia de defectos funcionales**
Ninguno de los cuatro problemas anteriores afectó la operación del torneo. Los resultados fueron correctos, la trazabilidad intacta, el event store coherente. Los defectos encontrados son de usabilidad e interacción, no de dominio.

---

## Por qué el UAT no los detectó

El UAT de SP6 validó 10/10 flujos funcionales con el dataset de Buenos Aires 2025. HITO-28 documentó que el testing exploratorio complementa el pipeline formal. Puerto Madryn agrega un nivel más:

| Modalidad | Detecta | No detecta |
|---|---|---|
| Tests formales (unit, integración, BDD) | Invariantes, contratos, regresiones | UX, interacción, flujo bajo presión |
| UAT con dataset sintético (HITO-9, HITO-20) | Flujos completos, edge cases de dominio | Ambigüedad de texto, navegación móvil real |
| UAT exploratorio / vibe coding (HITO-28) | Inconsistencias no especificadas | Problemas que solo emergen bajo presión real |
| **Producción real (HITO-36)** | **Todo lo anterior + presión real + usuarios nuevos** | Nada (es el oráculo completo) |

La diferencia no es de cobertura funcional sino de **contexto de uso**. Un usuario real en una competencia interactúa con el sistema con urgencia, sin conocer su historia, y con expectativas formadas por otros sistemas similares. Ese perfil de uso no puede simularse en UAT.

---

## La validación en capas del experimento

AtaraxiaDive completó el ciclo de validación más completo posible para un proyecto de esta escala:

```
Datos reales (HITO-17) → revelan inconsistencias de dominio
      ↓
UAT formal con dataset real (HITO-20) → valida flujos y variantes
      ↓
UAT exploratorio (HITO-28) → complementa con perspectiva no especificada
      ↓
Manual de usuario (HITO-35) → audita consistencia UX desde afuera
      ↓
Producción real (HITO-36) → valida presión real, usuarios nuevos, navegación móvil
```

Cada capa detecta una categoría de problema que la anterior no puede ver. Ninguna es redundante.

---

## La importancia del sistema en el contexto del experimento

Puerto Madryn 2026 cierra el Horizonte 3 del PLAN-EXPERIMENTO.md: "AtaraxiaDive se usa en un torneo real". Ese criterio de éxito fue planteado al inicio del experimento como el validador último del sistema. Se cumplió.

La observación experimental más relevante no es que el sistema funcionó — eso era necesario pero no suficiente. La observación relevante es que **los defectos encontrados en producción fueron todos de usabilidad, no de dominio**. Los invariantes de dominio especificados con IEDD, validados con BDD y verificados en UAT, se mantuvieron bajo presión real. El método hizo lo que prometía: especificar el comportamiento del dominio con precisión suficiente para que la implementación generada por IA fuera correcta en producción.

Los defectos de usabilidad (nav móvil, texto ambiguo) son defectos de especificación de interfaz, no de dominio. Sugieren que IEDD es sólido para el dominio pero que la especificación de comportamiento de interfaz móvil requiere su propia extensión metodológica — una pregunta abierta para trabajos futuros.

---

## Pregunta experimental respondida

> ¿El uso en una competencia real detecta clases de defectos que el UAT con dataset simulado no puede anticipar?

**Evidencia:** Sí, y los defectos son estructuralmente distintos: usabilidad bajo presión, navegación móvil, ambigüedad de texto en contexto real. Los defectos de dominio no aparecieron — la metodología los había contenido.

**Implicación para IEDD:** La cadena de validación completa (tests formales → UAT formal → UAT exploratorio → producción real) es la única forma de certificar un sistema. IEDD protege el dominio; la producción real protege la interfaz. Ambas capas son necesarias.

---

## Resultado

- Sistema operó completo en Puerto Madryn 2026 sin defectos de dominio
- 4 fixes de UI: PR #217 (nav móvil) + issues #213–#216 → `v1.0.4`
- Manual revisado contra producción: PR #218 → `v1.0.5`
- SP-ADJ-13 cerrado sin nueva baseline (ajuste documental sobre BL-007)
- Manual publicado en GitHub Pages en estado final

---

*Creado: 2026-05-30 — SP-ADJ-13 · Puerto Madryn 2026 · BL-007*
*Mantenido por: Victor Valotto + Claude Cowork*
