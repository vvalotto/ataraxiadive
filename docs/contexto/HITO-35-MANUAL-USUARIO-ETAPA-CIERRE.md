# HITO-35 — El manual de usuario como etapa de cierre y validación UX

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-35 — Hallazgo de ciclo de vida en SP7 |
| **Fecha** | 2026-05-30 |
| **Sprint** | SP7 — Despliegue y Documentación · INC-7.2 |
| **Relacionado** | HITO-18 · HITO-29 · BL-007 · MkDocs Material · GitHub Pages · `v1.0.2` |

---

## Contexto

INC-7.2 cierra SP7 con la producción del manual de usuario del sistema: documentación navegable de los cinco portales (Organizador, Juez, Atleta, Portal Público, Superusuario) más la sección Tu cuenta. Resultado: ~90 capturas de pantalla, build MkDocs Material estricto verde, publicación en GitHub Pages.

El manual fue planificado como un artefacto de comunicación. Lo que el proceso reveló es que cumple también una función de **validación UX estructurada** que ni el UAT ni el prototipo navegable pueden reemplazar.

---

## El manual como recorrido exhaustivo de la interfaz

Documentar un sistema implica abrir cada pantalla, verificar que el flujo descrito en el texto coincide con lo que muestra la interfaz, y capturar el estado visible. Este proceso fuerza un recorrido completo del sistema de una forma que el uso exploratorio no garantiza.

Durante INC-7.2, el recorrido sistemático para las capturas de pantalla reveló:

- Pantallas cuyo texto de ayuda o etiqueta de campo había quedado desactualizado respecto al comportamiento real
- Flujos que funcionaban pero producían estados intermedios poco claros para un usuario nuevo
- Casos donde la navegación del portal móvil (juez en competencia) asumía conocimiento previo del sistema que el manual debía compensar con contexto adicional

Cada uno de estos hallazgos fue documentado y algunos derivaron en los fixes de SP-ADJ-13.

---

## Diferencia con UAT y con el prototipo navegable

| Etapa | Propósito | Quién evalúa | Qué detecta |
|---|---|---|---|
| Prototipo navegable (HITO-18) | Validar flujos antes de implementar | Organizador · Juez | Flujos incorrectos o faltantes |
| UAT (HITO-20, HITO-28) | Verificar comportamiento funcional | Equipo del proyecto | Defectos funcionales, invariantes |
| Manual de usuario (HITO-35) | Documentar para usuarios reales | Redactor = auditor | Inconsistencias de UX, texto incorrecto, navegación asumida |

El manual no descubre defectos funcionales — los tests lo hacen. Descubre **inconsistencias entre lo que el sistema hace y lo que un usuario nuevo entendería que debería hacer** al verlo por primera vez. Este tipo de defecto no es visible desde adentro del sistema ni desde la perspectiva del desarrollador.

---

## El manual como invariante de consistencia documental

Al escribir el manual contra el sistema real (no contra la especificación), se invierte la dirección habitual de la documentación. En lugar de describir lo que el sistema *debería* hacer, se describe lo que *hace*. Cuando la descripción resulta confusa o contradictoria, el problema está en el sistema, no en el manual.

Este es el mismo principio que HITO-17 (datos reales como oráculo del dominio) aplicado a la documentación: **el manual escrito contra producción es un oráculo de consistencia UX**.

La implicación metodológica es directa: el manual de usuario no debería escribirse desde especificaciones sino desde el sistema funcionando, con capturas reales. Escribirlo antes de tener el sistema correcto (o desde especificaciones) produce documentación que diverge del producto real y pierde su función de validación.

---

## Relación con HITO-29 (anti-patrón de especificación tardía)

HITO-29 documentó el riesgo de escribir especificaciones después de implementar: el sesgo de confirmación hace que el redactor no detecte los casos que el código no cubre. El manual de usuario tiene el riesgo inverso: si se escribe antes del sistema final, no puede capturar el estado real.

La secuencia correcta para la documentación de usuario es:
1. Sistema funcionando en producción (o staging estable)
2. Recorrido sistemático de pantalla por pantalla
3. Captura del estado real
4. Texto descriptivo desde el punto de vista del usuario nuevo

Hacer esto en INC-7.2 después de INC-7.1 (despliegue) fue la secuencia correcta.

---

## El costo de diferir la documentación

El manual se dejó para el último incremento del proyecto. Esto tiene un beneficio claro (documenta el sistema final, no versiones intermedias) y un costo menos visible: si hubiera problemas estructurales de UX, estarían demasiado tarde para ser corregidos en SP7.

En AtaraxiaDive no hubo problemas estructurales — los encontrados en SP-ADJ-13 fueron de detalle. Pero la observación aplica: **diferir la documentación hasta el final es correcto para la calidad del documento; riesgoso para detectar problemas de UX a tiempo**.

El balance del experimento sugiere una cadencia híbrida: prototipo navegable temprano (HITO-18) para detectar flujos incorrectos, y manual completo al final para detectar inconsistencias de detalle.

---

## Pregunta experimental respondida

> ¿La documentación de usuario es una etapa necesaria del ciclo de vida o siempre puede diferirse?

**Evidencia:** Es necesaria, pero su momento óptimo depende del tipo de hallazgo que se busca. Para detectar flujos incorrectos: temprano (prototipo). Para detectar inconsistencias de detalle y generar documentación válida para usuarios reales: al final, sobre el sistema real.

**Implicación para IEDD:** Los incrementos de dominio técnico (despliegue, manual) son etapas del ciclo, no actividades de cierre. El manual es un artefacto verificable con su propia DoD (build verde, cobertura de portales, capturas reales) y su propio poder de detección.

---

## Resultado

- INC-7.2 cerrado: manual publicado en GitHub Pages · PR #212
- ~90 capturas de pantalla · 5 portales + Tu cuenta · build MkDocs Material strict verde
- `v1.0.2` tagueada · SP7 completamente cerrado
- Hallazgos de detalle UX derivaron en SP-ADJ-13 (HITO-36)

---

*Creado: 2026-05-30 — SP7 INC-7.2 · BL-007*
*Mantenido por: Victor Valotto + Claude Cowork*
