---
title: "Vista de Arquitectura — C4 L1+L2+L3"
type: vista
last_updated: "2026-05-31"
sources:
  - wiki/arquitectura/
  - docs/architecture/
  - docs/adr/
---

# Vista de Arquitectura — C4 L1 + L2 + L3

> El sistema visto en tres niveles de detalle: contexto externo (L1), Bounded Contexts (L2) y componentes internos (L3).

---

## C4 L1 — Contexto del Sistema

→ Página completa: [[arquitectura/sistema]]

| Elemento | Descripción |
|----------|-------------|
| **Sistema** | AtaraxiaDive — gestión de torneos de apnea |
| **Actores** | Organizador · Juez · Atleta |
| **Sistemas externos** | Resend (email) · Fly.io (hosting) · Navegador / PWA (cliente offline) |
| **Restricción clave** | Offline-first por conectividad limitada en pileta ([[decisiones/ADR-003-offline-first-pwa]]) |

---

## Propósito

Responder preguntas sobre cómo está organizado el sistema internamente: qué BCs existen, qué tipo de dominio y persistencia tienen, qué componentes contienen, qué interfaces exponen y cómo se relacionan entre sí. Es la vista del arquitecto, el nuevo desarrollador que ingresa al proyecto y el tech lead evaluando deuda técnica.

## Stakeholder principal

Arquitecto de software, desarrollador que ingresa al proyecto, Victor evaluando el experimento IEDD.

---

## C4 L2 — Bounded Contexts (contenedores)

```dataview
TABLE tipo_ddd AS "Tipo DDD", persistencia AS "Persistencia", db AS "Base de datos", test_coverage AS "Cobertura"
FROM "wiki/arquitectura"
WHERE type = "arquitectura" AND tipo_ddd != null
SORT tipo_ddd ASC
```

---

## C4 L3 — Componentes por BC

### Competencia

```dataview
TABLE tipo_componente AS "Tipo", capa AS "Capa", responsabilidad AS "Responsabilidad"
FROM "wiki/arquitectura/competencia"
WHERE type = "arquitectura-componente"
SORT capa ASC, tipo_componente ASC
```

### Registro

```dataview
TABLE tipo_componente AS "Tipo", capa AS "Capa", responsabilidad AS "Responsabilidad"
FROM "wiki/arquitectura/registro"
WHERE type = "arquitectura-componente"
SORT capa ASC, tipo_componente ASC
```

### Torneo

```dataview
TABLE tipo_componente AS "Tipo", capa AS "Capa", responsabilidad AS "Responsabilidad"
FROM "wiki/arquitectura/torneo"
WHERE type = "arquitectura-componente"
SORT capa ASC, tipo_componente ASC
```

### Resultados

```dataview
TABLE tipo_componente AS "Tipo", capa AS "Capa", responsabilidad AS "Responsabilidad"
FROM "wiki/arquitectura/resultados"
WHERE type = "arquitectura-componente"
SORT capa ASC, tipo_componente ASC
```

### Identidad

```dataview
TABLE tipo_componente AS "Tipo", capa AS "Capa", responsabilidad AS "Responsabilidad"
FROM "wiki/arquitectura/identidad"
WHERE type = "arquitectura-componente"
SORT capa ASC, tipo_componente ASC
```

### Notificaciones

```dataview
TABLE tipo_componente AS "Tipo", capa AS "Capa", responsabilidad AS "Responsabilidad"
FROM "wiki/arquitectura/notificaciones"
WHERE type = "arquitectura-componente"
SORT capa ASC, tipo_componente ASC
```

---

## Componentes por tipo — todo el sistema

```dataview
TABLE WITHOUT ID
  tipo_componente AS "Tipo",
  length(rows) AS "Total",
  map(rows, (r) => r.bc) AS "BCs"
FROM "wiki/arquitectura"
WHERE type = "arquitectura-componente"
GROUP BY tipo_componente
SORT length(rows) DESC
```

---

## Ports — interfaces entre componentes

```dataview
TABLE bc AS "BC", interfaces_out AS "Interfaces out", adr_refs AS "ADRs"
FROM "wiki/arquitectura"
WHERE type = "arquitectura-componente" AND tipo_componente = "port"
SORT bc ASC
```

---

## Todos los componentes del sistema

```dataview
TABLE bc AS "BC", tipo_componente AS "Tipo", capa AS "Capa"
FROM "wiki/arquitectura"
WHERE type = "arquitectura-componente"
SORT bc ASC, capa ASC
```

---

## Preguntas características y recorridos

### 1. ¿Qué BC implementa la lógica de negocio central del deporte?

**Respuesta directa:** BC Competencia — Core Domain con Event Sourcing.

**Recorrido:**
[[arquitectura/competencia]] → [[arquitectura/competencia/performance-aggregate]] → [[arquitectura/competencia/competencia-aggregate]] → [[ADR-001-event-sourcing-competencia]]

---

### 2. ¿Cómo se autentica un usuario y qué claims lleva el token?

**Recorrido:**
[[arquitectura/identidad]] → [[arquitectura/identidad/router-identidad]] → [[arquitectura/identidad/command-handlers-identidad]] → [[arquitectura/identidad/jwt-service]]

El JWT lleva: `{sub: usuario_id, email, nombre, apellido, rol (elegido), exp}`. Los BCs downstream adoptan relación Conformist: consumen el token sin negociar el modelo de identidad.

---

### 3. ¿Qué componente implementa la idempotencia de notificaciones?

**Recorrido:**
[[arquitectura/notificaciones]] → [[arquitectura/notificaciones/notificacion-aggregate]] (factory `solicitar_envio` verifica `existe_envio_exitoso_previo`) → [[arquitectura/notificaciones/sqlite-notificacion-event-store]] (método `exists_success_by_evento_fuente_id`)

La clave de idempotencia es `EventoFuenteId` — ID del evento de dominio fuente. El índice `json_extract(payload, '$.evento_fuente_id')` hace esta verificación eficiente.

---

### 4. ¿Dónde está el acoplamiento cross-BC y cómo se gestiona?

El sistema evita HTTP entre BCs en runtime. El patrón predominante es **lectura directa de SQLite**:

| Adaptador | Lee de | Usado por |
|-----------|--------|-----------|
| `AtletaNombreAdapter` | `registro.db` | BC Competencia |
| `AtletaCategoriaAdapter` | `registro.db` | BC Resultados |
| `SQLiteTorneoConsulta` | `torneo.db` | BC Registro |
| `ResultadosCompetenciaAdapter` | `competencia.db` | BC Resultados |

**Recorrido completo:**
[[arquitectura/competencia/atleta-nombre-port]] → [[arquitectura/registro/sqlite-repositories]] → [[arquitectura/resultados/resultados-competencia-port]]

---

### 5. ¿Cómo funciona el cálculo de rankings y el algoritmo FAAS?

**Recorrido:**
[[arquitectura/resultados/ranking-competencia]] → [[arquitectura/resultados/algoritmo-faas]] → [[arquitectura/resultados/command-handlers-resultados]] → [[arquitectura/resultados/query-handlers-resultados]] (fallback provisional)

El fallback en tiempo real: si no existe stream `ranking-{competencia_id}-{disciplina}` en `resultados.db`, el router consulta directamente las performances en `competencia.db`.

---

### 6. ¿Qué precondiciones controlan las transiciones del ciclo de vida del torneo?

El BC Torneo expone callbacks desde `configure_*` para que otros BCs inyecten precondiciones sin acoplar el dominio:

**Recorrido:**
[[arquitectura/torneo/torneo-aggregate]] (estados: CREADO → INSCRIPCION_ABIERTA → PREPARACION → EJECUCION → PREMIACION → CERRADO) → [[arquitectura/torneo/command-handlers-torneo]] → [[arquitectura/torneo/router-torneo]] (funciones `configure_*`)

---

## Páginas hub de esta vista

| Página | Por qué es hub |
|--------|----------------|
| [[arquitectura/competencia]] | Core Domain — lógica central del deporte |
| [[arquitectura/competencia/performance-aggregate]] | Aggregate principal del sistema |
| [[arquitectura/identidad/router-identidad]] | Guards cross-cutting (`OrganizadorDep`, `JuezDep`, `AtletaDep`) usados por todos los BCs |
| [[arquitectura/notificaciones/notificacion-aggregate]] | Patrón de idempotencia ES |
| [[arquitectura/resultados/algoritmo-faas]] | Algoritmo de puntuación FAAS |
| [[arquitectura/torneo/torneo-aggregate]] | Máquina de estados del torneo |
| [[ADR-001-event-sourcing-competencia]] | Decisión fundacional de arquitectura |
| [[ADR-007-sqlite-persistencia-bc]] | Un archivo .db por BC |
