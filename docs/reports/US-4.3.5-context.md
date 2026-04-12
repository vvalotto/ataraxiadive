# Contexto de Implementación — US-4.3.5

| Campo | Valor |
|---|---|
| **US** | US-4.3.5 — Adaptación STA en el Paso 3 |
| **Incremento** | INC-4.3 |
| **Sprint** | SP4 — La Plataforma |
| **Fecha** | 2026-04-12 |
| **Branch** | `feature/US-4.3.5-sta-paso-3` |

---

## Hallazgos relevantes del código actual

### 1. El inicio real de la performance hoy está corrido al Paso 4

La spec de `US-4.3.2` y los wireframes del juez indican:

- Paso 3: OT, ventana activa y acción de inicio;
- Paso 4: performance en curso con cronómetro corriendo.

La implementación actual en `PerformanceFlowPage.tsx` hace otra cosa:

- Paso 3 solo abre la ventana OT;
- Paso 4 recién muestra `INICIAR PERFORMANCE`;
- Paso 4 también usa `chronoStarted` para alternar entre inicio y finalización.

Conclusión:

- `US-4.3.5` no conviene resolverse solo cambiando un label;
- hay que realinear el flujo para que el tap de inicio suceda dentro del Paso 3.

### 2. La detección de STA ya existe implícitamente por unidad

La pantalla hoy calcula:

- `isSTA = atletaActivo?.unidad === "Segundos"`

Eso ya permite distinguir STA sin tocar backend ni store.

Conclusión:

- la adaptación puede resolverse solo en frontend;
- no hace falta introducir una API nueva ni cambiar el dominio.

### 3. `RpSelector` sigue modelado exclusivamente para metros y centímetros

El selector actual:

- recibe `metros` y `centimetros`;
- usa presets `[25, 50, 75, 100, 125]`;
- renderiza unidad fija `m`;
- usa botones `-1`, `+1`, `+5`, `+10`.

La spec de `US-4.3.5` requiere para STA:

- display en `MM:SS`;
- presets `2:00`, `3:00`, `4:00`, `5:00`, `6:00`;
- ajustes `-5s`, `+5s`, `+30s`, `+1m`.

Conclusión:

- `RpSelector` necesita una variante explícita para tiempo;
- no alcanza con cambiar textos desde la pantalla.

### 4. El backend ya soporta resultados en segundos

La API actual ya envía:

- `valor_rp`
- `unidad`

La pantalla usa `atletaActivo.unidad` al registrar resultado, y la spec confirma que
`unidad=Segundos` ya es compatible con backend.

Conclusión:

- la US sigue siendo frontend puro;
- el foco real es serializar correctamente el valor para STA y ajustar la UX.

### 5. No hay tests frontend automatizados en el repo

`frontend/package.json` no incluye runner de tests y no se encontraron archivos `.test` o `.spec`.

Conclusión:

- la validación técnica viable para esta US es `npm run lint` y `npm run build`;
- la validación funcional fuerte va a ser manual en navegador.

---

## Decisión para seguir

La implementación de `US-4.3.5` va a incluir:

1. realinear Paso 3 para que maneje OT + inicio;
2. mostrar CTA contextual para STA: `VIAS RESPIRATORIAS EN AGUA`;
3. dejar Paso 4 solo como performance en curso;
4. agregar modo `Segundos` en `RpSelector` para STA;
5. mantener sin cambios el backend.

---

*Generado: 2026-04-12 — Fase 0 US-4.3.5*
