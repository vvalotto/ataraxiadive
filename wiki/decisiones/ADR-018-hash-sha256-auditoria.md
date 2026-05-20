---
title: "ADR-018: Hash SHA-256 para integridad de resultados de competencia"
type: decision
last_updated: "2026-05-20"
sources:
  - docs/adr/ADR-018-hash-sha256-auditoria.md
estado: Aceptada
fecha: 2026-04-16
bcs_afectados: [competencia]
---

# ADR-018: Hash SHA-256 para integridad de resultados de competencia

## Decisión

Al cerrar una disciplina (`CerrarCompetencia`), calcular el hash SHA-256 de la secuencia canónica de eventos y persistirlo como campo `hash_sha256` en el payload del evento `CompetenciaCerrada`.

## Por qué

Los torneos pueden ser oficiales ante la FAAS. El event store es inmutable **por convención arquitectónica** (sin endpoint de eliminación), pero no por restricción física — un administrador con acceso directo a SQLite podría modificar registros sin que la aplicación lo detecte. El hash permite verificar integridad externamente sin ejecutar la aplicación.

## Algoritmo de la secuencia canónica

Implementado en `CalculadorHashCompetencia` (`competencia/domain/services/`):

1. Recuperar todos los eventos del stream, ordenados por `sequence_number` ASC.
2. Para cada evento, construir diccionario canónico:
   ```python
   {
     "datos": evento["payload"],
     "sequence_number": evento["sequence"],
     "timestamp": evento["occurred_at"],
     "tipo": evento["event_type"],
   }
   ```
3. Serializar cada dict con `sort_keys=True` (orden determinístico).
4. Concatenar con `\n`.
5. `sha256(concatenado.encode("utf-8")).hexdigest()` → 64 caracteres hex.

La especificación es suficiente para que cualquier herramienta externa reproduzca el cálculo (`sha256sum`, Python stdlib, OpenSSL).

## Consecuencias vigentes

- SHA-256 está en `hashlib` (stdlib) — sin dependencias adicionales.
- El hash vive en `CompetenciaCerrada`: la auditoría encuentra eventos y hash en el mismo lugar.
- El hash protege contra alteración **posterior al cierre**. Antes del cierre, el organizador puede corregir performances — comportamiento esperado.
- **Límite**: no protege contra un atacante que modifique tanto los eventos como el evento `CompetenciaCerrada`. Prueba consistencia interna, no integridad frente a adversario con acceso físico a la DB.

## Evolución futura (SP5)

- Firma digital con clave privada del organizador.
- Publicación del hash en API de la FAAS o registro externo.
- UI de verificación pública para atletas y jueces.

## ADRs relacionados

- [[ADR-001-event-sourcing-competencia]] — el event store cuya integridad protege este hash
- [[ADR-008-event-store-sqlite]] — infraestructura donde vive el stream de eventos
