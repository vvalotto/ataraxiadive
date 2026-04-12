# Plan de Implementación — US-4.3.5

**US:** US-4.3.5 — Adaptación STA en el Paso 3  
**Incremento:** INC-4.3  
**Sprint:** SP4 — La Plataforma  
**Fecha:** 2026-04-12  
**Branch:** `feature/US-4.3.5-sta-paso-3`

---

## Objetivo

Adaptar el flujo del juez para STA de forma reglamentariamente correcta:

- el inicio de la performance se registra cuando las vías respiratorias entran en agua;
- la UI del Paso 3 cambia el CTA y su texto contextual para STA;
- el Paso 5 usa un selector de tiempo en segundos, no de distancia.

---

## Alcance real

### Frontend

Modificar el flujo del juez para que:

- Paso 3 maneje la ventana OT activa y el tap de inicio;
- el CTA de inicio sea distinto en STA;
- Paso 4 represente solo la performance ya iniciada;
- `RpSelector` tenga una variante `Segundos`.

### Backend

Sin cambios.

El backend ya soporta `registrar_resultado` con `unidad=Segundos`.

---

## Decisiones de implementación

### 1. Corregir el desfasaje entre spec y UI actual

La implementación vigente deja el inicio real en Paso 4.  
Decisión:

- mover la acción de inicio al Paso 3;
- dejar Paso 4 solo para `FINALIZAR PERFORMANCE` y BKO.

Esto es consistente con:

- `docs/specs/sp4/US-4.3.2.md`
- `docs/specs/sp4/US-4.3.5.md`
- `docs/design/ux/wireframes-juez.md`

### 2. Detectar STA por unidad existente

Decisión:

- reutilizar `atletaActivo.unidad === "Segundos"` como señal de STA;
- no agregar banderas nuevas al store.

### 3. Mantener un solo `RpSelector` con dos modos

Decisión:

- extender el componente con una prop de modo;
- evitar duplicar selector de metros y selector de tiempo.

Modos:

- `Metros`
- `Segundos`

### 4. Serialización del valor RP para STA

Decisión:

- conservar el payload actual de `registrarResultado`;
- para STA construir `valor_rp` como total de segundos;
- seguir enviando `unidad` desde `atletaActivo.unidad`.

---

## Cambios propuestos

### A. Flujo del juez

Modificar:

- [frontend/src/pages/juez/PerformanceFlowPage.tsx](/Users/victor/PycharmProjects/ataraxiadive/frontend/src/pages/juez/PerformanceFlowPage.tsx:1)

Cambios:

1. introducir estado local para ventana OT activa;
2. mover el CTA de inicio al Paso 3;
3. mostrar label y descripción alternativa cuando `isSTA`;
4. al iniciar, avanzar directo a Paso 4 con cronómetro activo;
5. simplificar Paso 4 para que solo permita finalizar o registrar BKO.

### B. Selector de RP

Modificar:

- [frontend/src/components/juez/RpSelector.tsx](/Users/victor/PycharmProjects/ataraxiadive/frontend/src/components/juez/RpSelector.tsx:1)

Cambios:

1. agregar modo `Segundos`;
2. renderizar display `MM:SS`;
3. presets `120, 180, 240, 300, 360`;
4. ajustes `-5, +5, +30, +60`;
5. reutilizar el campo secundario como segundos cuando corresponda.

### C. Helpers de formato/serialización

Modificar:

- [frontend/src/pages/juez/PerformanceFlowPage.tsx](/Users/victor/PycharmProjects/ataraxiadive/frontend/src/pages/juez/PerformanceFlowPage.tsx:1)

Cambios:

1. separar formateo de distancia y de tiempo;
2. construir correctamente `valor_rp` para metros y para segundos;
3. ajustar textos de cierre para STA.

---

## Riesgos

### 1. Regresión en disciplinas de distancia

Si el reordenamiento del Paso 3/4 se hace mal, DNF y otras disciplinas pueden cambiar su
comportamiento esperado.

Mitigación:

- mantener exactamente la misma secuencia funcional para no-STA;
- validar explícitamente DNF y STA.

### 2. Formato incorrecto al enviar STA

Si la UI muestra `MM:SS` pero serializa mal `valor_rp`, el backend puede registrar un RP
distinto al esperado.

Mitigación:

- usar helpers explícitos para convertir entre display y total de segundos;
- probar con un caso simple como `4:30`.

### 3. Complejidad accidental en `PerformanceFlowPage`

La pantalla ya concentra bastante lógica.

Mitigación:

- introducir helpers pequeños en vez de ramas duplicadas;
- limitar el cambio al flujo OT y al formateo.

---

## Validación prevista

- `frontend: npm run lint`
- `frontend: npm run build`
- validación manual STA:
  - Paso 3 con CTA contextual
  - inicio desde Paso 3
  - Paso 5 en tiempo
- validación manual DNF:
  - Paso 3 estándar
  - Paso 5 en metros

---

## Secuencia de implementación

1. Inicializar tracking de `US-4.3.5`.
2. Registrar Fase 0 con el contexto validado.
3. Registrar Fase 1 con BDD.
4. Registrar Fase 2 con plan.
5. Implementar cambios en `PerformanceFlowPage`.
6. Extender `RpSelector`.
7. Ejecutar validaciones técnicas.
8. Generar reporte final y preparar smoke manual.

---

*Plan generado: 2026-04-12 — US-4.3.5 INC-4.3 SP4*
