# Event Storming — Big Picture
## Dominio: Gestión de Torneos de Apnea

| Campo | Valor |
|-------|-------|
| **Documento** | event-storming-big-picture.md |
| **Tipo ES** | Big Picture — Nivel 1 |
| **Capa IEDD** | Entre Capa 1 (Dominio) y Capa 2 (Modelo DDD) |
| **Fecha** | 2026-03-17 |
| **Modalidad** | Solo-asincrónica — Victor Valotto (experto dominio) + Claude (facilitador) |
| **Estado** | ✅ Completo — 6 hot spots pendientes de resolución futura |

---

## Convención de Notación

| Símbolo | Significado |
|---------|-------------|
| 🟠 | Evento de dominio (algo que ocurrió — pasado) |
| 🔵 | Comando (acción que dispara el evento) |
| 🟡 | Actor (quien ejecuta el comando) |
| 🟣 | Política (regla automática: "cuando X → entonces Y") |
| 🔴 | Hot Spot (duda, ambigüedad, conflicto a resolver) |
| 🟢 | Read Model (información que el actor necesita para decidir) |

---

## Alcance

Dominio completo — las 6 fases del ciclo de vida de un torneo de apnea:

```
Apertura → Inscripción → Preparación → Ejecución → Premiación → Cierre
```

Objetivo: identificar todos los eventos de dominio significativos y las fronteras
naturales de Bounded Contexts desde el comportamiento del dominio, sin asumir
BCs previos.

---

## Fase 1 — Apertura del Torneo

> Estado: ✅ Validada (hot spots abiertos)

### Línea de Eventos

```
🔵 CrearTorneo           🔵 SeleccionarDisciplinas    🔵 HabilitarInscripcion
🟡 Organizador           🟡 Organizador               🟡 Organizador
        ↓                         ↓                          ↓
🟠 TorneoCreado     →   🟠 DisciplinasSeleccionadas  →  🟠 InscripcionHabilitada
```

### Datos significativos por evento

| Evento | Datos que transporta |
|--------|---------------------|
| `TorneoCreado` | nombre, ciudad, fecha inicio, fecha fin, entidad organizadora |
| `DisciplinasSeleccionadas` | lista de disciplinas (STA, DNF, DYN, DYNB, SPE2X50...) |
| `InscripcionHabilitada` | fecha inicio inscripción, fecha fin inscripción |

### Hot Spots

| ID | Descripción | Estado |
|----|-------------|--------|
| 🔴 HS-01 | ¿`CrearTorneo` y `SeleccionarDisciplinas` son un solo comando o dos? ¿El torneo puede crearse sin disciplinas y agregarlas después? | ✅ Son dos comandos separados — el torneo se crea primero y las disciplinas se agregan después |
| 🔴 HS-02 | RF-GT-07: ¿La entidad organizadora (federación/club) se registra al crear el torneo o es configuración previa del sistema? | ⏳ Pendiente |
| 🔴 HS-03 | RF-GT-03: ¿Hay restricción sobre cuántos torneos activos puede tener un mismo organizador? | ✅ Solo un torneo activo por organizador |

---

## Fase 2 — Inscripción de Atletas

> Estado: ✅ Validada (hot spots resueltos)

### Línea de Eventos

```
🔵 RegistrarAtleta / VerificarAtleta    🔵 InscribirseEnTorneo      🔵 CancelarInscripcion
🟡 Atleta                               🟡 Atleta                   🟡 Atleta
        ↓                                       ↓                          ↓
🟠 AtletaRegistrado         →       🟠 AtletaInscripto         →  🟠 InscripcionCancelada
```

### Datos significativos por evento

| Evento | Datos que transporta |
|--------|---------------------|
| `AtletaRegistrado` | nombre, apellido, mail, fecha nac., género, doc., teléfono, brevet |
| `AtletaInscripto` | atleta, torneo, categoría, disciplinas seleccionadas, constancia de pago, apto médico |
| `InscripcionCancelada` | atleta, torneo, motivo |

### Políticas

| Política | Descripción |
|----------|-------------|
| 🟣 P-01 | Cuando un atleta no registra AP antes del cierre → no compite (se materializa en Fase 3) |
| 🟣 P-02 | Cuando la fecha fin de inscripción se alcanza → sistema dispara `InscripcionCerrada` automáticamente |
| 🟣 P-03 | Cuando el organizador ejecuta `CerrarInscripcion` → `InscripcionCerrada` (cierre manual anticipado) |

### Hot Spots

| ID | Descripción | Estado |
|----|-------------|--------|
| 🔴 HS-04 | Atleta nuevo (carga todos los datos) vs. existente en BD FAAS (verifica y corrige). ¿Dos comandos o variantes del mismo flujo? | ✅ MVP: sin integración BD FAAS — el atleta siempre carga sus datos. Un solo comando `RegistrarAtleta`. |
| 🔴 HS-05 | RF-IN-07 pendiente: ¿qué pasa si los datos del atleta difieren de la BD FAAS? | ✅ No aplica MVP — integración FAAS fuera de alcance v1 |
| 🔴 HS-06 | ¿`InscripcionCerrada` la dispara el sistema al llegar la fecha fin, el organizador manualmente, o ambos? | ✅ Ambos: el sistema cierra automáticamente al llegar la fecha fin, y el organizador puede cerrarla manualmente antes. |
| 🔴 HS-07 | RF-IN-04: cancelación hasta el día anterior a la competencia. ¿Al torneo completo o a una disciplina puntual? | ✅ Al torneo completo, hasta el día anterior al torneo. |

---

## Fase 3 — Preparación de Competencias

> Estado: ✅ Validada (hot spots parcialmente resueltos)

### Línea de Eventos

```
🔵 RegistrarAP           🔵 CerrarPlazoAP        🔵 GenerarGrilla       🔵 AjustarGrilla
🟡 Atleta                🟡 Sistema               🟡 Sistema/Org         🟡 Organizador
       ↓                        ↓                        ↓                      ↓
🟠 APRegistrado    →  🟠 PlazoAPVencido    →  🟠 GrillaDeSalida  →  🟠 GrillaDeSalida
                                                   Generada               Ajustada
```

### Datos significativos por evento

| Evento | Datos que transporta |
|--------|---------------------|
| `APRegistrado` | atleta, disciplina, valor AP, unidad (metros/segundos según disciplina) |
| `PlazoAPVencido` | competencia, disciplina, lista de atletas sin AP → estado NoCompite |
| `GrillaDeSalidaGenerada` | disciplina, lista ordenada [atleta, posición, andarivel, OT calculado] |
| `GrillaDeSalidaAjustada` | disciplina, cambios manuales sobre la grilla generada |

### Políticas

| Política | Descripción |
|----------|-------------|
| 🟣 P-04 | Cuando `PlazoAPVencido` → atletas sin AP quedan en estado NoCompite (no compiten) |
| 🟣 P-05 | Orden de grilla: disciplinas de distancia (DNF, DYN, DYNB) → menor a mayor AP; disciplinas de tiempo (STA) → mayor a menor AP |
| 🟣 P-06 | Asignación de andariveles → automática por el sistema al generar la grilla |

### Hot Spots

| ID | Descripción | Estado |
|----|-------------|--------|
| 🔴 HS-08 | ¿`RegistrarAP` es por disciplina o por torneo? | ✅ Por disciplina — un atleta registra un AP distinto para cada disciplina en la que está inscripto |
| 🔴 HS-09 | ¿Cuándo vence el plazo de AP? ¿Configurado o manual? | ✅ El organizador configura una fecha/hora de cierre de anuncios al crear la competencia; el sistema dispara `PlazoAPVencido` automáticamente |
| 🔴 HS-10 | ¿La grilla puede regenerarse después de un cambio (AP cancelado, etc.) o solo ajuste manual? | ⏳ Pendiente — requiere mayor especificación |
| 🔴 HS-11 | ¿Cómo se distribuyen los atletas entre andariveles? | ✅ Asignación automática por el sistema |
| 🔴 HS-12 | El intervalo entre OTs (RF-PR-08): ¿lo configura el juez antes o después de la grilla? ¿Evento separado? | ⏳ Pendiente — requiere mayor especificación |

---

## Fase 4 — Ejecución de Competencias

> Estado: ✅ Validada (hot spots parcialmente resueltos)

### Línea de Eventos — Nivel 1: Competencia

```
🔵 IniciarCompetencia
🟡 Juez/Organizador
       ↓
🟠 CompetenciaIniciada
       ↓
🟣 P-07: CompetenciaIniciada → habilita ejecución secuencial de N Performances (según grilla)
```

### Línea de Eventos — Nivel 2: Performance (N veces, una por atleta según grilla)

```
🔵 LlamarAtleta     [zona v2+: HS-18]     🔵 RegistrarResultado    🔵 AsignarTarjeta
🟡 Sistema (grilla)  🔴                    🟡 Juez                  🟡 Juez
       ↓                  ↓                        ↓                       ↓
🟠 AtletaLlamado → · · · · · · · · · → 🟠 ResultadoRegistrado → 🟠 TarjetaAsignada
                   (dominio ocurre            (v1: el juez registra          (blanca/amarilla/roja)
                    fuera del sistema v1)      lo que observó)
```

Variante DNS:
```
🟠 AtletaLlamado → [no se presenta] → 🟠 DNSRegistrado
```

Cierre:
```
🟣 P-08: Cuando todas las Performances completadas (ResultadoRegistrado o DNSRegistrado) →
         sistema dispara CompetenciaFinalizada
🟠 CompetenciaFinalizada
```

### Datos significativos por evento

| Evento | Datos que transporta |
|--------|---------------------|
| `CompetenciaIniciada` | disciplina, cantidad de performances, juez asignado |
| `AtletaLlamado` | atleta, disciplina, posición en grilla, OT programado |
| `DNSRegistrado` | atleta, disciplina, OT programado |
| `ResultadoRegistrado` | atleta, disciplina, valor (metros con decimales ó tiempo), juez |
| `TarjetaAsignada` | atleta, disciplina, tipo (blanca/amarilla/roja), motivo si aplica |
| `CompetenciaFinalizada` | disciplina, performances completadas, DNS |

### Políticas

| Política | Descripción |
|----------|-------------|
| 🟣 P-07 | Cuando `CompetenciaIniciada` → habilita ejecución secuencial de N Performances según grilla |
| 🟣 P-08 | Cuando todas las Performances completadas → sistema dispara `CompetenciaFinalizada` |
| 🟣 P-09 | Cuando `DNSRegistrado` → descalificación automática, sin espera (RF-EJ-02) |

### Hot Spots

| ID | Descripción | Estado |
|----|-------------|--------|
| 🔴 HS-13 | ¿`IniciarCompetencia` y `LlamarAtleta` son eventos distintos, o llamar al primer atleta implícitamente inicia la competencia? | ✅ Son eventos distintos |
| 🔴 HS-14 | ¿`RegistrarResultado` y `AsignarTarjeta` son un solo comando o dos pasos secuenciales? | ✅ Son dos pasos secuenciales e independientes |
| 🔴 HS-15 | RF-EJ-06: corrección de resultado — ¿genera `ResultadoCorregido` (nuevo evento) o reemplaza el anterior? | ✅ Genera nuevo evento `ResultadoCorregido` |
| 🔴 HS-16 | RF-EJ-01: múltiples jueces — ¿el sistema registra qué juez asignó cada tarjeta o solo el resultado final? | ✅ El sistema registra el juez que asignó cada tarjeta |
| 🔴 HS-17 | RF-GT-05: ¿se puede volver de Ejecución a Preparación? ¿Qué eventos lo modelan? | ✅ No se puede volver — la transición es unidireccional (v1) |
| 🔴 HS-18 | **Zona v2+:** entre `AtletaLlamado` y `ResultadoRegistrado` existen eventos intermedios fuera del alcance v1. Candidatos para v2: `PerformanceIniciada` (OT confirmado), `BlackoutRegistrado` (→ tarjeta roja automática), `ProtocoloSuperficieEvaluado`, `PerformanceSuspendida` (safety diver). | ✅ Documentado — fuera de alcance v1 |

---

## Fase 5 — Premiación

> Estado: ✅ Propuesta registrada (hot spots abiertos — pendiente validación)

### Línea de Eventos

```
🔵 CalcularResultados     🔵 PublicarResultados    🔵 EntregarPremios
🟡 Sistema                🟡 Organizador           🟡 Organizador
       ↓                         ↓                       ↓
🟠 ResultadosCalculados → 🟠 ResultadosPublicados → 🟠 PremiosEntregados
```

### Datos significativos por evento

| Evento | Datos que transporta |
|--------|---------------------|
| `ResultadosCalculados` | disciplina, ranking por categoría/género, Overall si aplica |
| `ResultadosPublicados` | torneo, disciplinas incluidas, URL/formato de publicación |
| `PremiosEntregados` | torneo, podios por disciplina/categoría |

### Políticas

| Política | Descripción |
|----------|-------------|
| 🟣 P-10 | Cuando todas las `CompetenciaFinalizada` del torneo → habilita `CalcularResultados` |
| 🟣 P-11 | Empate en una disciplina → mismo puesto y mismos puntos (RF-PM-03) |

### Hot Spots

| ID | Descripción | Estado |
|----|-------------|--------|
| 🔴 HS-19 | RF-PM-01: cálculo por puntos o por marca absoluta — pendiente de definir. ¿El evento `ResultadosCalculados` es suficiente sin resolver el algoritmo ahora? | ⏳ Pendiente |
| 🔴 HS-20 | RF-PM-02: Overall (ranking general multi-disciplina). ¿Es evento separado `OverallCalculado` o incluido en `ResultadosCalculados`? | ✅ Evento separado `OverallCalculado` — se dispara después de calcular todas las disciplinas |
| 🔴 HS-21 | ¿`PublicarResultados` es por disciplina (publicación incremental) o una sola publicación al cierre del torneo? | ✅ Por disciplina — publicación incremental a medida que cada competencia finaliza |
| 🔴 HS-22 | `PremiosEntregados`: ¿genera efectos en el sistema (certificado, notificación) o solo registro del hecho? | ⏳ Pendiente |

---

## Fase 6 — Cierre del Torneo

> Estado: ✅ Validada (hot spots abiertos)

### Línea de Eventos

```
🔵 CerrarTorneo
🟡 Organizador
       ↓
🟠 TorneoCerrado
```

Variante cancelación (puede ocurrir en cualquier fase anterior):
```
🔵 CancelarTorneo
🟡 Organizador
       ↓
🟠 TorneoCancelado   ← estado cancelado, datos preservados (RF-GT-04)
```

### Datos significativos por evento

| Evento | Datos que transporta |
|--------|---------------------|
| `TorneoCerrado` | torneo, fecha de cierre, resultados disponibles para descarga |
| `TorneoCancelado` | torneo, motivo, fase en la que se canceló |

### Políticas

| Política | Descripción |
|----------|-------------|
| 🟣 P-12 | Cuando `TorneoCerrado` → resultados quedan disponibles para descarga (RF-PM-06) |

### Hot Spots

| ID | Descripción | Estado |
|----|-------------|--------|
| 🔴 HS-23 | `CancelarTorneo` puede ocurrir en cualquier fase. ¿Hay restricciones? ¿Se puede cancelar con competencias ya ejecutadas? | ✅ Sí, se puede cancelar en cualquier fase incluso con competencias ejecutadas — datos siempre preservados |
| 🔴 HS-24 | RF-GT-05: vuelta de Ejecución a Preparación. ¿Se modela como evento `TorneoRevertidoAPreparacion` o es implícito en el estado? | ✅ No aplica v1 — consecuencia de HS-17: transición unidireccional |
| 🔴 HS-25 | ¿`TorneoCerrado` dispara notificaciones a atletas y jueces (RF-NT-04)? | ⏳ Pendiente |

---

## Resumen de Hot Spots Globales

| ID | Fase | Descripción | Estado |
|----|------|-------------|--------|
| HS-01 | Apertura | ¿`CrearTorneo` y `SeleccionarDisciplinas` son un solo comando o dos? | ✅ Dos comandos separados |
| HS-02 | Apertura | ¿La entidad organizadora se registra al crear el torneo o es config previa? | ⏳ Pendiente |
| HS-03 | Apertura | ¿Cuántos torneos activos puede tener un organizador? | ✅ Solo uno |
| HS-04 | Inscripción | Atleta nuevo vs. existente en BD FAAS — ¿dos comandos? | ✅ MVP: un solo `RegistrarAtleta` |
| HS-05 | Inscripción | ¿Qué pasa si datos difieren de BD FAAS? | ✅ No aplica v1 |
| HS-06 | Inscripción | ¿Quién dispara `InscripcionCerrada`? | ✅ Sistema (automático) y organizador (manual) |
| HS-07 | Inscripción | ¿Cancelación al torneo completo o por disciplina? | ✅ Al torneo completo, hasta el día anterior |
| HS-08 | Preparación | ¿AP es por disciplina o por torneo? | ✅ Por disciplina |
| HS-09 | Preparación | ¿Cuándo vence el plazo de AP? | ✅ Fecha/hora configurada por el organizador |
| HS-10 | Preparación | ¿La grilla puede regenerarse o solo ajuste manual? | ⏳ Pendiente |
| HS-11 | Preparación | ¿Asignación de andariveles automática o manual? | ✅ Automática |
| HS-12 | Preparación | Intervalo entre OTs: ¿antes o después de la grilla? ¿Evento separado? | ⏳ Pendiente |
| HS-13 | Ejecución | ¿`IniciarCompetencia` y `LlamarAtleta` son eventos distintos? | ✅ Distintos |
| HS-14 | Ejecución | ¿`RegistrarResultado` y `AsignarTarjeta` son un paso o dos? | ✅ Dos pasos secuenciales |
| HS-15 | Ejecución | Corrección de resultado: ¿nuevo evento o reemplazo? | ✅ Nuevo evento `ResultadoCorregido` |
| HS-16 | Ejecución | ¿El sistema registra qué juez asignó cada tarjeta? | ✅ Sí |
| HS-17 | Ejecución | ¿Se puede volver de Ejecución a Preparación? | ✅ No — transición unidireccional v1 |
| HS-18 | Ejecución | Zona v2+: eventos intermedios entre `AtletaLlamado` y `ResultadoRegistrado` | ✅ Documentado — fuera de alcance v1 |
| HS-19 | Premiación | Cálculo por puntos o por marca absoluta | ⏳ Pendiente |
| HS-20 | Premiación | ¿Overall es evento separado o incluido en `ResultadosCalculados`? | ✅ Evento separado `OverallCalculado` |
| HS-21 | Premiación | ¿`PublicarResultados` por disciplina o al cierre del torneo? | ✅ Por disciplina — publicación incremental |
| HS-22 | Premiación | `PremiosEntregados`: ¿genera certificado/notificación o solo registro? | ⏳ Pendiente |
| HS-23 | Cierre | ¿Se puede cancelar con competencias ya ejecutadas? | ✅ Sí — datos siempre preservados |
| HS-24 | Cierre | Vuelta de Ejecución a Preparación: ¿evento explícito? | ✅ No aplica v1 — consecuencia de HS-17 |
| HS-25 | Cierre | ¿`TorneoCerrado` dispara notificaciones? | ⏳ Pendiente |

---

## Candidatos a Bounded Contexts

Los BCs emergen de los puntos donde el **lenguaje cambia** o hay una **frontera de
consistencia transaccional** natural en la línea de eventos.

| Candidato a BC | Tipo | Eventos que agrupa |
|---------------|------|--------------------|
| **Torneo** | Supporting | `TorneoCreado`, `DisciplinasSeleccionadas`, `InscripcionHabilitada`, `TorneoCerrado`, `TorneoCancelado` |
| **Registro** | Supporting | `AtletaRegistrado`, `AtletaInscripto`, `InscripcionCancelada`, `InscripcionCerrada` |
| **Competencia** | **Core Domain** | `APRegistrado`, `PlazoAPVencido`, `GrillaDeSalidaGenerada`, `GrillaDeSalidaAjustada`, `CompetenciaIniciada`, `AtletaLlamado`, `DNSRegistrado`, `ResultadoRegistrado`, `ResultadoCorregido`, `TarjetaAsignada`, `CompetenciaFinalizada` |
| **Resultados** | Supporting | `ResultadosCalculados`, `OverallCalculado`, `ResultadosPublicados`, `PremiosEntregados` |
| **Identidad** | Generic | Sin eventos explícitos en este ES — cross-cutting (usuarios, roles, autenticación) |
| **Notificaciones** | Generic | Sin eventos propios — disparado por políticas de otros BCs |

---

## Derivación: Eventos → Candidatos a BC

El cambio de lenguaje marca las fronteras naturales:

```
[Torneo]         TorneoCreado · DisciplinasSeleccionadas · InscripcionHabilitada
                     ↓
[Registro]       AtletaRegistrado · AtletaInscripto · InscripcionCancelada · InscripcionCerrada
                     ↓
 ── FRONTERA: el lenguaje cambia de "atleta inscripto" a "performance / AP / OT" ──
                     ↓
[Competencia]    APRegistrado · GrillaDeSalidaGenerada · CompetenciaIniciada ·
                 AtletaLlamado · ResultadoRegistrado · TarjetaAsignada · CompetenciaFinalizada
                     ↓
 ── FRONTERA: el lenguaje cambia de "performance ejecutada" a "ranking / podio" ──
                     ↓
[Resultados]     ResultadosCalculados · OverallCalculado · ResultadosPublicados · PremiosEntregados
                     ↓
[Torneo]         TorneoCerrado · TorneoCancelado
```

**Observaciones:**
- `Competencia` absorbe la Preparación (AP + grilla) porque el lenguaje ya es de
  competencia (AP, OT, andarivel) aunque el torneo aún no inició ejecución.
- `Torneo` aparece al inicio y al cierre — gestiona el ciclo de vida del contenedor,
  no la lógica de ejecución.
- Los 7 BCs preliminares de CLAUDE.md §7 se comprimen en 4+2 genéricos.
  `Configuración` no emergió como BC propio — sus conceptos (disciplinas, categorías,
  reglas de tarjetas) son datos de configuración de `Torneo` y `Competencia`.
  Esta diferencia es un dato experimental a documentar en la retrospectiva BL-000.

---

## Notas del Experimento

Esta sesión es de modalidad **solo-asincrónica**: Victor Valotto como único experto
del dominio, asistido por Claude como facilitador. La limitación de no contar con
un equipo presencial se compensa con la profundidad del dominio ya documentado en
`docs/dominio/` (5 archivos, cuestionario detallado con respuestas).

### Aprendizajes — sesión 2026-03-17

**1. Valor dual del ES**
El ES no fue solo una reorganización de los RFs existentes. Cumplió dos funciones
distintas: *confirmó* modelado que el experto ya tenía, *y* descubrió aspectos que
no habían sido pensados. Ambas funciones tienen valor experimental diferente: la
confirmación da confianza en el modelo; el descubrimiento mejora la especificación.

**2. Limitación del formato solo-asincrónico**
El experto de dominio quedó mayormente en rol reactivo (validar/aprobar propuestas
del facilitador) en vez del rol proactivo que caracteriza al ES presencial con equipo.
Esto no es un fallo del proceso sino un dato sobre la metodología: el ES solo-asincrónico
produce resultados válidos pero con menor riqueza exploratoria que el formato grupal.
A documentar en retrospectiva BL-000.

**3. ES produce modelos más simples y coherentes**
Los 7 BCs identificados preliminarmente en CLAUDE.md se redujeron a 4+2 genéricos.
La simplificación emergió naturalmente del comportamiento del dominio — `Configuración`
no apareció como BC propio. Un modelo más simple derivado del comportamiento es más
confiable que uno derivado de análisis estático de RFs.

**4. Los hot spots son información, no incompletitud**
Quedaron 6 hot spots sin resolver. Esto no indica que el ES quedó incompleto: indica
exactamente qué zonas necesitan más pensamiento antes de especificar. ES hace visible
la ambigüedad; eso solo ya tiene valor para IEDD.

**5. Respuesta preliminar a la hipótesis experimental**
> El ES entre Capa 1 y Capa 2 de IEDD vale porque ayuda a descubrir y entender
> mejor el dominio, y por lo tanto mejora la calidad de la especificación.

Esta es la primera evidencia empírica del experimento AtaraxiaDive. A contrastar
con los datos de SP1 cuando las US-IEDD derivadas de este modelo se implementen.

**Hipótesis a evaluar en retrospectiva BL-000:**
> Los BCs que emergen de este Big Picture ES son más coherentes que los 7 BCs
> identificados preliminarmente en CLAUDE.md. Las diferencias son un dato experimental.

**Referencia:** `docs/contexto/DECISION-EVENT-STORMING.md`

---

*Documento creado: 2026-03-17 — Semana 0, Fase 0*
*Mantenido por: Claude Cowork + Victor Valotto*
