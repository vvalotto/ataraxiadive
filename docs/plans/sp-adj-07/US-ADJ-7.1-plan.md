# Plan de Implementación: US-ADJ-7.1 — Corregir resultado tras DNS

| Campo | Valor |
|-------|-------|
| **Sprint** | SP-ADJ-07 |
| **Tipo** | Fix de dominio |
| **Branch** | `feature/US-ADJ-7.1-corregir-dns` |
| **BC** | `competencia` |
| **Estimación** | 2-3 h |
| **Estado** | Completado |
| **Fecha completado** | 2026-04-19 |

---

## Alcance

Agregar una transición explícita `DNS -> ResultadoRegistrado` para corregir un DNS
registrado por error, sin modificar el flujo normal `ResultadoRegistrado -> Ejecutada`.

La política P-08 no se dispara desde este comando. La finalización seguirá ocurriendo
desde `AsignarTarjetaHandler` o `RegistrarDNSHandler`.

---

## Decisiones de implementación

- Mantener endpoint bajo el prefijo real del router: `/competencia/...` (singular).
- Usar `participante_id` en el body, consistente con el resto de endpoints actuales;
  aceptar alias `atleta_id` como compatibilidad con la spec si no agrega ruido.
- Reutilizar `_handler_utils` para stream ID, carga, reconstitución y persistencia.
- Validar estado y motivo en el aggregate, no en el handler.
- Validar `valor_rp >= 0` en el aggregate antes de emitir evento.

---

## Tareas

### 1. Dominio

- [x] Crear `src/competencia/domain/events/resultado_corregido_tras_dns.py`
  - Evento `ResultadoCorregidoTrasDNS`.
  - Payload: `performance_id`, `participante_id`, `disciplina`, `valor_rp`,
    `unidad`, `registrado_por`, `motivo_correccion`, `corregido_en`.

- [x] Modificar `src/competencia/domain/aggregates/performance_events.py`
  - Importar el evento.
  - Agregar factory `crear_resultado_corregido_tras_dns()`.

- [x] Modificar `src/competencia/domain/exceptions.py`
  - Agregar `EstadoInvalidoParaCorregirResultadoTrasDNS`.
  - Reutilizar `MotivoObligatorio` para motivo vacío.

- [x] Modificar `src/competencia/domain/aggregates/performance.py`
  - Importar evento/factory y excepción.
  - Agregar `corregir_resultado_tras_dns(valor_rp, unidad, registrado_por, motivo_correccion)`.
  - Permitir solo desde `EstadoPerformance.DNS`.
  - Validar `motivo_correccion.strip()`.
  - Validar `valor_rp >= 0`.
  - Setear `_rp`, `_rp_medido`, `_rp_penalizado=None`, `_estado=ResultadoRegistrado`.

- [x] Modificar `src/competencia/domain/aggregates/performance_state.py`
  - Registrar handler de replay para `ResultadoCorregidoTrasDNS`.
  - Aplicar RP medido y estado `ResultadoRegistrado`.

### 2. Application

- [x] Crear `src/competencia/application/commands/corregir_resultado_tras_dns.py`
  - `CorregirResultadoTrasDNSCommand`.
  - `CorregirResultadoTrasDNSHandler`.
  - Carga stream, reconstituye aggregate, ejecuta comando de dominio y persiste evento.

### 3. API

- [x] Modificar `src/competencia/api/router.py`
  - Agregar body `CorregirResultadoTrasDNSBody`.
  - Agregar dependency del handler.
  - Agregar endpoint:
    `POST /competencia/{competencia_id}/performances/{performance_id}/corregir-resultado-tras-dns`
  - Retornar `204`.
  - Mapear `PerformanceNoEncontrada` a `404` y `DomainError` a `409`.

### 4. Tests

- [x] Unit dominio: `tests/unit/competencia/domain/test_performance_corregir_dns.py`
  - Corrige DNS y deja `ResultadoRegistrado`.
  - Emite `ResultadoCorregidoTrasDNS`.
  - Rechaza desde `Ejecutada`.
  - Rechaza desde `Llamada`.
  - Rechaza motivo vacío.
  - Replay reconstruye `ResultadoRegistrado`.

- [x] Unit application: handler persiste evento y no persiste en estado inválido.

- [x] Integración: `tests/integration/competencia/test_corregir_resultado_tras_dns_integration.py`
  - Flujo AP → llamada → DNS → corrección → tarjeta blanca.
  - Verificar orden `ResultadoCorregidoTrasDNS`, `TarjetaAsignada`.

- [x] API: endpoint retorna `204` y agrega evento; caso estado inválido retorna `409`.

- [x] BDD: `tests/features/steps/corregir_resultado_tras_dns_steps.py`
  - Cablear `US-ADJ-7.1-corregir-resultado-tras-dns.feature`.
  - Validar corrección, rechazos y flujo hasta tarjeta blanca.

### 5. Quality gates y documentación

- [x] Ejecutar tests focalizados.
- [x] Ejecutar `codeguard` sobre componentes modificados/agregados por la US.
- [x] Generar evidencia `US-ADJ-7.1-codeguard-raw.json`, `US-ADJ-7.1-coverage.json`
  y `US-ADJ-7.1-quality.json`.
- [x] Actualizar `docs/specs/sp-adj-07/US-ADJ-7.1.md` a `Implementada`.
- [x] Actualizar checklist en `PLAN-SP-ADJ-07`.
- [x] Generar `docs/reports/US-ADJ-7.1-report.md`.

---

## Métricas de Tiempo

| Fase | Real |
|------|------|
| Validación de contexto | 32s |
| BDD | 87s |
| Plan | 185s |
| Implementación | 1044s |
| Tests unitarios | 18s |
| Tests integración | 5s |
| Validación BDD | 4s |
| Quality gates | 9s tracker + rerun acotado |
| Documentación | 7s tracker + ajuste posterior |
| Reporte final | 6s tracker + ajuste posterior |
| **Total tracker** | **1649s** |

## Lecciones Aprendidas

- El feature BDD puede existir sin estar ejecutable si falta el módulo de steps con
  `scenarios(...)`; la Fase 6 debe verificar colección real de pytest-bdd.
- CodeGuard de US debe ejecutarse sobre componentes modificados/agregados, no sobre
  todo el BC, para evitar ruido de deuda previa.
- La cobertura total de `domain+application` sigue reflejando deuda histórica del BC;
  para esta US se documenta también el alcance por archivos tocados.

---

## Riesgos

- `Performance` ya está cerca de umbrales de diseño. Evitar duplicar lógica: la transición
  debe ser pequeña y el handler debe reutilizar helpers existentes.
- No disparar P-08 desde este comando. Si se dispara antes de `AsignarTarjeta`, la disciplina
  podría finalizar con performances todavía sin tarjeta.
- La spec menciona `/competencias` plural, pero el router real usa `/competencia`.

---

## Validación mínima esperada

```bash
pytest tests/unit/competencia/domain/test_performance_corregir_dns.py
pytest tests/unit/competencia/application/test_corregir_resultado_tras_dns_handler.py
pytest tests/integration/competencia/test_corregir_resultado_tras_dns_integration.py
pytest tests/features/steps/corregir_resultado_tras_dns_steps.py
```

---

*Creado: 2026-04-19 — Fase 2 para BUG-SP4-003*
