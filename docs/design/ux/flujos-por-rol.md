# Flujos por Rol — AtaraxiaDive SP4

> Artefacto INC-4.0 · Fuente: prototipo validado + Reglamento CMAS 2022/01 (FAAS)
> Última actualización: 2026-04-05

---

## 1. Rol: Juez

**Contexto de uso:** pileta, manos mojadas, luz solar directa, operación bajo presión de tiempo.
**Dispositivo:** smartphone (mobile-first, orientación vertical).
**Restricción crítica:** ≤ 6 toques por performance, botones ≥ 58 px.

### 1.1 Flujo principal — Performance completa

```
[Login]
  └── Email + contraseña → INGRESAR
        │
[Mis Disciplinas]
  └── Lista de disciplinas asignadas (DNF / STA / DBF / DYN)
      ├── ACTIVA  → tap → Grilla de Salida
      └── PENDIENTE → no habilitada aún
            │
[Grilla de Salida]
  └── Lista ordenada por OT ascendente
      ├── ✓ BLANCA / ROJA / DNS  → no tappable (ya ejecutó)
      ├── ⚠ REVISIÓN             → tappable → pantalla de resolución
      ├── ▶ SIGUIENTE            → tappable (primer pendiente, resaltado)
      └── PENDIENTE              → tappable (siguientes)
            │
[Paso 1 — Llamar atleta]
  ├── LLAMAR ATLETA → Paso 2
  └── DNS — No se presenta → pantalla DNS
            │
[Paso 2 — Confirmar presencia]
  ├── PRESENTE → Paso 3
  └── DNS — No se presenta → pantalla DNS
            │
[Paso 3 — Tiempo Oficial]
  Estado A: muestra OT programado + botón "⏱ TIEMPO OFICIAL"
  └── Juez presiona en el momento exacto del OT
        │
  Estado B: ventana +30s activa (countdown 30→0)
  ├── Verde 30s–11s · Amarillo 10s–6s · Rojo 5s–1s
  ├── ▶ ATLETA INICIA (juez presiona cuando ve al atleta sumergirse) → Paso 4
  └── Si 0s: ventana vencida → REGISTRAR DQ (no inició en ventana) → resultado Roja
            │
[Paso 4 — Performance en curso]
  └── Cronómetro activo desde ATLETA INICIA
      ├── ⏹ FINALIZAR PERFORMANCE → Paso 5
      └── ⚡ BKO — Black-out → pantalla BKO
            │
[Paso 5 — Registrar RP]
  └── Selector metros + cm:
      presets (25/50/75/100/125) + ajuste (−1/+1/+5/+10 m) + numpad cm
      └── CONFIRMAR MARCA → Paso 6
            │
[Paso 6 — Asignar tarjeta]
  ├── ⬜ TARJETA BLANCA   → resultado Blanca → SIGUIENTE ATLETA
  ├── 🟨 TARJETA AMARILLA → resultado Amarilla (en revisión)
  └── 🟥 TARJETA ROJA     → resultado Roja → SIGUIENTE ATLETA
```

### 1.2 Flujos alternativos

#### DNS — Did Not Start
```
[Paso 1 o Paso 2]
  └── DNS — No se presenta
        └── Confirmación → CONFIRMAR DNS → resultado DNS → SIGUIENTE ATLETA
```

#### BKO — Black-out
```
[Paso 4 — En curso]
  └── ⚡ BKO
        └── Distancia alcanzada (metros + cm, obligatorio)
              └── CONFIRMAR BKO — TARJETA ROJA → resultado Roja
```
> Regla CMAS 1.1.10.3: BKO bajo el agua = tarjeta roja automática. Campo distancia obligatorio.

#### Tarjeta Amarilla — Resolución
```
[Resultado Amarilla]  o  [Grilla → fila ⚠ REVISIÓN]
  └── Deliberación judges (máx 3 minutos — CMAS 1.2.3.1)
      ├── ⬜ RESOLVER → BLANCA  (con eventual penalización −3m)
      └── 🟥 RESOLVER → ROJA
```

#### DQ — No inició en ventana OT+30s
```
[Paso 3 — ventana vencida]
  └── REGISTRAR DQ — No inició en ventana → resultado Roja
```
> Diferente al DNS: atleta presente pero no sumergió vías respiratorias antes de OT+30s (CMAS 1.2.1.8).

### 1.3 Flujo offline
```
[Cualquier pantalla de performance]
  └── Pérdida de conexión → badge "Sin conexión" (rojo, parpadeante)
      └── Acciones se encolan localmente (Dexie.js)
            └── Al reconectar → sincronización automática en background
```

---

## 2. Rol: Organizador

**Contexto de uso:** escritorio o tablet, antes y durante el torneo.
**Dispositivo:** desktop-first (tablet compatible).

### 2.1 Flujo principal — Gestión del torneo

```
[Login]
  └── Email + contraseña → rol Organizador → Panel principal
        │
[Panel principal]
  ├── Torneos activos
  ├── Alertas pendientes (amarillas sin resolver, etc.)
  └── Accesos rápidos
        │
        ├── [Gestión de Torneo]
        │     ├── Crear / editar torneo (nombre, fecha, sede, disciplinas)
        │     ├── Configurar disciplinas (DNF, STA, DBF, DYN, SPE)
        │     └── Publicar / cerrar torneo
        │
        ├── [Gestión de Grilla]
        │     ├── Ver grilla de salida por disciplina
        │     ├── Ajustar orden de salida
        │     ├── Modificar OT de atleta (con justificación)
        │     └── Exportar grilla (PDF)
        │
        ├── [Gestión de Jueces]
        │     ├── Asignar jueces a disciplinas / andariveles
        │     ├── Ver estado en tiempo real por disciplina
        │     └── Reasignar ante ausencia
        │
        ├── [Resultados en tiempo real]
        │     ├── Vista por disciplina (ranking parcial)
        │     ├── Overall ranking
        │     └── Publicar resultados oficiales
        │
        └── [Audit Log]
              ├── Historial de eventos por performance
              ├── Filtro por atleta / disciplina / juez
              └── Hash SHA-256 por registro (integridad)
```

### 2.2 Flujo — Resolución de incidencia
```
[Alertas]
  └── Tarjeta amarilla sin resolver → tap → detalle de la performance
        └── Ver video / consultar → Resolver (Blanca o Roja)
```

---

## 3. Rol: Atleta

**Contexto de uso:** pre-competencia y post-competencia, smartphone.
**Dispositivo:** mobile-first. Solo lectura durante la competencia.

### 3.1 Flujo principal

```
[Login]
  └── Email + contraseña → rol Atleta → Portal atleta
        │
[Portal atleta]
  ├── [Mis inscripciones]
  │     ├── Torneos disponibles → inscribirse
  │     ├── Mis inscripciones activas
  │     └── Cancelar inscripción (dentro del plazo)
  │
  ├── [Mis anuncios (AP)]
  │     ├── Ver disciplinas inscriptas
  │     ├── Ingresar / modificar AP por disciplina
  │     └── Confirmar anuncio (cierra cuando el organizador lo habilita)
  │
  ├── [Mi grilla]
  │     ├── OT asignado por disciplina
  │     ├── Andarivel
  │     └── Posición en la grilla
  │
  └── [Resultados]
        ├── Mi resultado por disciplina (RP, tarjeta)
        ├── Ranking de disciplina
        └── Ranking Overall
```

### 3.2 Restricciones de acceso
- El atleta **no puede modificar** el AP una vez que el organizador cierra el período de anuncios.
- Durante la ejecución de su performance: solo lectura.
- Los resultados son visibles una vez que el organizador los publica.

---

## 4. Navegación entre roles

Un usuario puede tener múltiples roles (ej: juez + atleta). En ese caso:

```
[Login]
  └── Si tiene múltiples roles → pantalla de selección de rol activo
        ├── Juez   → interfaz del juez
        ├── Atleta → portal del atleta
        └── Organizador → panel organizador
```

---

## 5. Invariantes de dominio relevantes para la UX

| Invariante | Impacto en UI |
|------------|--------------|
| No puede haber un PENDIENTE con OT anterior a un ejecutado | Grilla siempre ordenada por OT; completados no tappable |
| Tarjeta amarilla bloquea CerrarCompetencia | Badge ⚠ visible en grilla y en panel organizador |
| BKO → tarjeta roja automática, distancia obligatoria | Campo distancia no puede estar vacío en pantalla BKO |
| Ventana OT: atleta puede iniciar OT hasta OT+30s | Paso 3 muestra countdown activo post-botón TIEMPO OFICIAL |
| DQ (no inició) ≠ DNS (no se presentó) | Dos acciones distintas con registros y etiquetas distintos |
| Medición con precisión de 1 cm (CMAS 2.1.4.1) | Selector RP: metros + numpad cm |
| Penalización general DNF: −3 m (CMAS 1.1.13.1) | Tarjeta amarilla resuelta como blanca puede tener deducción |

---

*Fuentes: Reglamento CMAS Apnea Indoor v2022/01 (FAAS) · prototipo-juez.html validado 2026-04-05*
*Siguiente artefacto: wireframes-juez.md · wireframes-organizador.md · wireframes-atleta.md*
