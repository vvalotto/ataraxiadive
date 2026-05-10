# US-6.3.2: Formulario de Inscripción — AP en wizard + persistir adjuntos (RF-IN-05/06)

**Estado**: `Pending`
**Incremento**: INC-6.3 — Ajustes Atleta
**Hallazgos**: UI-ATL-02 · RF-IN-05 · RF-IN-06
**Bounded Context**: `registro` + `frontend`
**Capas afectadas**:
- `frontend/src/pages/atleta/AtletaInscripcionPage.tsx`
- `registro/domain/aggregates/inscripcion.py`
- `registro/infrastructure/repositories/sqlite_inscripcion_repository.py`
- `registro/api/router.py`

---

## Descripción

Como **atleta completando el wizard de inscripción**,
quiero **declarar mi AP y adjuntar mi certificado médico y comprobante de pago dentro del mismo formulario**
para **completar toda la información necesaria en un solo flujo sin pasos adicionales posteriores**.

---

## Contexto de los Hallazgos

### UI-ATL-02 — AP fuera del flujo de inscripción

El paso 2 del wizard permite seleccionar disciplinas pero no declara el AP. El atleta termina de inscribirse y recién después debe ir a "Mis inscripciones" → "Declarar AP". El AP es dato esencial: sin él el organizador no puede cerrar el período de inscripción.

### RF-IN-05 / RF-IN-06 — UI hecha, backend pendiente

El paso 3 del wizard ya recopila `certificado` (File) y `comprobante` (File) en el cliente, pero la `mutationFn` los descarta: solo llama `POST /registro/inscripciones` que no acepta archivos. El aggregate `Inscripcion` y la tabla `inscripciones` no tienen columnas para estos adjuntos.

**Nota AA-03**: `registro` BC está en D=0.59 degradando. Persistencia mínima — un campo por adjunto, un endpoint por adjunto. Sin nuevas abstracciones ni ports.

---

## Fuente de verdad

- `docs/05-requerimientos_funcionales.md` — RF-IN-05 / RF-IN-06
- `docs/plans/sp6/PLAN-SP6.md` — UI-ATL-02 · RF-IN-05 · RF-IN-06
- `frontend/src/pages/atleta/AtletaInscripcionPage.tsx` — wizard actual
- `frontend/src/pages/atleta/portalData.ts` — helpers AP (`esDisciplinaTiempo`, `isApInputValido`, `normalizeApInput`, `getUnidadEsperada`, `getUnidadLabel`)
- `src/registro/domain/aggregates/inscripcion.py` — aggregate sin campos adjuntos
- `src/registro/infrastructure/repositories/sqlite_inscripcion_repository.py` — repositorio con `_ensure_schema`

---

## Especificación

### Tarea 1 (frontend) — AP inline en paso 2

| | |
|---|---|
| **Precondición** | El paso 2 muestra disciplinas y categoría; no tiene inputs AP |
| **Postcondición** | Al seleccionar una disciplina aparece su input AP inmediatamente debajo; al deseleccionar, el valor se descarta |
| **Invariante** | El AP no es obligatorio para avanzar al paso 3; si se ingresa, debe ser válido según `isApInputValido` |

Estado adicional: `apPorDisciplina: Record<string, string>`.

```tsx
// Input AP por disciplina (bajo su botón cuando selected):
{selected && (
  <div className="mt-2 flex items-center gap-3 rounded-2xl border border-sky-500/30 bg-sky-500/10 px-4 py-3">
    <input
      value={apPorDisciplina[disciplina.disciplina] ?? ''}
      onChange={(e) => setApPorDisciplina(prev => ({ ...prev, [disciplina.disciplina]: e.target.value }))}
      inputMode={esDisciplinaTiempo(disciplina.disciplina) ? 'text' : 'decimal'}
      placeholder={esDisciplinaTiempo(disciplina.disciplina) ? 'mm:ss' : '0'}
      className="w-full bg-transparent text-lg font-semibold text-white outline-none placeholder:text-slate-500"
    />
    <span className="text-xs font-semibold uppercase tracking-[0.18em] text-sky-300">
      {getUnidadLabel(getUnidadEsperada(disciplina.disciplina))}
    </span>
  </div>
)}
```

Validación al avanzar al paso 3: si algún AP ingresado es inválido → error; si está vacío → se omite (se puede declarar luego).

### Tarea 2 (frontend) — Enviar APs y adjuntos tras inscripción

| | |
|---|---|
| **Precondición** | La `mutationFn` solo llama `inscribirAtleta`; APs y archivos se descartan |
| **Postcondición** | Tras `inscribirAtleta`, se llaman `guardarApInscripcion` (por cada AP declarado) y los endpoints de adjuntos (si los archivos están presentes) |
| **Invariante** | Si alguna llamada post-inscripción falla, la inscripción ya está creada — mostrar advertencia pero no revertir |

```typescript
mutationFn: async () => {
  const { inscripcion_id } = await inscribirAtleta({ atletaId, torneoId, disciplinas })

  // APs declarados (best-effort)
  for (const d of disciplinasSeleccionadas) {
    const v = apPorDisciplina[d]
    if (v && isApInputValido(v, d)) {
      await guardarApInscripcion({ inscripcionId: inscripcion_id, disciplina: d, valorAp: normalizeApInput(v, d) })
    }
  }

  // Adjuntos (best-effort)
  if (certificado) await subirAptoMedico(inscripcion_id, certificado)
  if (comprobante) await subirConstanciaPago(inscripcion_id, comprobante)

  return inscripcion_id
}
```

Las funciones `subirAptoMedico` y `subirConstanciaPago` se agregan a `frontend/src/api/registro.ts` usando `FormData` + `fetch` (o Axios según el patrón existente).

### Tarea 3 (backend) — Campos en aggregate e infraestructura

| | |
|---|---|
| **Precondición** | `Inscripcion` no tiene campos de adjuntos; la tabla tampoco |
| **Postcondición** | `Inscripcion` tiene `apto_medico_path: str | None` y `constancia_pago_path: str | None`; la tabla tiene las columnas correspondientes |
| **Invariante** | Migración via `_ensure_schema` con `ALTER TABLE ... ADD COLUMN` (nullable) — compatible con datos existentes |

```python
# En inscripcion.py:
apto_medico_path: str | None = field(default=None)
constancia_pago_path: str | None = field(default=None)

def adjuntar_apto_medico(self, path: str) -> None:
    if not path or not path.strip():
        raise ValueError("path no puede ser vacío")
    self.apto_medico_path = path

def adjuntar_constancia_pago(self, path: str) -> None:
    if not path or not path.strip():
        raise ValueError("path no puede ser vacío")
    self.constancia_pago_path = path
```

```python
# En sqlite_inscripcion_repository.py — _ensure_schema:
for col, ddl in [
    ("apto_medico_path", "ALTER TABLE inscripciones ADD COLUMN apto_medico_path TEXT"),
    ("constancia_pago_path", "ALTER TABLE inscripciones ADD COLUMN constancia_pago_path TEXT"),
]:
    if col not in columns:
        await conn.execute(ddl)
```

### Tarea 4 (backend) — Endpoints de upload

| | |
|---|---|
| **Precondición** | No existen endpoints para adjuntos |
| **Postcondición** | `POST /registro/inscripciones/{id}/apto-medico` y `POST /registro/inscripciones/{id}/constancia-pago` aceptan `UploadFile`, guardan el archivo en `data/adjuntos/{inscripcion_id}/` y actualizan el aggregate |
| **Invariante** | Auth guard `AtletaDep`; tamaño máximo 10 MB; directorio creado con `mkdir(parents=True, exist_ok=True)` |

Estrategia de almacenamiento: `data/adjuntos/{inscripcion_id}/apto_medico{ext}` y `data/adjuntos/{inscripcion_id}/constancia_pago{ext}`. No se necesita port de storage para v1.0.

```python
@router.post("/inscripciones/{inscripcion_id}/apto-medico", status_code=200)
async def subir_apto_medico(inscripcion_id: UUID, archivo: UploadFile, _: AtletaDep) -> JSONResponse:
    return await _subir_adjunto(inscripcion_id, archivo, "apto_medico", "adjuntar_apto_medico")

@router.post("/inscripciones/{inscripcion_id}/constancia-pago", status_code=200)
async def subir_constancia_pago(inscripcion_id: UUID, archivo: UploadFile, _: AtletaDep) -> JSONResponse:
    return await _subir_adjunto(inscripcion_id, archivo, "constancia_pago", "adjuntar_constancia_pago")

async def _subir_adjunto(inscripcion_id: UUID, archivo: UploadFile, nombre: str, metodo: str) -> JSONResponse:
    MAX_SIZE = 10 * 1024 * 1024
    contenido = await archivo.read()
    if len(contenido) > MAX_SIZE:
        return JSONResponse(status_code=413, content={"detail": "Archivo demasiado grande (máx 10 MB)"})
    inscripcion = await _inscripcion_repo().find_by_id(inscripcion_id)
    if inscripcion is None:
        return JSONResponse(status_code=404, content={"detail": "Inscripción no encontrada"})
    ext = Path(archivo.filename or "").suffix or ".bin"
    directorio = Path("data/adjuntos") / str(inscripcion_id)
    directorio.mkdir(parents=True, exist_ok=True)
    ruta = directorio / f"{nombre}{ext}"
    ruta.write_bytes(contenido)
    getattr(inscripcion, metodo)(str(ruta))
    await _inscripcion_repo().save(inscripcion)
    return JSONResponse(status_code=200, content={"path": str(ruta)})
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-6.3.2 — Formulario inscripción: AP inline + persistir adjuntos

  Scenario: Input AP aparece al seleccionar disciplina
    Given el atleta está en el paso 2 del wizard
    When selecciona la disciplina DYN
    Then aparece un input AP debajo de DYN con placeholder "0" y unidad "M"

  Scenario: AP inválido bloquea avance al paso 3
    Given el atleta seleccionó STA y escribió "abc" como AP
    When intenta avanzar al paso 3
    Then ve error de AP inválido y permanece en el paso 2

  Scenario: AP vacío no bloquea avance
    Given el atleta seleccionó DYN sin completar AP
    When intenta avanzar al paso 3
    Then avanza sin error

  Scenario: AP declarado se persiste tras inscripción
    Given el atleta completó el wizard con DYN seleccionado y AP "50"
    When envía la inscripción
    Then el AP de DYN queda guardado en el backend

  Scenario: Apto médico persistido en backend
    Given una inscripción activa
    When el frontend llama POST /registro/inscripciones/{id}/apto-medico con un PDF
    Then la respuesta es 200 y la inscripción tiene apto_medico_path no nulo

  Scenario: Constancia de pago persistida en backend
    Given una inscripción activa
    When el frontend llama POST /registro/inscripciones/{id}/constancia-pago con un PDF
    Then la respuesta es 200 y la inscripción tiene constancia_pago_path no nulo

  Scenario: Archivo demasiado grande rechazado
    Given una inscripción activa
    When se intenta subir un archivo de más de 10 MB
    Then la respuesta es 413

  Scenario: Inscripciones existentes sin adjuntos siguen funcionando
    Given una inscripción creada antes de esta US
    When se recupera del repositorio migrado
    Then apto_medico_path y constancia_pago_path son None sin error
```

---

## Notas de implementación

- Importar `UploadFile` de FastAPI y `Path` de `pathlib` en `router.py`
- `data/adjuntos/` debe agregarse a `.gitignore`
- `guardarApInscripcion` requiere `inscripcion_id` del response de `inscribirAtleta` — verificar que la API devuelva `inscripcion_id`
- Las llamadas post-inscripción son best-effort: si fallan, la inscripción ya está creada; el atleta puede completarlas desde "Mis inscripciones" (flujo alternativo ya existente)

---

## Referencias

- RFs: `docs/05-requerimientos_funcionales.md` — RF-IN-05 · RF-IN-06
- Hallazgo UX: `docs/plans/sp6/PLAN-SP6.md` — UI-ATL-02
- Wizard: `frontend/src/pages/atleta/AtletaInscripcionPage.tsx`
- Helpers AP: `frontend/src/pages/atleta/portalData.ts`
- Aggregate: `src/registro/domain/aggregates/inscripcion.py`
- Repositorio: `src/registro/infrastructure/repositories/sqlite_inscripcion_repository.py`

---

*Redactado: 2026-05-07 — SP6 INC-6.3*
