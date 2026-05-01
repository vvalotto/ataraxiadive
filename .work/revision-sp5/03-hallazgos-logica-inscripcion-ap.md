# Revisión Funcional — Flujo de Inscripción y AP
## Hallazgos de lógica de negocio en circuito organizador

**Fecha:** 2026-04-29
**Contexto:** validación funcional del circuito del organizador en branch `validation/organizador-circuit`
**Alcance:** consistencia entre inscripción, declaración de AP, cierre de inscripción y preparación de competencia

---

## Resumen ejecutivo

Se detectó un gap crítico de modelo entre la lógica de negocio esperada y la
implementación actual del sistema.

El flujo operativo esperado exige que el AP esté informado antes de cerrar la
inscripción y antes de generar la grilla. Sin embargo, la implementación actual
ubica el AP dentro del BC `competencia`, como parte de los eventos de
`performance`. Esto deja invertida la secuencia del negocio:

- para preparar la competencia se necesita AP;
- pero para disponer de AP hoy se necesita una competencia ya creada;
- y el cierre de inscripción no valida la presencia de AP.

El resultado es una inconsistencia transversal entre `registro`, `torneo`,
`competencia` y la UX del organizador.

---

## Hallazgos abiertos

| ID | Área | Hallazgo | Severidad | Estado |
|----|------|----------|-----------|--------|
| UAT-INS-AP-01 | Dominio · Registro · Competencia | El sistema modela el AP después del cierre de inscripción, aunque debería ser precondición para preparación y generación de grilla | Crítica | Abierto |

---

## Detalle de hallazgos

### UAT-INS-AP-01 — El AP está modelado demasiado tarde en el flujo

**Descripción:**
Durante la validación del circuito del organizador se verificó que el torneo
puede avanzar desde `INSCRIPCION_ABIERTA` hacia `PREPARACION` sin validar que
los atletas hayan declarado AP, pero luego la generación de grilla sí depende
de performances con AP ya registrados.

Esto produce una contradicción de negocio: el sistema permite cerrar la
inscripción sin AP, pero exige AP para la fase siguiente.

**Regla de negocio esperada:**

```text
INSCRIPCION_ABIERTA
-> atleta inscripto por disciplina
-> AP declarado
-> cierre de inscripción
-> PREPARACION
-> generación de grilla
```

**Implementación actual observada:**

```text
INSCRIPCION_ABIERTA
-> cierre de inscripción
-> PREPARACION
-> creación/configuración de competencia
-> registro de AP en performance
-> generación de grilla
```

**Evidencia local:**

- `CerrarInscripcionHandler` no valida AP antes de permitir la transición:
  [transicionar_torneo.py](/Users/victor/PycharmProjects/ataraxiadive/src/torneo/application/commands/transicionar_torneo.py)
- `GenerarGrillaHandler` sí exige performances con AP:
  [generar_grilla.py](/Users/victor/PycharmProjects/ataraxiadive/src/competencia/application/commands/generar_grilla.py)
- La pantalla `Inscriptos` obtiene AP desde `_load_ap_por_torneo()`, que lee
  eventos de `Performance` en `competencia.db`:
  [router.py](/Users/victor/PycharmProjects/ataraxiadive/src/registro/api/router.py)

**Causa raíz:**
El AP fue modelado como dato operativo de `competencia` en lugar de modelarse
como parte del flujo de `registro` por disciplina.

Esto puede servir para el circuito técnico de performance, pero no respeta la
secuencia operativa real del torneo, donde el AP debe quedar declarado antes de
cerrar la inscripción y antes de preparar la grilla.

**Impacto:**

- la fase `INSCRIPCION_ABIERTA` no puede cumplir su objetivo completo;
- el organizador no tiene forma consistente de completar la preparación del
  torneo;
- `Inscriptos` no puede reflejar correctamente el estado del AP durante la
  inscripción;
- la generación de grilla depende de datos que deberían existir antes de crear
  la competencia operativa.

**Comportamiento esperado:**

- el AP debe declararse por atleta y disciplina durante la inscripción;
- no se debe permitir `INSCRIPCION_ABIERTA -> PREPARACION` si faltan AP
  obligatorios;
- la preparación/generación de grilla debe consumir AP ya declarados en el
  contexto de inscripción;
- la pantalla `Inscriptos` debe mostrar y administrar AP sin requerir una
  competencia previamente creada.

**Acción propuesta:**

- persistir AP en `registro` por `(atleta, torneo, disciplina)`;
- hacer que `Inscriptos` lea y muestre AP desde `registro`;
- bloquear la transición `INSCRIPCION_ABIERTA -> PREPARACION` si existe alguna
  inscripción activa sin AP requerido;
- cambiar la preparación/generación de grilla para consumir AP desde `registro`
  en lugar de depender de `performance` preexistentes;
- revisar si el evento de AP en `competencia` debe mantenerse como réplica
  operativa o eliminarse como fuente primaria del dato.

**Criterio de aceptación:**

1. Dado un torneo en `INSCRIPCION_ABIERTA` con inscriptos sin AP, el
   organizador no puede cerrar inscripción.
2. Dado un torneo en `INSCRIPCION_ABIERTA` con todos los AP completos, el
   organizador puede cerrar inscripción y pasar a `PREPARACION`.
3. Dado un torneo en `PREPARACION`, la generación de grilla usa los AP
   declarados en inscripción y no depende de performances creadas manualmente.
4. La pantalla `Inscriptos` muestra AP declarados aun cuando todavía no exista
   una competencia operativa para el torneo.

**Clasificación:**
Track formal obligatorio. Hallazgo crítico de modelo/regla de negocio con
impacto transversal en `registro`, `torneo`, `competencia` y frontend
organizador.

---

## Hallazgos cerrados / sin impacto

*(ninguno en esta sesión)*
