# Contexto de Implementación — US-4.3.4

| Campo | Valor |
|---|---|
| **US** | US-4.3.4 — Tarjeta amarilla — flujo de revisión y resolución desde la UI |
| **Incremento** | INC-4.3 |
| **Sprint** | SP4 — La Plataforma |
| **Fecha** | 2026-04-12 |
| **Branch** | `feature/US-4.3.4-tarjeta-amarilla` |

---

## Hallazgos relevantes del código actual

### 1. El dominio no tiene todavía estado `EnRevision`

La máquina de estados vigente en `EstadoPerformance` es:

- `AnunciadaAP`
- `Llamada`
- `ResultadoRegistrado`
- `Ejecutada`
- `DNS`

Hoy no existe un estado intermedio entre `ResultadoRegistrado` y `Ejecutada`.

Conclusión:

- `US-4.3.4` sí requiere cambio real de dominio;
- no alcanza con resolverlo solo en frontend o router.

### 2. `AsignarTarjeta(Amarilla)` hoy no deja la performance pendiente

`Performance.asignar_tarjeta(...)` actualmente:

- solo acepta estado `ResultadoRegistrado`;
- construye `TarjetaAsignacion`;
- calcula `ResolucionTarjeta`;
- aplica `_aplicar_resolucion_tarjeta(...)`;
- deja la performance en `Ejecutada`.

Además, para `TipoTarjeta.Amarilla` el dominio vigente exige `motivo_texto`.

Conclusión:

- la lógica actual de amarilla es de resultado final, no de revisión pendiente;
- habrá que redefinir el comportamiento para que amarilla pase a `EnRevision`;
- conviene preservar compatibilidad mínima exigiendo `motivo_texto` al asignar amarilla.

### 3. No existe comando ni endpoint para resolver una revisión

En `competencia/application/commands/` no existe hoy:

- `ResolverRevisionCommand`
- `ResolverRevisionHandler`

Tampoco existe en `competencia/api/router.py`:

- `POST /competencia/{competencia_id}/resolver-revision`

Conclusión:

- la US necesita una operación nueva de application + API;
- no conviene sobrecargar `asignar-tarjeta` para cerrar la revisión.

### 4. No existe evento de dominio para la resolución

Los eventos actuales de performance incluyen:

- `APRegistrado`
- `AtletaLlamado`
- `ResultadoRegistrado`
- `DNSRegistrado`
- `TarjetaAsignada`
- `ResultadoCorregido`

No existe `RevisionResuelta`.

Conclusión:

- la nueva transición debe quedar persistida con un evento dedicado;
- eso simplifica reconstrucción, auditoría y soporte futuro para `INC-4.6`.

### 5. La grilla ya consume `estado`, así que puede absorber `EnRevision`

La UI del juez ya renderiza estados derivados de la grilla y de la performance activa.
Eso permite agregar una variante visual nueva para `EnRevision` sin rehacer la navegación.

Conclusión:

- la adaptación de frontend puede montarse sobre el flujo actual;
- `GrillaPage` y `PerformanceFlowPage` necesitan reconocer `EnRevision`.

### 6. El tracker anterior quedó inconsistente

`US-4.3.3-tracking.json` quedó con fases 1 y 2 en `in_progress` mientras la fase 3 ya figura
como completada.

Conclusión:

- para `US-4.3.4` hay que operar con secuencialidad estricta real, aunque el archivo de tracking
  previo haya quedado desalineado;
- no conviene encadenar implementación sin dejar antes los artefactos de Fase 1 y 2 en disco.

---

## Decisión para seguir

La implementación de `US-4.3.4` debe tratar la tarjeta amarilla como estado transitorio real:

1. agregar `EstadoPerformance.EnRevision`;
2. cambiar `AsignarTarjeta(Amarilla)` para que no cierre la performance;
3. introducir `RevisionResuelta`;
4. agregar `ResolverRevisionCommand` + handler + endpoint HTTP;
5. adaptar grilla y flujo del juez para resolución inmediata o diferida.

---

*Generado: 2026-04-12 — Fase 0 US-4.3.4*
