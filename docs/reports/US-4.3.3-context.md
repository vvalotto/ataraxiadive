# Contexto de Implementación — US-4.3.3

| Campo | Valor |
|---|---|
| **US** | US-4.3.3 — Casos alternativos — DNS, BKO y tarjeta blanca con penalizaciones |
| **Incremento** | INC-4.3 |
| **Sprint** | SP4 — La Plataforma |
| **Fecha** | 2026-04-11 |
| **Branch** | `feature/US-4.3.3-casos-alternativos-performance` |

---

## Hallazgos relevantes del código actual

### 1. `RegistrarDNS` ya existe, pero no está expuesto por HTTP

- Handler disponible: `src/competencia/application/commands/registrar_dns.py`
- Falta exponer `POST /competencia/{id}/registrar-dns` en `src/competencia/api/router.py`
- El patrón puede reutilizar la misma estructura que `llamar`, `registrar-resultado` y `asignar-tarjeta`

### 2. La spec no coincide exactamente con el dominio para DNS

La spec dice que DNS puede registrarse desde `AnunciadaAP` o `Llamada`.

El dominio real hoy valida:

- `Performance.registrar_dns()` solo acepta estado `Llamada`
- si se intenta desde `AnunciadaAP`, el aggregate rechaza con `EstadoInvalidoParaRegistrarDNS`

Conclusión:

- para esta US no conviene prometer DNS desde Paso 1 si no se cambia dominio;
- el comportamiento implementable sin tocar reglas del aggregate es DNS desde Paso 2
  o desde un Paso 1 que primero haga `llamar` y luego `registrar-dns`.

### 3. La spec tampoco coincide con el modelo real de penalizaciones

La spec habla de `tarjeta = Blanca` con `penalizaciones > 0`.

El dominio real usa:

- `TipoTarjeta.BlancaConPenalizaciones`
- `penalizaciones: tuple[PenalizacionTecnica, ...]`
- cada penalización trae `{ tipo, deduccion }`

Además:

- `TarjetaAsignacion` rechaza penalizaciones cuando `tipo != BlancaConPenalizaciones`
- `AsignarTarjetaHandler` solo admite esa variante para disciplinas dinámicas:
  `DNF`, `DYN`, `DBF`

Conclusión:

- la UI debe mapear “Tarjeta blanca con penalizaciones” a `BlancaConPenalizaciones`;
- la validación de disciplinas permitidas debe seguir el código real (`DNF`, `DYN`, `DBF`),
  no la lista textual de la spec.

### 4. Los códigos reales de `MotivoDQ` difieren de la spec

Enum real en `src/competencia/domain/value_objects/motivo_dq.py`:

- `BKO_SUPERFICIE`
- `BKO_SUBACUATICO`
- `PROTOCOLO_SUPERFICIE`
- `INFRACCION_TECNICA_DQ`
- `NO_INICIO_EN_VENTANA`
- `SALIDA_EN_FALSO`

La spec menciona variantes textuales distintas (`NO_PROTOCOLO`, `INFRACCION_TECNICA`, etc.).

Conclusión:

- la UI debe presentar labels en español, pero postear los códigos del enum real.

### 5. BKO requiere distancia obligatoria en dominio

`TarjetaAsignacion` exige:

- `motivo_dq` obligatorio para `Roja`
- `distancia_blackout > 0` obligatoria para `BKO_SUPERFICIE` y `BKO_SUBACUATICO`

Esto alinea bien con la UX planteada para S-12.

### 6. La grilla actual todavía no muestra RP final penalizado

`GET /competencia/{id}/grilla` hoy entrega:

- nombre sintético
- AP
- unidad
- estado

No entrega:

- `rp_medido`
- `rp_penalizado`

Conclusión:

- si la US requiere ver el RP final penalizado en grilla, habrá que enriquecer la query;
- si no, alcanza con cerrar el flujo y volver a grilla con estado final.

---

## Decisión para seguir

La implementación de `US-4.3.3` debe alinearse al backend real:

1. agregar `POST /registrar-dns`;
2. UI para DNS, BKO y tarjeta roja con `MotivoDQ` real;
3. UI de penalizaciones mapeando a `BlancaConPenalizaciones`;
4. restringir penalizaciones a `DNF`, `DYN`, `DBF`;
5. tratar como discrepancia de spec el caso “DNS desde Paso 1” si no se modifica dominio.

---

*Generado: 2026-04-11 — Fase 0 US-4.3.3*
