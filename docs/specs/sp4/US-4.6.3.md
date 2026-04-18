# US-4.6.3: UI de auditoría — traza de eventos por performance

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.6
**Bounded Context**: `frontend/`
**Capas afectadas**: `frontend/src/` (nueva pantalla organizador)

---

## Descripción

Como **organizador**,
quiero **ver en la app la traza completa de eventos de cualquier performance y el hash SHA-256 de una disciplina cerrada**
para **auditar resultados, detectar correcciones y certificar integridad ante la federación sin necesidad de acceso a la base de datos**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Query | `ObtenerAuditLog` (US-4.6.1) | Fuente de datos de la pantalla |
| Evento de dominio | Todos los eventos de `Performance` | Entradas del log mostradas en la UI |
| Hash SHA-256 | Del evento `CompetenciaCerrada` (US-4.6.2) | Mostrado en el encabezado de la disciplina cerrada |

### Lenguaje ubicuo relevante

- **Traza:** la secuencia cronológica de eventos de una performance, visible como timeline en la UI.
- **Hash de disciplina:** digest SHA-256 visible al organizador cuando la disciplina ya fue cerrada. Permite verificar integridad externamente.
- **Estado de disciplina:** `EnEjecucion` (sin hash) o `Cerrada` (con hash visible).

---

## Especificación del comportamiento

### Invariantes

- **INV-4.6.3-01:** Solo los usuarios con rol `organizador` o `admin` ven la pantalla de auditoría. Un juez no tiene acceso.
- **INV-4.6.3-02:** La traza es de solo lectura — ningún elemento de la UI permite modificar eventos.
- **INV-4.6.3-03:** El hash SHA-256 se muestra **solo** si la disciplina está en estado `Cerrada`. Si está `EnEjecucion`, el campo no aparece.
- **INV-4.6.3-04:** Los eventos se muestran en orden cronológico ascendente (el más antiguo primero).

### Flujo de navegación

```
/organizador/torneos
  → /organizador/torneos/{torneo_id}/competencias
      → /organizador/competencias/{competencia_id}/auditoria
          → lista de atletas de la disciplina
              → /organizador/competencias/{competencia_id}/auditoria/{atleta_id}
                  → traza de eventos de esa performance
```

### Layout de la pantalla de auditoría (disciplina)

```
┌─────────────────────────────────────────────────┐
│  Auditoría — DNF                                │
│  Torneo: Open BA 2026 · Estado: Cerrada         │
│                                                 │
│  Hash SHA-256:                                  │
│  a3f7c2d1... [copiar]                           │
│  ─────────────────────────────────────────────  │
│  Atletas (10)                                   │
│  ┌──────────────────────────────────┐           │
│  │ Martín García       Blanca  →    │           │
│  │ Ana Flores     Bl+Pen (2)   →    │           │
│  │ Roberto Chen         Roja   →    │           │
│  │ Diego Vega            DNS   →    │           │
│  └──────────────────────────────────┘           │
└─────────────────────────────────────────────────┘
```

### Layout de la traza de una performance

```
┌─────────────────────────────────────────────────┐
│  ← Martín García · DNF · Blanca                 │
│  ─────────────────────────────────────────────  │
│  ● PerformanceRegistrada                        │
│    10:05:00 · AP: 60.0m                         │
│                                                 │
│  ● ResultadoRegistrado                          │
│    10:12:34 · RP: 58.0m                         │
│                                                 │
│  ● TarjetaAsignada                              │
│    10:12:40 · Blanca · 0 penalizaciones         │
└─────────────────────────────────────────────────┘
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-4.6.3 — UI auditoría del organizador

  Background:
    Given el usuario está autenticado como organizador
    And existe la competencia "comp-abc" con disciplina DNF cerrada
    And el hash SHA-256 de DNF es "a3f7c2..."
    And el atleta "Martín García" tiene 3 eventos en el audit log

  Scenario: organizador navega a la pantalla de auditoría
    When accede a /organizador/competencias/comp-abc/auditoria
    Then ve la lista de atletas de la disciplina con su resultado final
    And el encabezado muestra el estado "Cerrada"
    And el hash SHA-256 "a3f7c2..." es visible con botón copiar

  Scenario: hash NO visible si la disciplina está en ejecución
    Given la disciplina está en estado EnEjecucion (no cerrada)
    When el organizador accede a la pantalla de auditoría
    Then el campo hash SHA-256 NO aparece en la UI
    And el estado muestra "En ejecución"

  Scenario: organizador ve la traza de una performance
    When selecciona al atleta "Martín García"
    Then ve 3 eventos en orden cronológico ascendente
    And el primer evento es "PerformanceRegistrada · AP: 60.0m"
    And el último evento es "TarjetaAsignada · Blanca"

  Scenario: performance con corrección muestra todos los eventos
    Given la performance de "Ana Flores" tiene 4 eventos (incluye ResultadoCorregido)
    When el organizador ve su traza
    Then ve 4 eventos
    And el evento "ResultadoCorregido" aparece con timestamp posterior al original

  Scenario: juez no puede acceder a la pantalla de auditoría
    Given el usuario está autenticado como juez
    When intenta navegar a /organizador/competencias/comp-abc/auditoria
    Then es redirigido a su pantalla de juez (o recibe 403)

  Scenario: botón copiar hash funciona
    When el organizador pulsa el botón copiar junto al hash
    Then el hash completo "a3f7c2..." queda en el portapapeles
    And aparece un feedback visual breve ("Copiado")
```

---

## Impacto arquitectónico

- [ ] No — se implementa con la arquitectura existente (React + rutas por rol)

**Capa(s) afectadas:**
- [x] Frontend — nuevas pantallas: `AuditoriaCompetenciaPage`, `AuditoriaPerformancePage`
- [x] Frontend — nuevo hook: `useAuditLog(competencia_id, atleta_id)`
- [x] Frontend — consume el endpoint de US-4.6.1

**Notas:**
- La pantalla es solo para el rol `organizador`. Las rutas del juez (`/juez/...`) no se tocan.
- El hash se muestra truncado (primeros 16 chars + "...") con el texto completo en tooltip. El botón copiar copia el hash completo.
- En modo offline la pantalla puede no estar disponible (solo para organizador, que siempre opera con conexión).

---

## Referencias

- Plan SP4 §INC-4.6 — US-4.6.3
- US-4.6.1: endpoint que alimenta la pantalla
- US-4.6.2: fuente del hash SHA-256 mostrado
- ADR-001: Event Sourcing — los eventos son el audit log
- `docs/design/architecture.md` §Frontend — rutas por rol

---

*Redactado: 2026-04-15 — INC-4.6 Auditoría y Exportación*
