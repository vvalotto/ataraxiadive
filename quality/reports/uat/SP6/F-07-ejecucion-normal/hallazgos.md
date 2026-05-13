# Hallazgos — Fase F-07: Ejecución Normal de Performances

## Defectos

| ID | Escenario | Descripción | Severidad | Pasos para reproducir | Estado | Fix |
|----|-----------|-------------|-----------|----------------------|--------|-----|
| H-07-01 | F07-S02 | Portal público muestra a Cuchiarelli en grilla DBF sin estado DNS tras marcarlo en panel juez | 🟡 | 1. Juez 1 marca DNS a Cuchiarelli DBF · 2. Abrir portal público `/portalapnea` → página torneo → tab DBF · 3. Refrescar manualmente · Cuchiarelli aparece sin estado DNS | Resuelto | `AtletaRow`: columna Tarjeta muestra "DNS" cuando `entry.estado === 'DNS'` |
| H-07-02 | F07-S06 | Portal público muestra RP de SPE en segundos crudos (ej: "59") en lugar de mm:ss (ej: "00:59.00") | 🟡 | 1. Juez 2 registra Alperin SPE RP=00:59.00 · 2. Abrir portal público → tab SPE · resultado muestra "59" | Resuelto | `PublicTorneoDetallePage`: `formatRp` usa `formatMarca` en lugar de valor crudo |

## Mejoras (fuera de scope UAT)

| ID | Origen | Descripción | Prioridad sugerida |
|----|--------|-------------|-------------------|
| M-07-01 | F07-S03 | Botones de tarjeta (Blanca/Amarilla/Roja) con colores muy tenues en estado no seleccionado — dificultan identificación en móvil · Resuelto: bg opacidad /5→/40 · border /30→/60 en `StepTarjeta.tsx` | Media |
| M-07-02 | F07-S08 | Cartel "Ventana OT activa" redundante en paso 3 del flujo juez · Resuelto: div cyan eliminado de `PerformanceFlowPage.tsx` | Baja |
