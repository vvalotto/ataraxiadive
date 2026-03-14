# ADR-004: Reglas de competencia como datos configurables

| Campo | Valor |
|-------|-------|
| **Estado** | Aceptada |
| **Fecha** | 2026-03-14 |
| **Autores** | Victor Valotto |
| **Reemplaza** | — |

---

## Contexto

Las reglas de apnea competitiva cambian aproximadamente cada 2 años (actualización del
reglamento de la federación). Los cambios típicos incluyen: nuevas disciplinas, modificación
de penalizaciones por tarjeta amarilla, cambio en los criterios de ranking, nuevas categorías
por edad o género.

Si estas reglas están hardcodeadas en el código fuente, cada cambio de reglamento requiere
un ciclo de desarrollo, testing y despliegue — con riesgo de regresiones.

El atributo de calidad AC-CF-01 establece que el administrador debe poder agregar disciplinas
sin reiniciar el sistema. AC-CF-02 requiere que las penalizaciones sean configurables.

## Opciones Consideradas

**Opción A — Hardcoded en el dominio:** Las disciplinas (STA, DNF, DBF, DYN, SPE2X50) y sus
reglas están en constantes o enums en `domain/`. Cambiar una regla requiere modificar código.

**Opción B — Configuración en archivos (YAML/JSON):** Las reglas viven en archivos de
configuración versionados. Cambiar una regla requiere editar un archivo y hacer deploy.

**Opción C — Configuración como datos en base de datos:** Las reglas se almacenan como JSONB
en PostgreSQL. El administrador las modifica desde un panel sin intervención técnica.
El sistema las lee en runtime.

## Decisión

Se adopta **configuración como datos en base de datos (Opción C)** para disciplinas,
categorías y reglas de tarjetas.

Las reglas que son invariantes del dominio (ej: "una performance cerrada no puede
modificarse") siguen en el código — son parte del modelo, no configuración.

## Consecuencias

```mermaid
erDiagram
    DISCIPLINE_CONFIG {
        uuid id
        string code
        string name
        string measurement_type
        string unit
        string ranking_order
        jsonb rules
        bool active
    }

    CARD_RULE_CONFIG {
        uuid id
        string code
        string description
        float penalty_seconds
        float penalty_meters
        bool disqualifying
    }

    CATEGORY_CONFIG {
        uuid id
        string name
        int min_age
        int max_age
        string gender
    }
```

**Positivas:**
- El administrador puede agregar una disciplina nueva o modificar una penalización
  desde el panel sin tocar código ni hacer deploy (AC-CF-01, AC-CF-02)
- Los torneos futuros usan la configuración vigente; los torneos pasados conservan
  la configuración con la que se ejecutaron (snapshot al crear el torneo)
- JSONB en PostgreSQL permite esquemas flexibles para reglas que varían por disciplina

**Negativas:**
- La validación de las reglas configuradas es responsabilidad de la aplicación,
  no del compilador — se requieren tests exhaustivos de los valores de configuración
- El modelo de dominio necesita leer configuración en runtime, lo que introduce
  dependencia de infraestructura en los casos de uso (mitigado por inyección de dependencias)

**Riesgos:**
- Una configuración inválida puede romper una competencia en producción.
  Mitigación: validación estricta al guardar la configuración + tests de integración
  que cubran las combinaciones de reglas más comunes
