# Checklist UAT SP4 — Flujo de Performance (Capa 2 Manual)

**Generado:** 2026-04-12 15:07
**Frontend:** http://localhost:5173
**Login:** juez@uat-sp4.test / juezsp4uat2025

---

## Setup previo

- [ ] Frontend corriendo: `cd frontend && npm run dev`
- [ ] Backend corriendo en puerto 8000
- [ ] Abrir http://localhost:5173 en Chrome/Safari (modo móvil en DevTools)
- [ ] Hacer login con el usuario juez

---

## Competencia DNF

**Cómo acceder:** Login → /juez/disciplinas → seleccionar DNF → grilla → tocar atleta

### E-01 — DNS (Diego Vega, AP=40m)
*Verifica el flujo de No Se Presenta*

- [X] Atleta aparece en grilla con estado AnunciadaAP
- [X] Paso 1: botón "LLAMAR ATLETA" visible y funcional
- [X] Paso 2: aparece opción "DNS — NO SE PRESENTA"
- [X] Al confirmar DNS: pantalla de completado muestra "DNS REGISTRADO"
- [X] Botón "SIGUIENTE ATLETA" navega de vuelta a grilla

---

### E-02 — BKO mid-performance (Laura Romero, AP=50m)
*Verifica el blackout durante la performance*

- [X] Llegar al paso 4 (performance en curso)
- [X] Botón "BKO — BLACK-OUT" visible
- [X] Al presionar BKO: aparece formulario StepBKO con selector RP (metros.centímetros) y motivo DQ
- [X] Ingresar metros=25, centímetros=50
- [X ] Seleccionar motivo: BKO SUBACUÁTICO (requiere campo distancia blackout) 
- [ ] Ingresar distancia blackout (ej: 20.00) no
- [ ] Botón CONFIRMAR habilitado solo cuando todos los campos están completos (no se habilita)
- [ ] Al confirmar: pantalla completada muestra "TARJETA ROJA"
- [ ] Botón CANCELAR vuelve al paso 4 limpiando los campos

---

### E-03 — Blanca simple (Carlos Ibañez, AP=60m)
*Flujo dorado completo: paso 1 → paso 6*

- [X] Flujo completo paso 1 (llamar) → paso 2 (confirmar) → paso 3 (OT) → paso 4 (performance) → paso 5 (RP)
- [X] Paso 5: ingresar metros=58, centímetros=00
- [X] Paso 6: tres botones de tarjeta sin texto, con colores (blanco, rojo, amarillo)
- [X] Seleccionar BLANCA: selector resaltado en verde
- [X] No aparece selector de motivo DQ
- [X] Botón CONFIRMAR TARJETA habilitado
- [X] Pantalla completada muestra marca y "TARJETA BLANCA"

---

### E-04 — Blanca con penalizaciones (Ana Flores, AP=70m)
*Verifica el selector de penalizaciones*

- [X] Llegar al paso 6 con tarjeta BLANCA seleccionada
- [X] Aparece sección de penalizaciones con 4 tipos
- [X] Agregar 1 penalización "Sin contacto pared": contador sube a 1
- [X] Agregar 1 penalización "Fuera de carril": contador sube a 1
- [X] Resumen muestra "2 penalizaciones · −6m"
- [X] Botón quitar (−) reduce el contador; no puede bajar de 0
- [X] Al confirmar: pantalla completada muestra "TARJETA BLANCA CON PENALIZACIONES" y "2 penalizaciones"

---

### E-05 — Roja DQ estándar (Roberto Chen, AP=80m)
*Verifica el selector de motivo DQ sin distancia*

- [ ] Paso 6: seleccionar ROJA
- [ ] Aparece selector de motivo DQ
- [ ] Seleccionar "PROTOCOLO SUPERFICIE" (no requiere distancia)
- [ ] Campo distancia blackout NO aparece
- [ ] Botón CONFIRMAR habilitado con motivo seleccionado
- [ ] Pantalla completada muestra "TARJETA ROJA"

---

### E-06 — Roja BKO post-performance (Patricia Ruiz, AP=90m)
*Verifica distancia blackout obligatoria*

- [ ] Paso 6: seleccionar ROJA
- [ ] Seleccionar "BKO SUPERFICIE": aparece campo "Distancia blackout"
- [ ] Botón CONFIRMAR deshabilitado hasta completar distancia
- [ ] Ingresar distancia=15.00
- [ ] Botón CONFIRMAR se habilita
- [ ] Pantalla completada muestra "TARJETA ROJA"

---

### E-07 — Resolver revisión → Blanca (Martin Acosta, ya en EnRevision)
*Resume: atleta ya tiene tarjeta amarilla asignada*

- [ ] En grilla: atleta aparece con estado EnRevision
- [ ] Al seleccionarlo: flow inicia directo en **paso 7** (no pasa por 1-6)
- [ ] Pantalla muestra "TARJETA AMARILLA · Resolución pendiente"
- [ ] Botón "RESOLVER → BLANCA" disponible
- [ ] Al seleccionar Blanca: no aparece selector de motivo DQ
- [ ] Botón CONFIRMAR RESOLUCIÓN habilitado
- [ ] Pantalla completada muestra "TARJETA BLANCA"

---

### E-08 — Resolver revisión → Roja (Silvia Casas, ya en EnRevision)
*Resume: atleta ya tiene tarjeta amarilla asignada*

- [ ] Flow inicia en **paso 7**
- [ ] Seleccionar "RESOLVER → ROJA": aparece selector de motivo DQ
- [ ] Seleccionar motivo DQ (ej: INFRACCIÓN TÉCNICA)
- [ ] Botón CONFIRMAR habilitado con motivo seleccionado
- [ ] Pantalla completada muestra "TARJETA ROJA"

---

### R-01 — Resume en paso 2 (Jorge Mendez, ya Llamada)
*Verifica que el flow retoma el estado correcto*

- [ ] En grilla: atleta aparece con estado Llamada
- [ ] Al seleccionarlo: flow inicia directo en **paso 2** (Confirmar presencia)
- [ ] Paso 1 (Llamada) NO aparece (ya fue ejecutado)
- [ ] Continuar flujo normal desde paso 2

---

### R-02 — Resume en paso 6 (Claudia Rios, ya ResultadoRegistrado)
*Verifica que el flow retoma el estado correcto*

- [ ] En grilla: atleta aparece con estado ResultadoRegistrado
- [ ] Al seleccionarlo: flow inicia directo en **paso 6** (Tarjeta)
- [ ] Pasos 1-5 NO aparecen
- [ ] AtletaCard muestra el RP ya registrado (125m)
- [ ] Continuar desde paso 6

---

## Competencia STA

**Cómo acceder:** Login → /juez/disciplinas → seleccionar STA → grilla → tocar atleta

### T-01 — DNS STA (Javier Herrera, AP=120s)
*Verifica DNS en disciplina de tiempo*

- [ ] Flow normal hasta paso 2
- [ ] AtletaCard muestra "AP: 2:00 min" (no en metros)
- [ ] Confirmar DNS → completado "DNS REGISTRADO"

---

### T-02 — BKO STA mid-performance (Carolina Espinoza, AP=180s)
*Verifica BKO sin selector de metros (STA usa tiempo)*

- [ ] Llegar al paso 4
- [ ] Presionar "BKO — BLACK-OUT"
- [ ] StepBKO **NO** muestra el selector RP (metros/centímetros) — es STA
- [ ] Solo aparece: selector de motivo DQ
- [ ] Seleccionar BKO SUBACUÁTICO
- [ ] Botón CONFIRMAR habilitado solo con motivo (sin necesidad de metros ni distancia)
- [ ] Confirmar → "TARJETA ROJA"

---

### T-03 — Blanca STA (Fernando Bravo, AP=240s)
*Verifica el flujo de tiempo completo*

- [ ] Paso 3: texto "Las vías respiratorias del atleta entran en contacto con el agua"
- [ ] Botón VÍAS RESPIRATORIAS EN AGUA (en lugar de "ATLETA INICIA")
- [ ] Paso 5: selector RP de tiempo (minutos + segundos, no metros)
- [ ] Ingresar 4 minutos, 05 segundos
- [ ] Paso 6: confirmar BLANCA
- [ ] Pantalla completada muestra "4:05 min"

---

## Hallazgos de UI

Documentar aquí cualquier problema encontrado durante el walk-through:

.
3. En la confirmación de la marca (paso 5) modificar el layout para que el ingreso del los números quede dentro de la region de la pantalla del teléfono
4. En el paso 6 el selector tarjeta deber con los colores de cada tarjeta sin texto
5. En la grilla de la competencia, el primero de la lista debe ser el proximo atleta.
6. Cuando hay BKO, la distancia es la misma que se ingresa con los botones, no se necesario volver a pedirla
7. Al confirmar: pantalla completada muestra "TARJETA ROJA", debe pintarse de rojo el badge
8. Seleccionar BLANCA: selector resaltado en verde, la tarjeta debe ser de color blanca, cada una de las tres tarjetas deben estar pintadas para que el juez sepa los colores

---

*Generado automáticamente por run_uat.sh — Sun Apr 12 15:07:14 -03 2026*
