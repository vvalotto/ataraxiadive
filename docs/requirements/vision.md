# Vision — AtaraxiaDive

| Campo | Valor |
|-------|-------|
| **Documento** | Vision del Producto |
| **Capa IEDD** | 1 — Dominio |
| **Versión** | 1.0 |
| **Fecha** | 2026-03-16 |
| **Insumos** | `docs/dominio/01-dominio_torneos_apnea.md`, `docs/dominio/03-atributos_calidad.md`, `docs/dominio/05-requerimientos_funcionales.md` |

---

## 1. El Problema que Resuelve

Los torneos nacionales de apnea (freediving) se gestionan hoy con herramientas
genéricas: planillas, papel, comunicación por mail. El flujo tiene seis fases
—apertura, inscripción, preparación, ejecución, premiación, cierre— donde la
fase de **ejecución** es un cuello de botella crítico: el juez debe registrar
acciones en tiempo real mientras el atleta está bajo el agua y el cronómetro corre.
Un error o demora en ese momento es irreversible.

**AtaraxiaDive resuelve esto** con una plataforma web especializada que cubre el
ciclo de vida completo del torneo, con capacidad offline en la interfaz del juez
y trazabilidad completa de cada performance.

---

## 2. Usuarios del Sistema

| Rol | Responsabilidad principal | Acceso |
|-----|--------------------------|--------|
| **Administrador** | Gestiona usuarios, disciplinas, categorías y reglas globales | Back-office |
| **Organizador** | Crea y conduce el torneo completo (todas las fases) | Web full |
| **Juez** | Registra performances en tiempo real durante la ejecución | Mobile-first, offline |
| **Atleta** | Se inscribe, registra anuncios (AP), consulta resultados propios y finales | Mobile-first |
| **Público** | Consulta resultados publicados del torneo | Solo lectura |

### Objetivos por rol

**Administrador:** configurar el sistema una vez y no necesitar intervención en cada torneo.

**Organizador:** conducir un torneo completo desde la apertura hasta la publicación
de resultados con mínima fricción operativa y sin errores de configuración.

**Juez:** registrar el estado de cada performance con el mínimo de acciones posibles
(máximo 6 toques por performance), incluso con manos mojadas y sin conectividad.

**Atleta:** inscribirse, declarar su AP antes del plazo, y consultar resultados
finales. No depender de terceros para ninguna de estas acciones.

---

## 3. Alcance del Sistema v1

### Dentro del alcance

- **Gestión del ciclo de vida del torneo:** apertura, inscripción, preparación,
  ejecución, premiación, cierre.
- **Inscripción de atletas** con integración opcional a la BD externa de la FAZ
  (solo lectura, pendiente de definición de protocolo). La entidad es la
  FAAS — Federación Argentina de Actividades Subacuáticas.
- **Anuncios (AP):** registro, inmutabilidad post-cierre, descalificación por no anuncio.
- **Grilla de salida:** generación automática por AP + ajuste manual del organizador.
- **Ejecución de competencias:** flujo juez completo (llamar → confirmar → iniciar
  → finalizar → registrar), soporte de múltiples andariveles simultáneos.
- **Registro de performances:** marca (tiempo o distancia con decimales), tarjeta
  (blanca/amarilla/roja), penalizaciones configurables, black-out con distancia.
- **Log de auditoría inalterable** de las acciones del juez.
- **Rankings y resultados:** por disciplina, por categoría/género, Overall del torneo.
- **Publicación de resultados** en la plataforma y exportación descargable.
- **Notificaciones** por email y push (inscripción, apertura de anuncios, resultados).
- **Modo offline** en la interfaz del juez durante la ejecución.
- **Configurabilidad** de disciplinas, categorías y reglas de tarjetas por el administrador.

### Fuera del alcance v1

- Streaming de resultados en vivo para público externo.
- Integración con cronometraje electrónico (touchpads, sensores).
- Gestión de pagos de inscripción (se acepta constancia manual).
- Exportación en formato AIDA/CMAS (pendiente para versiones posteriores).
- Múltiples sedes por torneo (un torneo = una sede).
- Soporte multi-idioma (español primero, arquitectura preparada).

---

## 4. Restricciones de Contexto

| Dimensión | Restricción |
|-----------|-------------|
| **Escala** | Hasta 100 atletas/torneo, ~50 usuarios concurrentes, 4 torneos/año |
| **Conectividad** | Competencias en piletas/lagos: conectividad no garantizada |
| **Dispositivos** | Juez en celular/tablet (manos mojadas, sol directo) |
| **Reglas** | Definidas por federaciones (AIDA/CMAS); cambian muy esporádicamente (~cada 2 años) |
| **Datos externos** | BD de atletas es externa (FAAS); protocolo de acceso pendiente |
| **Mantenimiento** | Sistema actualizable fuera de ventanas de competencia |

---

## 5. Criterios de Éxito del Producto

Derivados de los atributos de calidad (IDs del cuestionario AC-XX-NN):

| Criterio | ID | Condición verificable |
|----------|----|-----------------------|
| Respuesta del juez | AC-RD-01 | Registro de acción en ≤ 500 ms bajo carga normal |
| Flujo mínimo del juez | AC-US-02 | Performance completa en ≤ 6 acciones (toque/clic) |
| Offline garantizado | AC-DS-03 | Juez puede operar sin internet durante la ejecución |
| Auditoría inalterable | AC-SG-02 | Toda acción del juez queda registrada y no puede modificarse retroactivamente |
| Protección de resultados | AC-SG-04 | Performance cerrada no modificable sin trazabilidad |
| Persistencia ante fallas | AC-CN-01 | Performance registrada garantizada incluso ante falla inmediata post-registro |
| Reconstrucción de estado | AC-CN-03 | Estado completo de competencia reconstruible desde log de eventos |
| Configurabilidad sin código | AC-MT-02 | Organizador puede configurar reglas sin intervención de desarrollador |

---

## 6. Lo que AtaraxiaDive NO Es

- No es un sistema de gestión de federaciones (no gestiona membresías ni calendarios nacionales).
- No es una herramienta de cronometraje electrónico (el juez toma tiempos manualmente).
- No reemplaza a la base de datos de la FAAS (la consulta es de solo lectura).
- No es un sistema de streaming ni plataforma de espectadores.
- No gestiona logística del torneo (viajes, alojamiento, pagos).

---

## 7. Relación con el Experimento IEDD

AtaraxiaDive es el **sandbox empírico** del experimento IEDD. Este documento de
vision es el primer artefacto formal de la Capa 1 del marco: establece el alcance
del sistema antes de que exista una línea de código.

La hipótesis a contrastar: _pasar por vision → context-map → domain-model antes
de implementar produce invariantes de dominio más precisos y reduce la ambigüedad
que llega al código en SP1_.

El cierre de Semana 0 (con todos los artefactos de Capas 1-4 completados) será el
punto de referencia para medir esa hipótesis al cerrar BL-001.

**Documento de referencia:** `docs/contexto/PLAN-EXPERIMENTO.md`

---

## 8. Vínculo con la Cadena IEDD

```
Este documento (vision.md)              ← Capa 1: Dominio
  └── produce → context-map.md          ← Capa 2: Modelo estratégico (BCs)
        └── produce → domain-model.md   ← Capa 2: Modelo táctico (aggregates)
              └── produce → architecture.md ← Capa 4: Arquitectura
                    └── produce → US-IEDD   ← Capa 3: Especificación
                          └── produce → src/ ← Capa 5: Implementación (SP1)
```

---

*Creado: 2026-03-16 — Semana 0, Fase 0*
*Mantenido por: Claude Cowork + Victor Valotto*
