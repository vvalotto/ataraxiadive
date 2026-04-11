# Plan de Implementación — US-4.3.3

**US:** US-4.3.3 — Casos alternativos — DNS, BKO y tarjeta blanca con penalizaciones  
**Incremento:** INC-4.3  
**Sprint:** SP4 — La Plataforma  
**Fecha:** 2026-04-11  
**Branch:** `feature/US-4.3.3-casos-alternativos-performance`

---

## Objetivo

Extender el flujo del juez implementado en `US-4.3.2` para cubrir:

- DNS desde el flujo operativo;
- BKO con distancia obligatoria y tarjeta roja;
- tarjeta roja con `MotivoDQ`;
- tarjeta blanca con penalizaciones técnicas;
- bloqueo visual de penalizaciones cuando la disciplina no las admite.

---

## Alcance real

### Backend

Agregar al router de competencia:

- `POST /competencia/{competencia_id}/registrar-dns`

Reutilizando:

- `RegistrarDNSHandler`
- `JuezDep`
- `PerformancesEstadoAdapter`

No se prevén cambios de dominio para esta US salvo que aparezca un bloqueo no detectado.

### Frontend

Extender [PerformanceFlowPage](/Users/victor/PycharmProjects/ataraxiadive/frontend/src/pages/juez/PerformanceFlowPage.tsx:1) para soportar:

- acción `DNS` desde Paso 2;
- acción `BKO` desde Paso 4;
- selector de `MotivoDQ` en roja;
- selector de penalizaciones en blanca penalizada;
- resultado final consistente con roja / blanca / blanca penalizada / DNS.

No conviene abrir páginas separadas: el wizard actual ya concentra el estado local y
la navegación del juez.

---

## Decisiones de compatibilidad con el dominio real

### 1. DNS

La spec habla de DNS desde Paso 1 o Paso 2, pero el aggregate solo permite DNS desde `Llamada`.

Decisión:

- exponer `DNS` desde Paso 2;
- opcionalmente mostrar el CTA en Paso 1 solo después de `llamar`, pero sin simular un DNS desde `AnunciadaAP`.

### 2. Blanca con penalizaciones

La UI puede seguir mostrando “Tarjeta blanca”, pero el payload real debe mapear a:

- `tipo = BlancaConPenalizaciones`
- `penalizaciones = [{ tipo, deduccion }, ...]`

No se debe enviar `Blanca` con penalizaciones porque el backend lo rechaza.

### 3. Motivos DQ

La UI mostrará labels en español, pero enviará los códigos reales:

- `BKO_SUPERFICIE`
- `BKO_SUBACUATICO`
- `PROTOCOLO_SUPERFICIE`
- `INFRACCION_TECNICA_DQ`
- `NO_INICIO_EN_VENTANA`
- `SALIDA_EN_FALSO`

### 4. Penalizaciones permitidas

La validación frontend seguirá el código real:

- permitidas: `DNF`, `DYN`, `DBF`
- no permitidas: `STA`, familia `SPE`, y el resto

---

## Cambios propuestos

### A. Backend API

Modificar [src/competencia/api/router.py](/Users/victor/PycharmProjects/ataraxiadive/src/competencia/api/router.py:1):

1. Agregar `RegistrarDNSBody`.
2. Agregar `get_registrar_dns_handler(...)`.
3. Exponer `POST /{competencia_id}/registrar-dns`.
4. Mapear:
   - `PerformanceNoEncontrada` -> `404`
   - `DomainError` -> `409`

### B. API client frontend

Extender [frontend/src/api/competencia.ts](/Users/victor/PycharmProjects/ataraxiadive/frontend/src/api/competencia.ts:1):

1. `registrarDns(...)`
2. extender `asignarTarjeta(...)` para aceptar:
   - `tarjeta: 'Blanca' | 'Roja' | 'BlancaConPenalizaciones'`
   - `penalizaciones`
3. helper de construcción de penalizaciones:
   - `[{ tipo, deduccion: '3' }, ...]`

### C. UI del wizard

Modificar [frontend/src/pages/juez/PerformanceFlowPage.tsx](/Users/victor/PycharmProjects/ataraxiadive/frontend/src/pages/juez/PerformanceFlowPage.tsx:1):

1. Paso 2:
   - agregar CTA `DNS — No se presenta`
   - mutación `registrarDns`
   - pantalla/estado final de DNS
2. Paso 4:
   - agregar CTA `BKO — Black-out`
   - abrir modo BKO con selector de motivo BKO + distancia obligatoria
   - ejecutar secuencia:
     - `registrarResultado`
     - `asignarTarjeta(Roja, motivo_dq, distancia_blackout)`
3. Paso 6:
   - mantener roja con `MotivoDQ`
   - agregar selector de penalizaciones para blanca penalizada
   - si hay penalizaciones > 0, enviar `BlancaConPenalizaciones`
4. Pantalla final:
   - variar texto según resultado:
     - `DNS registrado`
     - `TARJETA ROJA`
     - `TARJETA BLANCA`
     - `TARJETA BLANCA CON PENALIZACIONES`

### D. Nuevos componentes

Crear componentes chicos para no degradar más `PerformanceFlowPage`:

- `frontend/src/components/juez/MotivoDqSelector.tsx`
- `frontend/src/components/juez/PenalizacionesSelector.tsx`

Objetivo:

- encapsular reglas visuales y labels de dominio;
- mantener el page component dentro de un tamaño razonable.

### E. Fixture manual

Agregar script específico de `US-4.3.3` o extender el de `US-4.3.2` para soportar:

- fixture DNF para penalizaciones;
- fixture con performance ya llamada para probar DNS/BKO más rápido.

Recomendación:

- nuevo script `scripts/setup_us_4_3_3_fixture.py`
- no modificar el de `US-4.3.2`, para conservar un reset simple del camino feliz.

---

## Riesgos

### 1. La spec pide cosas que el dominio todavía no acepta

Caso puntual:

- DNS desde `AnunciadaAP`

Si se insiste en ese comportamiento, habrá que cambiar el aggregate y no sólo la UI/API.

### 2. La grilla no expone todavía RP final penalizado

Si el criterio de aceptación exige mostrar `69.00m` en grilla después de penalizar,
hará falta enriquecer `ObtenerGrillaHandler` con `rp_medido` / `rp_penalizado`.

### 3. `PerformanceFlowPage` ya creció bastante

Si en esta US se fuerza demasiada lógica inline, la página se vuelve difícil de mantener.

Mitigación:

- extraer selectors y sub-secciones en componentes;
- mantener mutaciones y reglas derivadas nombradas.

---

## Validación prevista

- `npm run build`
- `npm run lint`
- `./.venv/bin/python -m compileall src`
- smoke test backend para `registrar-dns`
- validación manual:
  - DNS
  - BKO roja
  - roja con motivo
  - blanca con penalizaciones
  - penalizaciones deshabilitadas en STA

---

## Secuencia de implementación

1. Exponer `registrar-dns` en backend.
2. Extender API client frontend.
3. Extraer `MotivoDqSelector` y `PenalizacionesSelector`.
4. Extender `PerformanceFlowPage` con DNS/BKO/penalizaciones.
5. Preparar fixture manual específica.
6. Ejecutar validaciones técnicas.
7. Dejar artefactos de cierre y tracker consistente.

---

*Plan generado: 2026-04-11 — US-4.3.3 INC-4.3 SP4*
