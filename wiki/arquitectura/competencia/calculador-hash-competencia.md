---
title: "Competencia — Service CalculadorHashCompetencia"
type: arquitectura-componente
bc: competencia
capa: domain
tipo_componente: service
responsabilidad: "Calcula el hash SHA-256 de la secuencia canónica de eventos de una disciplina para auditoría"
interfaces_out: []
adr_refs: [ADR-018]
last_updated: "2026-05-23"
sources:
  - src/competencia/domain/services/calculador_hash_competencia.py
us_origen:
  - US-4.6.2-calculador-hash-competencia-hash-sha-256-de-integridad
---

# Service CalculadorHashCompetencia

## Responsabilidad

Servicio de dominio stateless que calcula el **hash SHA-256** de una secuencia ordenada de eventos de una disciplina. El hash se persiste en el evento `CompetenciaFinalizada` y sirve como sello de auditoría del resultado de la competencia (ADR-018).

## Algoritmo

1. Por cada evento: serializa a JSON canónico con `sort_keys=True` sobre `{tipo, datos, sequence_number, timestamp}`
2. Concatena todos los JSONs con `\n`
3. Aplica `SHA-256` sobre el resultado en UTF-8
4. Stream vacío → hash de string vacío (`sha256(b"")`)

## Uso

```python
hash_val = CalculadorHashCompetencia.calcular(eventos)
competencia.finalizar(..., hash_sha256=hash_val)
```

Llamado desde `_p08_finalizacion.py` (módulo de orquestación de cierre automático) y desde `FinalizarCompetenciaManualHandler`.

## Valor para el dominio

Permite verificar post-facto que los resultados de una disciplina no fueron alterados. Cualquier modificación del event store cambiaría el hash. El organizador puede compararlo con el hash publicado al cierre.

## Relaciones

**Contenedor:** [[arquitectura/competencia]]

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/competencia/domain/services/calculador_hash_competencia.py` | Servicio SHA-256 sobre secuencia de eventos |

## ADRs relacionados

- [[ADR-018-hash-sha256-auditoria]] — decisión de usar SHA-256 sobre la secuencia de eventos
