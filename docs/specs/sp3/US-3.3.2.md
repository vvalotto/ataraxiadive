# US-3.3.2: Flujo E2E — inscribir atleta → AP → grilla

**Estado**: `Done`
**Sprint**: SP3 — El Torneo
**Incremento**: INC-3.3
**Bounded Context**: `competencia` · `registro` · `torneo`
**Capas afectadas**: `tests/integration/`

---

## Descripción

Como **desarrollador del sistema**,
quiero **verificar el flujo end-to-end desde la inscripción de un atleta hasta la generación de grilla**
para **confirmar que los BCs Torneo, Registro y Competencia funcionan integrados**.

---

## Contexto

Esta US no agrega nuevo código de producción — consolida la integración entre los 3 BCs incorporados en INC-3.1, INC-3.2 e INC-3.3. El único artefacto nuevo es el test de integración E2E.

La relación entre BCs en este flujo:
```
Torneo (crea contexto) → Registro (atleta se inscribe) → Competencia (AP + grilla)
```

El vínculo Registro→Competencia en SP3 es **implícito**:
- `participante_id` en Competencia = `atleta_id` de Registro (mismo UUID)
- No hay ACL automático en SP3 — el caller usa el mismo UUID en ambos BCs
- El ACL formal (`AtletaInscripto → ParticipanteHabilitado`) queda para SP4

---

## Especificación

### Precondición

```
US-3.1.1, US-3.1.2: Torneo funcional
US-3.2.1, US-3.2.2, US-3.2.3: Identidad + Atleta + Inscripcion funcional
US-3.3.1: Competencia con torneo_id
```

### Postcondición

```
tests/integration/e2e/test_flujo_torneo_competencia.py
```

Flujo del test:

```python
# Paso 1 — Torneo
torneo_id = await crear_torneo(nombre="Copa Test", disciplinas=[STA, DNF])
await abrir_inscripcion(torneo_id)

# Paso 2 — Atletas y registros
atleta_id = uuid4()
await registrar_atleta(atleta_id, nombre="Juan Perez", ...)
await inscribir_atleta(atleta_id, torneo_id, disciplinas=[STA])

# Paso 3 — Competencia STA (usando torneo_id)
competencia_id = uuid4()
await configurar_intervalo_ot(competencia_id, Disciplina.STA, intervalo=300, torneo_id=torneo_id)

# Paso 4 — AP y grilla (participante_id = atleta_id)
await registrar_ap(competencia_id, participante_id=atleta_id, valor=360, unidad=Segundos)
await generar_grilla(competencia_id)
await confirmar_grilla(competencia_id)

# Paso 5 — Verificación
grilla = await obtener_grilla(competencia_id)
assert len(grilla.entradas) == 1
assert grilla.entradas[0].atleta_id == atleta_id
assert competencia.torneo_id == torneo_id
```

### Invariantes

- `INV-E2E-01`: El `atleta_id` de Registro coincide con el `participante_id` usado en Competencia
- `INV-E2E-02`: La `competencia_id` referencia el mismo `torneo_id` del torneo creado
- `INV-E2E-03`: La grilla generada contiene exactamente los atletas con AP registrado

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-3.3.2 — Flujo E2E Torneo-Registro-Competencia

  Scenario: flujo completo inscripcion → AP → grilla
    Given torneo abierto para inscripción
    And atleta registrado e inscripto en disciplina STA
    And competencia STA configurada con torneo_id
    When atleta registra su AP en la competencia
    And se genera la grilla
    Then la grilla contiene al atleta
    And competencia.torneo_id == torneo_id

  Scenario: atleta sin AP no aparece en grilla
    Given 2 atletas inscriptos, solo 1 registra AP
    When se genera la grilla
    Then la grilla contiene solo al atleta con AP (RF-PR-04)

  Scenario: múltiples atletas ordenados por AP
    Given 3 atletas con APs: 360s, 240s, 300s (STA — tiempo: mayor → menor)
    When se genera la grilla
    Then el orden es: 360s → 300s → 240s (RF-PR-05)
```

---

## Notas de implementación

- El test usa instancias reales (SQLite en memoria o archivo temporal), no mocks.
- Se crean los handlers directamente, sin pasar por la API HTTP (test de integración puro, no E2E HTTP).
- Si hay una API HTTP disponible, el test opcional puede usar `httpx.AsyncClient`.
- Este test documenta el contrato implícito `atleta_id = participante_id` para que en SP4 se pueda agregar la validación formal.

---

## Referencias

- US-3.3.1: `torneo_id` en Competencia
- US-3.2.3: Inscripcion
- US-3.1.2: API Torneo
- Plan: `docs/plans/sp3/PLAN-SP3.md`

---

*Redactado: 2026-03-28 — SP3*
