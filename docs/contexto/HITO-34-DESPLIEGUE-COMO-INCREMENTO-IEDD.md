# HITO-34 — El despliegue como incremento IEDD de dominio técnico

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-34 — Hallazgo de ciclo de vida en SP7 |
| **Fecha** | 2026-05-17 |
| **Sprint** | SP7 — Despliegue y Documentación · INC-7.1 |
| **Relacionado** | HITO-13 · HITO-3 · BL-007 · Fly.io · `v1.0.1` |

---

## Contexto

SP7 abre con INC-7.1: despliegue del sistema a producción en Fly.io. Es el primer incremento del proyecto que no tiene lógica de dominio ni features de negocio. Su contenido es puramente técnico: configuración de infraestructura, CI/CD, dominio personalizado y variables de entorno.

La pregunta metodológica que plantea es si IEDD tiene algo para decir sobre un incremento de este tipo, o si el marco simplemente no aplica y el trabajo se hace fuera del ciclo normal.

---

## El incremento técnico como caso límite de IEDD

INC-7.1 fue tratado como un incremento IEDD con su propio DoD observable:

- **Precondición:** `v1.0.0` tagueada en `main`, tests verdes, sistema funcionando en local
- **Postcondición:** `fly deploy` devuelve exit 0, `health-check` responde 200 en `ataraxiadive.fly.dev`
- **Invariante:** sin degradación de tests ni cambios en el dominio
- **DoD:** URL de producción accesible y funcional

El ejercicio demostró que **la estructura IEDD puede sostenerse para incrementos de infraestructura** con una adaptación: el "aggregate afectado" es la arquitectura de despliegue, y el "comportamiento del sistema" es la disponibilidad en producción. Los invariantes son de calidad (no regresión) en lugar de reglas de negocio.

---

## Diferencias con incrementos de dominio

| Aspecto | Incremento de dominio | Incremento de infraestructura |
|---|---|---|
| Precondición | Estado del modelo de negocio | Estado del entorno y configuración |
| Postcondición | Comportamiento observable del dominio | Servicio accesible en producción |
| Invariante | Regla de negocio que no puede violarse | Tests no regresionan · servicio disponible |
| Quality gate | DesignReviewer · CodeGuard | Health-check · CI verde |
| Evidencia | Tests BDD + unit + integración | `fly status` · URL de producción |

La diferencia es real pero no invalida la estructura. El incremento de infraestructura es especificable, tiene DoD verificable y produce evidencia observable. Lo que cambia es el dominio del problema: en lugar de modelar performances o torneos, se modela el entorno de ejecución.

---

## Lo que produjo el incremento

INC-7.1 no solo desplegó: reveló dependencias implícitas que no eran visibles en desarrollo local:

- Configuración de `PYTHONPATH` en el contexto de Fly.io diferente al local
- Variables de entorno necesarias pero no documentadas formalmente (se descubrieron al fallar el primer deploy)
- El comportamiento de SQLite en un sistema de archivos efímero (Fly.io mounts) vs local
- La necesidad de `volumes` persistentes para los archivos `.db` por BC

Cada una de estas fue una postcondición implícita que el sistema local no podía verificar. Esto refuerza un hallazgo del experimento: **el entorno de producción es un oráculo distinto al entorno de desarrollo**, no solo una versión "final" de lo mismo.

---

## Relación con HITO-13 (SP-ADJ como etapa formal)

HITO-13 documentó que la deuda técnica post-SP merece un sub-sprint formal. INC-7.1 es análogo pero para infraestructura: el despliegue no es una tarea de cierre — es un incremento con su propio contenido y su propia zona de falla.

Tratar el despliegue como "lo que se hace al terminar" (tarea implícita de cierre) habría producido un incremento sin DoD, sin evidencia verificable y sin trazabilidad de los problemas encontrados. Tratarlo como INC-7.1 con su propio ciclo IEDD produjo documentación de las decisiones técnicas (AA-05, AA-06 en BL-007) y evidencia del estado del sistema post-despliegue.

---

## Pregunta experimental respondida

> ¿El despliegue a producción puede tratarse como un incremento IEDD con su propia especificación y DoD?

**Evidencia:** Sí, con la adaptación de que el "dominio" es la infraestructura de ejecución. La estructura (precondición → implementación → DoD observable) se mantiene. Los quality gates cambian de forma pero no de función.

**Implicación para IEDD:** El marco debería reconocer explícitamente los **incrementos de dominio técnico** (infraestructura, despliegue, documentación) como ciudadanos de primera clase del ciclo, con su propio template de US y DoD adaptado.

---

## Resultado

- INC-7.1 cerrado con DoD verificado: `ataraxiadive.fly.dev` respondiendo 200
- `v1.0.1` tagueada (primer tag de producción)
- Decisiones de configuración documentadas en BL-007 (AA-05, AA-06, AA-07)

---

*Creado: 2026-05-17 — SP7 INC-7.1 · BL-007*
*Mantenido por: Victor Valotto + Claude Cowork*
