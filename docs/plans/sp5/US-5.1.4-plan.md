# Plan de Implementacion — US-5.1.4 Generacion y ajuste de grilla UI

**Sprint:** SP5
**Incremento:** INC-5.1
**Producto:** frontend
**Patron:** React/Vite PWA consumiendo `competencia/api/`
**Estimacion:** 3 puntos

## Alcance

Implementar el tab `Grilla` del detalle de torneo para que el organizador seleccione
disciplina, cree o consulte la competencia asociada, visualice la grilla, reordene
posiciones antes de confirmar y confirme la grilla.

## Contratos Disponibles

- `GET /competencia?torneo_id=...` lista competencias por torneo.
- `POST /competencia` crea/configura competencia con intervalo OT.
- `GET /competencia/{competencia_id}/estado?disciplina=...` obtiene estado.
- `GET /competencia/{competencia_id}/grilla?disciplina=...` obtiene grilla.
- `POST /competencia/{competencia_id}/ajustar-grilla` ajusta posiciones.
- `POST /competencia/{competencia_id}/confirmar-grilla` confirma grilla.

## Brecha Detectada

La spec requiere que la UI envie `primer OT` y que luego la tabla muestre OT calculado
desde ese valor. En el backend actual existe `GenerarGrillaCommand(ot_inicio=...)`, pero
no hay endpoint HTTP expuesto para ejecutarlo. `POST /competencia` solo configura el
intervalo y no recibe `primer_ot`.

**Decision requerida antes de Fase 3:** aprobar una de estas opciones:

1. Implementar solo frontend contra contratos existentes. La accion `Generar grilla`
   creara la competencia y consultara `GET /grilla`; si el backend no genero grilla,
   la UI mostrara estado vacio/error operativo.
2. Agregar un endpoint backend minimo para generar grilla desde la UI, por ejemplo
   `POST /competencia/{competencia_id}/generar-grilla` con `{ disciplina, ot_inicio,
   andariveles }`, y luego consumirlo desde el frontend.

Recomendacion tecnica: opcion 2, porque es la unica que satisface el criterio
"primer OT 09:00 produce OT 09:00, 09:08, 09:16" de forma verificable.

## Tareas

### 1. API Frontend

- [ ] Extender `frontend/src/api/competencia.ts` con payloads tipados:
  - `crearCompetencia({ competenciaId, disciplina, intervaloMinutos, configuradoPor, torneoId })`.
  - `obtenerCompetenciasPorTorneo(torneoId, disciplina?)` o filtrado local por disciplina.
  - `ajustarGrilla({ competenciaId, disciplina, cambios })`.
  - `confirmarGrilla({ competenciaId, disciplina })`.
  - Si se aprueba opcion 2: `generarGrilla({ competenciaId, disciplina, otInicio, andariveles })`.
- [ ] Normalizar errores con `ApiError` existente.
- [ ] Mantener bearer token con `buildHeaders()`.

### 2. Componentes UI

- [ ] Crear `frontend/src/components/organizador/ConfigurarGrillaForm.tsx`.
  - Campo intervalo OT numerico.
  - Campo primer OT `HH:MM`.
  - Boton `Generar grilla`.
  - Estados disabled/loading/error.
- [ ] Crear `frontend/src/components/organizador/TablaGrilla.tsx`.
  - Tabla con posicion, atleta, AP, andarivel y OT.
  - Reordenamiento manual solo en estado `Configurada`.
  - Recalculo local de posiciones 1..N al mover filas.
  - Envio de cambios en un unico `POST ajustar-grilla`.
  - Modo solo lectura si `grilla_confirmada` o estado `GrillaConfirmada`.
- [ ] Implementar drag sin nueva dependencia usando HTML Drag and Drop nativo, salvo que se
  apruebe instalar `@dnd-kit/core` y actualizar `package.json`.

### 3. Panel Grilla

- [ ] Crear `frontend/src/components/organizador/GrillaPanel.tsx`.
- [ ] Obtener competencias del torneo y resolver competencia por disciplina seleccionada.
- [ ] Mostrar selector de disciplina.
- [ ] Si no hay competencia, mostrar `ConfigurarGrillaForm`.
- [ ] Si hay competencia, consultar estado y grilla.
- [ ] Mostrar boton `Confirmar grilla` solo si hay atletas y la grilla no esta confirmada.
- [ ] Invalidar/refrescar queries tras generar, reordenar o confirmar.

### 4. Integracion en DetalleTorneo

- [ ] Reemplazar placeholder del tab `Grilla` en `DetalleTorneoPage.tsx`.
- [ ] Pasar `torneoId` a `GrillaPanel`.
- [ ] Mantener estilo visual consistente con `InscriptosPanel`.

### 5. Validacion

- [ ] Ejecutar `npm run build` en `frontend/`.
- [ ] Ejecutar `npm run lint` en `frontend/` si no queda bloqueado por artefactos generados.
- [ ] Validar manualmente los escenarios de `tests/features/US-5.1.4-generacion-ajuste-grilla.feature`.
- [ ] Documentar evidencia en `docs/reports/US-5.1.4-report.md` en Fase 9.

## Riesgos y Decisiones

- `@dnd-kit/core` no esta declarado en `frontend/package.json`, aunque la spec dice que ya existe.
- El contrato HTTP actual no permite enviar `primer OT` para generar la grilla; sin endpoint nuevo,
  la aceptacion principal queda parcialmente bloqueada.
- La UI no debe permitir reordenar ni confirmar si la competencia ya esta en `GrillaConfirmada`.
- Si una disciplina no tiene atletas/AP, el boton de confirmar debe quedar deshabilitado.

## DoD

- El organizador puede seleccionar disciplina en el tab `Grilla`.
- Puede crear/configurar la competencia para la disciplina desde la UI.
- Ve la grilla ordenada con AP, posicion, andarivel y OT.
- Puede reordenar filas antes de confirmar y persistir cambios.
- Puede confirmar la grilla y la tabla queda solo lectura.
- Build frontend aprobado.
