# SP2 — La Competencia: Incrementos y US Candidatas

| Campo | Valor |
|-------|-------|
| **Subproyecto** | SP2 — La Competencia |
| **Baseline objetivo** | BL-002 |
| **BCs activos** | Competencia (completo — se agrega aggregate `Competencia`) + Resultados (núcleo) |
| **DoD del SP2** | Ejecutar una disciplina STA y una DNF completas con 10 atletas cada una, incluyendo DNS y black-outs. Mostrar el ranking final de cada una. |
| **Fecha** | 2026-03-24 |

---

## Resumen de Incrementos

| Inc. | Nombre | Tipo | US candidatas | DoD observable |
|------|--------|------|---------------|----------------|
| **2.1** | La grilla de salida | Domain (aggregate Competencia) | US-2.1.1 a US-2.1.4 | Juez avanza por la grilla atleta a atleta · grilla generada con orden correcto |
| **2.2** | Dos mecánicas, un modelo | Domain + API | US-2.2.1, US-2.2.2 | STA (tiempo) y DNF (distancia) funcionando · avance automático al siguiente atleta |
| **2.3** | Andariveles simultáneos | Domain + API | US-2.3.1 | 2-3 andariveles activos sin conflicto · performances en andariveles distintos |
| **2.4** | El ranking | Domain (BC Resultados) | US-2.4.1, US-2.4.2 | Ranking con podio generado automáticamente al cerrar disciplina |

---

## Deuda SOLID SP1→SP2 (alta prioridad — resolver en US-2.1.1)

| Deuda | Tipo | Prioridad | Descripción |
|-------|------|-----------|-------------|
| DIP en `router.py` | SOLID | Alta | El router instancia dependencias directamente en lugar de recibirlas por inyección |
| OCP en `_apply_stored` de `Performance` | SOLID | Media | Método con cadena if/elif que debe extenderse para nuevos eventos |

Ambas se resuelven dentro de US-2.1.1 (primer US del SP2) antes de agregar código nuevo.

---

## Incremento 2.1 — La Grilla de Salida

**Objetivo:** introducir el aggregate `Competencia` completo con su ciclo de vida hasta
`IniciarCompetencia`. Reemplaza el stub `CompetenciaEstadoPort` con la implementación real.

### US-2.1.1 — Scaffold Aggregate Competencia + ConfigurarIntervaloOT

| Campo | Valor |
|-------|-------|
| **Comando** | `ConfigurarIntervaloOT` |
| **Evento** | `IntervaloOTConfigurado` |
| **Actor** | Organizador / Juez |
| **Invariantes** | INV-C-01 |
| **ES candidata** | US-C-01 |
| **RFs** | RF-PR-08 |

**Precondiciones:**
- La Competencia existe y está en estado `Preparacion`
- No existe aún un intervalo configurado, o bien existe y se está reconfigurando

**Postcondición:** `IntervaloOTConfigurado` persiste en el stream `competencia-{id}`.
Competencia mantiene estado `Preparacion`.

**Invariante:**
- `INV-C-01`: `intervaloDisciplina` debe estar configurado antes de `GenerarGrilla`

**Incluye:** resolución de deuda SOLID (DIP en `router.py` + OCP en `_apply_stored`).

---

### US-2.1.2 — Generar / Regenerar Grilla

| Campo | Valor |
|-------|-------|
| **Comando** | `GenerarGrilla` / `RegenerarGrilla` |
| **Evento** | `GrillaDeSalidaGenerada` |
| **Actor** | Organizador / Sistema |
| **Invariantes** | INV-C-01, P-01, P-02 |
| **ES candidata** | US-C-02 |
| **RFs** | RF-PR-04, RF-PR-05 |

**Precondiciones:**
- `intervaloDisciplina` está configurado (INV-C-01)
- La grilla no está confirmada (`GrillaConfirmada` no emitido) — regeneración permitida

**Postcondición:** `GrillaDeSalidaGenerada` persiste. La lista ordenada de atletas con
posición, andarivel y OT calculado queda proyectada en el Read Model.

**Invariantes / Políticas:**
- `INV-C-01`: intervalo configurado antes de generar
- `P-01`: disciplinas de distancia → AP menor a mayor; tiempo → AP mayor a menor
- `P-02`: OT de cada atleta = OT_inicio + (posición × intervaloDisciplina)
- `RF-PR-04`: atletas sin AP no aparecen en la grilla
- Regeneración permitida mientras `GrillaConfirmada` no fue emitido

---

### US-2.1.3 — Ajustar Grilla

| Campo | Valor |
|-------|-------|
| **Comando** | `AjustarGrilla` |
| **Evento** | `GrillaDeSalidaAjustada` |
| **Actor** | Organizador |
| **Invariantes** | INV-C-02 (parcial) |
| **ES candidata** | US-C-03 |
| **RFs** | RF-PR-07 |

**Precondiciones:**
- La grilla fue generada (`GrillaDeSalidaGenerada` emitido)
- La grilla **no** está confirmada (INV-C-02 — parcial: antes de `GrillaConfirmada`)

**Postcondición:** `GrillaDeSalidaAjustada` persiste con los cambios de posición/andarivel.
Read Model actualizado.

**Invariantes:**
- `INV-C-02`: `AjustarGrilla` no permitido después de `GrillaConfirmada`

---

### US-2.1.4 — Confirmar Grilla + Iniciar Competencia

| Campo | Valor |
|-------|-------|
| **Comandos** | `ConfirmarGrilla` · `IniciarCompetencia` |
| **Eventos** | `GrillaConfirmada` · `CompetenciaIniciada` |
| **Actor** | Organizador (confirmar) · Juez (iniciar) |
| **Invariantes** | INV-C-02, INV-C-03 |
| **ES candidatas** | US-C-04, US-C-05 |

**ConfirmarGrilla:**
- Precondición: grilla generada (`GrillaDeSalidaGenerada`)
- Postcondición: `GrillaConfirmada` persiste. Grilla congelada — `GenerarGrilla`,
  `RegenerarGrilla` y `AjustarGrilla` bloqueados (INV-C-02 completo)

**IniciarCompetencia:**
- Precondición: Competencia en estado `Confirmada` (INV-C-03)
- Postcondición: `CompetenciaIniciada` persiste. Competencia en estado `EnEjecucion`.
  Performances habilitadas para ejecución según grilla (P-06)

**Incluye:** reemplazo del stub `CompetenciaEstadoPort` con la implementación real
que consulta el stream de Competencia para verificar `GrillaConfirmada` e `is_en_ejecucion`.

---

## Incremento 2.2 — Dos Mecánicas, un Modelo

**Objetivo:** soportar STA (tiempo en segundos) y DNF (distancia en metros con decimales)
como disciplinas con descriptor propio. El juez ve el campo correcto según la disciplina.

### US-2.2.1 — Descriptor de Disciplina

| Campo | Valor |
|-------|-------|
| **Tipo** | Value Object + Port |
| **Actor** | Sistema |
| **RFs** | RF-EJ-08 |

Value Object `DisciplinaDescriptor`: encapsula tipo de medición (tiempo / distancia),
unidad (`Segundos` / `Metros`), y regla de ordenamiento de grilla.

Introduce `DisciplinaDescriptorPort` en `domain/ports/` para que `GenerarGrilla` y
`RegistrarResultado` consulten el descriptor sin acoplarse a una implementación concreta.

---

### US-2.2.2 — API Disciplina-Aware + Avance Automático

| Campo | Valor |
|-------|-------|
| **Tipo** | Application + API |
| **Actor** | Juez |
| **RFs** | RF-EJ-08 |

- Endpoint `POST /competencia/{id}/performance/{pid}/resultado` valida la unidad
  según el descriptor de la disciplina
- Lógica de avance automático: al finalizar una performance, el sistema identifica
  la siguiente según posición en grilla (P-06)
- Read Model `PerformanceActual` incluye el descriptor de disciplina para que el
  cliente muestre el campo correcto

---

## Incremento 2.3 — Andariveles Simultáneos

**Objetivo:** la grilla distribuye atletas en 2-3 andariveles. Performances en andariveles
distintos pueden registrarse sin conflicto.

### US-2.3.1 — Ejecución Multi-Andarivel

| Campo | Valor |
|-------|-------|
| **Comandos** | `GenerarGrilla` (extendido) · `LlamarAtleta` (multi-lane) |
| **Actor** | Sistema / Juez |
| **RFs** | RF-PR-06 |

- `GenerarGrilla` distribuye atletas en N andariveles (configurable, default=1)
- El aggregate garantiza que no hay dos performances activas (en estado `Llamada`)
  en el mismo andarivel simultáneamente
- Read Model `AndarivelesActivos`: lista de andariveles con el atleta actual de cada uno
- Endpoint `GET /competencia/{id}/andariveles` muestra estado de cada andarivel

---

## Incremento 2.4 — El Ranking

**Objetivo:** al finalizar la disciplina, el ranking se calcula automáticamente y es
visible con podio destacado.

### US-2.4.1 — Competencia Finalizada (automático)

| Campo | Valor |
|-------|-------|
| **Evento** | `CompetenciaFinalizada` |
| **Actor** | Sistema (automático) |
| **Invariantes** | INV-C-04, P-08 |
| **ES candidata** | US-C-06 |

Política P-08: cuando todas las Performances están en estado `Ejecutada` o `DNS`,
el sistema emite `CompetenciaFinalizada` automáticamente.

- `INV-C-04`: solo se finaliza cuando **todas** las Performances = Ejecutada o DNS
- `CompetenciaFinalizada` dispara el cálculo del ranking en BC Resultados

---

### US-2.4.2 — Calcular Ranking (BC Resultados — núcleo)

| Campo | Valor |
|-------|-------|
| **Comando** | `CalcularRanking` |
| **Actor** | Sistema (disparo desde `CompetenciaFinalizada`) |
| **RFs** | RF-PM-03 |
| **BC** | Resultados (primer US del BC) |

- Ranking ordenado: mejor marca primero (según descriptor de disciplina)
- DNS y tarjeta roja al final, después de las performances válidas
- Empates comparten posición (RF-PM-03) — misma posición y mismos puntos
- Read Model `RankingDisciplina`: lista con posición, atleta, marca, tarjeta, podio destacado
- Endpoint `GET /competencia/{id}/ranking`

**Nota SP2:** BC Resultados se inicializa en este incremento. Solo se crea el scaffold
mínimo necesario (equivalente a Inc 1.1 pero para BC Resultados).

---

## Mapping US Candidatas → ES Competencia

| US SP2 | US ES (event-storming-competencia.md) | Incremento |
|--------|---------------------------------------|-----------|
| US-2.1.1 | US-C-01 (ConfigurarIntervaloOT) | Inc 2.1 |
| US-2.1.2 | US-C-02 (GenerarGrilla) | Inc 2.1 |
| US-2.1.3 | US-C-03 (AjustarGrilla) | Inc 2.1 |
| US-2.1.4 | US-C-04 + US-C-05 (ConfirmarGrilla + IniciarCompetencia) | Inc 2.1 |
| US-2.2.1 | — (DisciplinaDescriptor — value object) | Inc 2.2 |
| US-2.2.2 | — (API disciplina-aware + avance automático) | Inc 2.2 |
| US-2.3.1 | US-C-02 extendido (multi-andarivel) | Inc 2.3 |
| US-2.4.1 | US-C-06 (CompetenciaFinalizada automático) | Inc 2.4 |
| US-2.4.2 | — (CalcularRanking — BC Resultados núcleo) | Inc 2.4 |

**US del ES Competencia pendientes para SPs posteriores:**
- US-P-06 (CorregirResultado con INV-P-15): ventana de impugnación → SP3 (BC Torneo)

---

## Datos Hardcodeados en SP2

SP2 opera sin BC Registro, BC Torneo ni BC Identidad.

| Dato | Fuente real | En SP2 |
|------|------------|--------|
| Datos del atleta (nombre, categoría) | BC Registro | String + ID fijo en los tests / seed data |
| `torneoId` | BC Torneo | UUID fijo |
| `ventanaImpugnacion` | BC Torneo | Sin validación (INV-P-15 diferido a SP3) |
| Roles (organizador / juez) | BC Identidad | Sin autenticación — comandos aceptan `actorId` string |
| Descriptores de disciplina | BC Configuración (SP4) | Hardcodeados: STA→Segundos, DNF→Metros |

---

## Próximos Pasos

1. ✅ Branch `feature/sp2-planificacion` creado desde `develop`
2. ✅ Este documento
3. Redactar `docs/specs/sp2/US-2.1.1.md` a `US-2.1.4.md` — primer incremento completo
4. Crear issues en Linear: 4 incrementos + sub-issues US Inc 2.1
5. Actualizar `docs/traceability/matrix.md` con US-IEDD SP2
6. PR `feature/sp2-planificacion` → `develop`
7. Al iniciar Inc 2.1: `git checkout -b feature/US-2.1.1-competencia-intervalo-ot develop`
