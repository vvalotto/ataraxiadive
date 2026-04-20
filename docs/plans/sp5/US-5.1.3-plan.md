# Plan de Implementacion — US-5.1.3 Vista de Inscriptos con Estado AP

**Sprint:** SP5  
**Incremento:** INC-5.1  
**Producto:** frontend  
**Patron:** React/Vite PWA consumiendo BCs `registro` y `competencia` existentes  
**Estimacion:** 3 puntos

## Alcance

Implementar el tab `Inscriptos` del detalle de torneo con una tabla read-only de atletas
inscriptos y estado AP por disciplina.

## Tareas

### 1. API Registro

- [ ] Crear `frontend/src/api/registro.ts`.
- [ ] Implementar `listarInscriptos(torneoId)`.
- [ ] Implementar `fetchAtleta(atletaId)`.
- [ ] Reutilizar bearer token mediante `getToken`.

### 2. Componentes UI

- [ ] Crear `EstadoAPBadge`.
- [ ] Crear `TablaInscriptos`.
- [ ] Mostrar filtro de disciplina con opcion `Todas`.
- [ ] Mostrar estado AP por disciplina en cada fila.
- [ ] Mostrar mensaje vacio si no hay inscriptos.

### 3. Integracion en DetalleTorneo

- [ ] Reemplazar placeholder del tab `Inscriptos`.
- [ ] Cargar inscriptos desde Registro.
- [ ] Cargar datos de atleta por `atleta_id`.
- [ ] Cargar competencias por torneo y grillas por disciplina en paralelo.
- [ ] Cruzar `atleta_id` + disciplina para determinar AP registrado.

### 4. Validacion

- [ ] `npm run build`.
- [ ] `npx eslint src`.
- [ ] Documentar limitacion de `npm run lint` global por `.vite/deps` generado.

## Riesgos y Decisiones

- El endpoint de atleta no expone genero; la UI mostrara `Sin dato`.
- Si no existe competencia/grilla para una disciplina, se mostrara `Sin AP` para esa disciplina.
- No se modifica backend en esta US.

## DoD

- El organizador ve inscriptos en el tab correspondiente.
- Puede filtrar por disciplina.
- Cada disciplina muestra AP registrado con valor o Sin AP.
- La vista es read-only.
