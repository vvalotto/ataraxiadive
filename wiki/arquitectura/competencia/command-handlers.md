---
title: "Competencia — Command Handlers"
type: arquitectura-componente
bc: competencia
capa: application
tipo_componente: handler
responsabilidad: "16 handlers de comandos: orquestación del flujo grilla + ejecución de competencia y performances"
interfaces_out:
  - EventStorePort
  - PerformancesAPPort
  - PerformancesEstadoPort
  - CompetenciaEstadoPort
  - DisciplinaDescriptorPort
  - AtletaNombrePort
adr_refs: [ADR-001, ADR-004]
last_updated: "2026-05-23"
sources:
  - src/competencia/application/commands/
---

# Command Handlers

## Responsabilidad

Conjunto de 16 handlers de comandos que implementan los casos de uso de escritura del BC. Cada handler recibe un Command DTO, orquesta la reconstitución del aggregate, ejecuta el método de dominio y persiste los eventos. Usan [[handler-utils]] para la mecánica común.

## Handlers — Ciclo de Competencia (grilla)

| Handler | Comando | Aggregate |
|---------|---------|-----------|
| `ConfigurarIntervaloOTHandler` | `ConfigurarIntervaloOTCommand` | Competencia |
| `GenerarGrillaHandler` | `GenerarGrillaCommand` | Competencia |
| `AjustarGrillaHandler` | `AjustarGrillaCommand` | Competencia |
| `ConfirmarGrillaHandler` | `ConfirmarGrillaCommand` | Competencia |
| `AsignarJuezPerformanceHandler` | `AsignarJuezPerformanceCommand` | Competencia |
| `IniciarCompetenciaHandler` | `IniciarCompetenciaCommand` | Competencia |
| `FinalizarCompetenciaManualHandler` | `FinalizarCompetenciaManualCommand` | Competencia |

## Handlers — Ciclo de Performance (ejecución)

| Handler | Comando | Aggregate |
|---------|---------|-----------|
| `RegistrarAPHandler` | `RegistrarAPCommand` | Performance |
| `LlamarAtletaHandler` | `LlamarAtletaCommand` | Performance + Competencia |
| `RegistrarResultadoHandler` | `RegistrarResultadoCommand` | Performance |
| `RegistrarDNSHandler` | `RegistrarDNSCommand` | Performance |
| `AsignarTarjetaHandler` | `AsignarTarjetaCommand` | Performance |
| `ResolverRevisionHandler` | `ResolverRevisionCommand` | Performance |
| `CorregirResultadoHandler` | `CorregirResultadoCommand` | Performance |
| `CorregirResultadoTrasDNSHandler` | `CorregirResultadoTrasDNSCommand` | Performance |

## Handlers especiales

| Archivo | Rol |
|---------|-----|
| `_p08_finalizacion.py` | Módulo de cierre automático — verifica si todas las performances completaron y llama `finalizar()` en la Competencia. Usa [[calculador-hash-competencia]]. |

## Puertos requeridos por GenerarGrillaHandler

`GenerarGrillaHandler` es el handler más complejo: necesita [[performances-ap-port]] (para los APs) y `DisciplinaDescriptorPort` (para saber el tipo de ordenamiento de la disciplina).

## Patrón de implementación

```
1. Cargar stream via handler-utils.cargar_o_fallar()
2. Reconstituir aggregate (Competencia o Performance)
3. Llamar método de dominio del aggregate
4. Persistir eventos pendientes via handler-utils.persistir_eventos_pendientes()
5. (Opcional) Verificar si la Competencia puede finalizarse automáticamente
```

## Relaciones

- Todos usan [[handler-utils]] y [[event-store-port]]
- `GenerarGrillaHandler` usa [[performances-ap-port]]
- `LlamarAtletaHandler` lee estado de [[competencia-aggregate]] y escribe en [[performance-aggregate]]
- Los handlers son invocados desde [[router-competencia]]
