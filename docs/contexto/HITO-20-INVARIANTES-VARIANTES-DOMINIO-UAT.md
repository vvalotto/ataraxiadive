# HITO-20 — Los invariantes de dominio asumen condiciones que no aplican a todas las variantes — el UAT end-to-end es el único oráculo que lo detecta

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-20 — Hallazgo metodológico durante UAT de SP4 |
| **Fecha** | 2026-04-12 |
| **Sprint** | SP4 — La Plataforma — INC-4.3 |
| **Relacionado** | `src/competencia/domain/value_objects/tarjeta_asignacion.py` · `docs/design/ux/mejoras-ux.md` · HITO-17 |

---

## Contexto

Durante el UAT de SP4 se ejecutó el flujo completo del juez usando datos reales de
Buenos Aires 2025. Al intentar registrar un BKO (black-out) en una performance de STA
(Static Apnea — disciplina de tiempo), el backend rechazó la solicitud con un error 422:

```
DistanciaBlackoutObligatoria: Tarjeta roja por blackout requiere distancia_blackout > 0 (INV-DQ-01)
```

El invariante INV-DQ-01 había sido especificado, implementado, y cubierto por tests
unitarios. Pasó todos los quality gates. Y aun así falló en producción-UAT.

---

## El invariante que era correcto y estaba incompleto

INV-DQ-01 establece:

> Cuando `MotivoDQ` requiere distancia de blackout (`BKO_SUPERFICIE`, `BKO_SUBACUATICO`),
> la tarjeta roja debe incluir `distancia_blackout > 0`.

La lógica es correcta para disciplinas dinámicas (DYNB, DNF, CWT, FIM, NLT): si un
atleta hace un black-out a mitad de recorrido, la distancia hasta donde llegó es dato
esencial del evento. Sin ese dato, el resultado es incompleto.

Pero STA es una disciplina de tiempo, no de distancia. En STA:
- El `ap_declarado` es un tiempo (mm:ss), no una distancia
- El `rp_medido` es un tiempo, no una distancia
- Si ocurre un BKO en STA, la "distancia de blackout" no tiene significado físico

El invariante fue especificado pensando en el caso más común (disciplinas dinámicas)
sin condicionar explícitamente la excepción para la única disciplina temporal del deporte.

---

## Por qué los tests no lo detectaron

Los tests unitarios de `TarjetaAsignacion` cubrían:

- BKO con `distancia_blackout` presente → válido ✅
- BKO sin `distancia_blackout` → `DistanciaBlackoutObligatoria` ✅
- Tarjeta blanca con `distancia_blackout` → `DistanciaBlackoutNoAplica` ✅

Lo que no cubrían:

- BKO en STA → caso no contemplado en la suite

Los tests de integración de la API tampoco: los fixtures usaban disciplinas dinámicas
por defecto. La disciplina STA existía en el dominio y en los datos reales, pero no
en los escenarios de test para BKO.

Este es el patrón: **los tests cubren los casos que el autor del test imaginó**.
El UAT con escenarios reales cubre los casos que los usuarios reales ejecutan.

---

## El segundo hallazgo: el UI pedía un dato que ya existía

Al analizar el problema de UX asociado (MUX-04), se descubrió una segunda capa:

El frontend tenía un campo de texto libre para que el juez ingresara manualmente la
`distanciaBlackout` en metros. Ese campo era redundante: la distancia ya estaba
capturada en el `RpSelector` (pasos 5 y 4-BKO). El dominio ya tenía el dato.

La solución no fue mejorar el campo — fue eliminarlo y derivar el valor:

```python
# En la mutación del frontend
distanciaBlackout: isSTA ? undefined : buildRpValue(metros, centimetros)

# En resolver_revision()
distancia_blackout = self._rp_medido if motivo_dq.requiere_distancia_blackout() else None
```

Esto revela una regla de diseño de UI para sistemas orientados a dominio:

> Si el dominio ya tiene el dato, la UI no debe pedirlo de nuevo.
> La UI es un traductor del estado del dominio al usuario, no una fuente alternativa
> de datos del dominio.

El juez no debería saber qué es `distanciaBlackout` ni tener que ingresarla.
El juez ingresó los metros con el selector. El sistema los usa.

---

## El aprendizaje metodológico central

### Sobre invariantes

> Los invariantes de dominio se especifican sobre el caso general. Las variantes del
> deporte introducen excepciones que no siempre son visibles en la fase de especificación.
> El UAT end-to-end con escenarios reales es el único punto del proceso donde estas
> excepciones emergen de forma confiable.

La solución técnica es sencilla (agregar `es_disciplina_tiempo` a `TarjetaAsignacion`).
El problema metodológico es más profundo: ¿cómo anticipar qué variantes del dominio
condicionan a los invariantes antes de que el UAT los exponga?

Una heurística que emerge de este caso:

**Al especificar un invariante, preguntar explícitamente: ¿aplica igual a todas las
variantes de la disciplina? ¿Hay alguna variante donde el invariante cambia de forma?**

En este proyecto, STA es la única disciplina temporal. Esa particularidad debería
haber sido parte de la especificación de INV-DQ-01. No lo fue porque la especificación
se escribió desde el caso dinámico.

### Sobre la cadena de detección

```
Especificación  →  Tests unitarios  →  Tests integración  →  UAT end-to-end
     ↑                  ↑                     ↑                     ↑
Detecta:          Detecta:             Detecta:              Detecta:
invariantes       lógica del           contratos             variantes reales
incompletos       caso nominal         entre capas           del dominio
(si se           (feliz y              (happy path           (todos los
pregunta         alternativo)          completo)             escenarios
bien)                                                        de uso)
```

Cada nivel detecta lo que el anterior no ve. El UAT no reemplaza a los tests;
cierra el espacio que los tests no pueden cubrir porque ese espacio depende
de qué escenarios reales existen, no de qué escenarios el programador imaginó.

---

## Implicancia para la plantilla US-IEDD

La plantilla US-IEDD incluye invariantes formales. Debería incluir también:

```
## Variantes del dominio

¿Este invariante aplica igual a todas las variantes de disciplina/rol/estado?
Si no: ¿qué variantes tienen comportamiento diferente y cuál es ese comportamiento?

Ejemplo:
- INV-DQ-01 aplica a disciplinas dinámicas (DYNB, DNF, CWT, FIM, NLT)
- Para STA: distancia_blackout = None (la disciplina no tiene dimensión espacial)
```

Esta sección no es obligatoria cuando el invariante es verdaderamente uniforme.
Pero cuando la US-IEDD afecta a un aggregate que opera en múltiples disciplinas,
omitirla es un riesgo metodológico real.

---

## Conexión con HITO-17

HITO-17 estableció que los datos reales de Buenos Aires 2025 son el oráculo empírico
del dominio: revelan variantes, edge cases y convenciones que la especificación no
documenta explícitamente.

HITO-20 extiende ese principio al plano de los invariantes:

> No solo los **datos** reales revelan el dominio. También los **escenarios** reales.
> Un atleta de STA que sufre un BKO es un escenario real, frecuente en competencia,
> que no fue imaginado al especificar INV-DQ-01.

El oráculo empírico opera en dos niveles:
- **Datos reales** → revelan valores, rangos, convenciones del dominio (HITO-17)
- **Escenarios reales** → revelan variantes de los invariantes del dominio (HITO-20)

Ambos niveles solo se activan cuando el UAT usa datos y escenarios del deporte real,
no fixtures artificiales diseñados para cubrir el caso nominal.

---

## Acciones incorporadas

- [x] `TarjetaAsignacion` condiciona INV-DQ-01 según `es_disciplina_tiempo`
- [x] `resolver_revision()` deriva `distancia_blackout` desde `rp_medido`
- [x] Campo `distanciaBlackout` eliminado del UI — derivado automáticamente
- [x] `mejoras-ux.md` creado como registro persistente de deuda UX
- [ ] Evaluar si la plantilla US-IEDD debe incluir sección "Variantes del dominio"
- [ ] Revisar otros invariantes del BC Competencia que podrían tener excepciones STA

---

*Registrado post-UAT SP4 INC-4.3 — el BKO en STA que expuso la frontera entre el caso nominal y la variante real del deporte*
