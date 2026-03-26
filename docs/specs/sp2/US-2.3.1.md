# US-2.3.1: Ejecución Multi-Andarivel

**Estado**: `Backlog`
**Incremento**: Inc 2.3 — Andariveles Simultáneos
**Subproyecto**: SP2 — La Competencia
**Agregado principal**: `Performance` · `Competencia`
**Bounded Context**: `competencia`

---

## Descripción (lenguaje de negocio)

Como **juez**,
quiero **poder tener 2 o 3 andariveles activos simultáneamente, con un atleta por andarivel**,
para **que la competencia avance más rápido sin tener que esperar a que un atleta finalice antes de llamar al siguiente**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Aggregate (existente) | `Competencia` | `generar_grilla()` ya distribuye atletas por andariveles (parámetro `andariveles`) |
| Aggregate (existente) | `Performance` | Tiene `andarivel` almacenado desde `AtletaLlamado` |
| Port (nuevo) | `AndarivelesActivosPort` | Consulta qué performances están en estado `Llamada` para verificar conflictos de andarivel |
| Read Model (nuevo) | `AndarivelesActivos` | Lista de andariveles con atleta actual por andarivel |

### Lenguaje ubicuo relevante

- **Andarivel activo**: andarivel que tiene un atleta en estado `Llamada` (performance no finalizada).
- **Conflicto de andarivel**: intento de llamar a un atleta en un andarivel que ya está activo. Rechazado por INV-C-05.
- **Multi-andarivel**: configuración donde la grilla asigna posiciones alternadas entre N andariveles. Atleta 1 → andarivel 1, atleta 2 → andarivel 2, atleta 3 → andarivel 1, etc.

---

## Especificación del comportamiento

### INV-C-05 (nuevo): no hay dos performances en estado Llamada en el mismo andarivel

```
INV-C-05: en un instante dado, cada andarivel puede tener como máximo una Performance
          en estado Llamada. Llamar a un atleta en un andarivel ya activo es rechazado.
```

Esta invariante se verifica en el handler `LlamarAtletaHandler`: antes de ejecutar el comando,
consulta `AndarivelesActivosPort` para detectar el conflicto.

### La asignación de andariveles en GenerarGrilla

Ya implementada desde US-2.1.2: `andarivel = ((posicion - 1) % andariveles) + 1`.

US-2.3.1 no modifica la lógica de generación — solo agrega la verificación de conflicto en `LlamarAtleta` y expone el nuevo Read Model.

### Operación: LlamarAtleta (con verificación multi-andarivel)

**Nombre**: `LlamarAtletaHandler.handle()`

| | Descripción |
|---|---|
| **Precondición** | Competencia en estado `EnEjecucion`. El andarivel del atleta a llamar no tiene ninguna performance activa en estado `Llamada` (INV-C-05). |
| **Postcondición** | `AtletaLlamado` persiste. El andarivel queda marcado como activo. |
| **Excepciones** | `AndarivelesActivosPort` devuelve conflicto → `AndarivelesConflicto` |

**Ejemplo concreto:**

```
Grilla 2 andariveles:
  pos 1: Atleta A, andarivel 1
  pos 2: Atleta B, andarivel 2
  pos 3: Atleta C, andarivel 1

Estado actual: AtletaLlamado(A, andarivel=1) activo (Llamada)

LlamarAtleta(B, andarivel=2) → OK   (andarivel 2 libre)
LlamarAtleta(C, andarivel=1) → AndarivelesConflicto   (andarivel 1 ocupado por A)

Juez registra resultado de A → estado Ejecutada
LlamarAtleta(C, andarivel=1) → OK   (andarivel 1 liberado)
```

---

### Read Model: AndarivelesActivos

Proyecta el estado de cada andarivel en un instante dado, leyendo los streams de performances.

```
AndarivelesActivos:
  andariveles: list[
    {
      numero: int,          # 1, 2, 3, ...
      ocupado: bool,
      atleta_id: str | None,
      performance_id: str | None,
      ot_programado: str | None
    }
  ]
```

**Endpoint:** `GET /competencia/{id}/andariveles?disciplina=STA`

---

## Criterios de aceptación (BDD)

```gherkin
Feature: Ejecución Multi-Andarivel — dos atletas simultáneos sin conflicto

  Background:
    Given una competencia STA en estado EnEjecucion con 2 andariveles
    And la grilla tiene: pos 1 = Atleta A (andarivel 1), pos 2 = Atleta B (andarivel 2), pos 3 = Atleta C (andarivel 1)

  Scenario: Llamar a atletas en andariveles distintos — sin conflicto
    When el juez llama a Atleta A (andarivel 1)
    And el juez llama a Atleta B (andarivel 2)
    Then ambos AtletaLlamado persisten
    And GET /andariveles muestra andarivel 1 ocupado por A y andarivel 2 ocupado por B

  Scenario: Rechazo — llamar a atleta en andarivel ya activo (INV-C-05)
    Given Atleta A fue llamado y está en estado Llamada en andarivel 1
    When el juez intenta llamar a Atleta C (andarivel 1)
    Then el sistema rechaza con "AndarivelesConflicto"
    And ningún evento es persistido

  Scenario: Llamar al siguiente atleta del mismo andarivel tras finalizar el anterior
    Given Atleta A fue llamado (andarivel 1), completó con tarjeta blanca
    When el juez llama a Atleta C (andarivel 1)
    Then AtletaLlamado(C) persiste
    And GET /andariveles muestra andarivel 1 ocupado por C

  Scenario: AndarivelesActivos refleja estado correcto
    Given Atleta A fue llamado (andarivel 1) y está en Llamada
    When se consulta GET /competencia/{id}/andariveles
    Then la respuesta muestra andarivel 1 ocupado con atleta A
    And andarivel 2 libre

  Scenario: GenerarGrilla con 2 andariveles distribuye correctamente
    Given una competencia con 4 atletas y 2 andariveles configurados
    When se genera la grilla
    Then las posiciones 1 y 3 quedan en andarivel 1
    And las posiciones 2 y 4 quedan en andarivel 2
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [ ] No — extiende `LlamarAtletaHandler` con un nuevo port; la distribución por andariveles ya existe

**Capas afectadas:**
- [ ] Domain — sin cambios (la lógica es de aplicación)
- [x] Application — `LlamarAtletaHandler` inyecta `AndarivelesActivosPort`; nuevo handler `ObtenerAndarivelesActivosHandler`
- [x] Infrastructure — `AndarivelesActivosAdapter` consulta streams de performances y proyecta el estado de cada andarivel
- [x] API — `GET /competencia/{id}/andariveles`

**Nueva excepción de aplicación:** `AndarivelesConflicto` — en `application/commands/llamar_atleta.py`.

---

## Notas de implementación

- `AndarivelesActivosAdapter` lee todos los streams `performance-{cid}-*` de la disciplina y filtra los que están en estado `Llamada`. No requiere Event Store propio — reutiliza el mismo SQLite que BC Competencia.
- El número de andariveles de la grilla se puede inferir del evento `GrillaDeSalidaGenerada` (campo `andariveles` en el payload) o pasarse por query param. Recomendado: leer del evento para que sea auto-consistente.
- Esta US no modifica `GenerarGrilla` ni `GenerarGrillaHandler` — la distribución por andariveles ya es funcional desde US-2.1.2.

---

## Referencias

- SP2 candidatas: `docs/plans/sp2/SP2-candidatas.md` — Inc 2.3, US-2.3.1
- RF-PR-06: ¿pueden competir varios atletas simultáneamente? → Sí
- Event Storming Competencia: `docs/design/event-storming-competencia.md` — Flujo 3 (ejecución)
- US-2.2.2 (prerequisito de orden): `posicion_grilla` en Performance debe estar disponible

---

*Redactado: 2026-03-26 — IEDD Capa 3*
