---
title: "DNS — Did Not Start"
type: concepto
last_updated: "2026-05-22"
sources:
  - wiki/arquitectura/competencia.md
  - wiki/arquitectura/resultados.md
---

# DNS — Did Not Start

Evento de dominio que registra que un [[atleta]] inscripto en una [[disciplina]] no se presentó a competir o no completó su intento de forma válida.

## Cuándo ocurre

El juez registra DNS cuando:
- El atleta fue llamado en la [[grilla]] pero no se presentó.
- El atleta abandonó antes de iniciar la performance medible.

Es una acción activa del juez ([[roles]]), no un estado implícito por ausencia.

## Efecto en la Performance

El aggregate `Performance` transiciona a un estado terminal `DNS`. El aggregate es inmutable a partir de ese punto.

**Evento generado:** `DNSRegistrado` — persiste en el stream `performance-{id}` del event store de [[competencia]].

## Efecto en el Ranking

Las entradas DNS aparecen al final del [[ranking]], después de todas las performances válidas y descalificadas. No se les asigna posición numérica.

| Tipo de resultado | Posición en ranking |
|-------------------|---------------------|
| Blanca / BlancaConPenalizaciones | Top (por mejor RP) |
| Roja | Después de válidas |
| DNS | Al final, sin posición |

## Corrección post-DNS

Una vez registrado DNS, el estado de la performance **no puede ser modificado** — las correcciones en Competencia solo aplican a resultados registrados (RP + tarjeta), no a DNS.

## BC propietario

[[competencia]] — handler `RegistrarDNSHandler`, evento `DNSRegistrado`.

## Conceptos relacionados

- [[performance]] — la performance que termina en DNS
- [[grilla]] — el atleta fue llamado desde la grilla antes de registrarse el DNS
- [[ranking]] — el DNS aparece al final sin posición
- [[tarjeta]] — alternativa al DNS cuando el atleta completó la performance pero fue descalificado
