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
us_origen:
  - US-1.2.1-registrar-ap
  - US-1.2.2-llamar-atleta
  - US-1.2.3-registrar-resultado
  - US-1.2.4-asignar-tarjeta-blanca-roja
  - US-1.2.5-registrar-dns
  - US-1.2.6-corregir-resultado
  - US-2.1.1-configurar-intervalo-ot-scaffold-aggregate-competencia
  - US-2.1.2-generar-grilla-regenerar-grilla
  - US-2.1.3-ajustar-grilla
  - US-2.1.4-confirmar-grilla-iniciar-competencia
  - US-2.4.1-competencia-finalizada-automatico-politica-p-08
  - US-4.1.1-motivo-dq-str-enum-tarjeta-asignacion-extendida-brecha
  - US-4.3.4-estado-en-revision-resolver-revision-ui-tarjeta
  - US-5.1.4-grilla-panel-generar-y-confirmar-grilla-por-disciplina
  - US-5.2.2-accion-finalizar-prueba-por-disciplina
  - US-ADJ-1.4-refactoring-api-dip-en-router-p-08-a-composition-root
  - US-ADJ-2.7-refactoring-eliminar-codigo-muerto-get-on-finalizada
  - US-ADJ-6.3-eliminar-inspect-signature-callback-on-finalizada
  - US-ADJ-7.1-bug-sp4-003-corregir-resultado-tras-dns
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

**Contenedor:** [[arquitectura/competencia]]

- Todos usan [[handler-utils]] y [[event-store-port]]
- `GenerarGrillaHandler` usa [[performances-ap-port]]
- `LlamarAtletaHandler` lee estado de [[competencia-aggregate]] y escribe en [[performance-aggregate]]
- Los handlers son invocados desde [[router-competencia]]

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/competencia/application/commands/` |  |
