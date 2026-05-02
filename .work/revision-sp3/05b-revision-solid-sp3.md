# Revisión SOLID — Cierre SP3

**Fecha:** 2026-04-02
**Alcance:** BCs nuevos de SP3 (Torneo, Registro, Identidad, Resultados-ext)
**Herramienta:** Revisión manual de código

---

## Resumen ejecutivo

| Principio | BC más afectado | Severidad máx | Issues |
|-----------|-----------------|---------------|--------|
| SRP | Identidad | 🟡 | JWTService mezcla config + operación |
| OCP | Torneo, Resultados | 🔴 | `_DISCIPLINAS_SP3` hardcoded; event type literal |
| LSP | Registro | 🟡 | `obtener_disciplinas` no cumple contrato |
| ISP | — | ✅ | Sin violations |
| DIP | Identidad | 🔴 | Application depende de `JWTService` concreto + `bcrypt` directo |

---

## SRP — Single Responsibility Principle

### ✅ Correcto

- `Torneo` aggregate: 3 responsabilidades visibles (ciclo de vida, disciplinas, jueces), pero todas pertenecen al invariante del aggregate. Aceptable en DDD — el LCOM alto no implica violación de SRP si las responsabilidades son cohesivas con el aggregate raíz.
- `Inscripcion` aggregate: una sola responsabilidad (ciclo de vida de la inscripción). Correcto.
- `Atleta` aggregate: datos de identidad deportiva + validaciones de entrada. Correcto.
- `AutenticarUsuarioHandler`: orquesta autenticación en application layer. Correcto en concepto.

### ⚠️ Issues

**S-01** — `JWTService.__init__` lee variables de entorno directamente:

```python
# identidad/infrastructure/jwt_service.py
def __init__(self) -> None:
    secret = os.environ.get("IDENTIDAD_JWT_SECRET")  # ← config reading
    expiry_hours = int(os.environ.get("IDENTIDAD_JWT_EXPIRY_HOURS", 24))
    ...
```

El servicio tiene dos razones de cambio: (1) lógica de JWT y (2) cómo se obtiene la configuración.
Si mañana la config viene de Vault o de un archivo, el servicio cambia.

**Severidad:** 🟢 Menor — en infra layer, funciona, no bloquea nada.
**Corrección sugerida:** recibir `secret` y `expiry_hours` como parámetros en el constructor.
El lugar de lectura de env vars queda en el composition root (`app.py`).

---

## OCP — Open/Closed Principle

### ✅ Correcto

- `_TRANSICIONES_VALIDAS` dict en `Torneo`: el mapa de transiciones está externalizado. Para agregar estados, solo se modifica el dict sin tocar `_transicionar()`. Patrón correcto.
- `RankingOverall._apply_stored`: un solo event type por ahora — no hay match exhaustivo que rompa al agregar eventos.

### ❌ Issues

**O-01 — `_DISCIPLINAS_SP3` hardcodeado en dominio** ← CRÍTICO

```python
# torneo/domain/aggregates/torneo.py:38-44
_DISCIPLINAS_SP3 = {
    Disciplina.STA,
    Disciplina.DNF,
    Disciplina.DYN,
    Disciplina.DYNB,
    Disciplina.SPE2X50,
}

def asignar_disciplinas(self, disciplinas: frozenset[Disciplina]) -> None:
    invalidas = disciplinas - _DISCIPLINAS_SP3
    if invalidas:
        raise ValueError(f"Disciplinas no válidas para SP3: {invalidas}")
```

El nombre `_DISCIPLINAS_SP3` revela que esta restricción es **una decisión de implementación de sprint**, no una regla del dominio. El aggregate Torneo no debería saber qué disciplinas "son válidas para SP3".

Cuando SP4 agregue nuevas disciplinas (HS-19: fórmula de puntos configurable, posibles nuevas modalidades), este código necesitará modificación — violación directa de OCP.

**La regla real** del dominio es: "solo se pueden asignar disciplinas que existen en el sistema". Eso ya está garantizado por el tipo `Disciplina` (enum). La restricción "_SP3" es artificial.

**Severidad:** 🔴 Alta — el mensaje de error con "SP3" en producción es confuso y el código se rompe en SP4.

**Corrección sugerida:** eliminar la validación `invalidas`. El enum `Disciplina` ya garantiza que no se pasan valores inválidos. Si hay restricción por torneo en el futuro, viene de configuración externa, no hardcodeada.

---

**O-02 — Literal de event type hardcodeado en `CalcularOverallHandler`**

```python
# resultados/application/commands/calcular_overall.py:76
if event["event_type"] != "IntervaloOTConfigurado":
    continue
```

El handler usa un literal de string para identificar el evento que mapea competencia→torneo.
Si el event type cambia de nombre (refactor de dominio de Competencia), este handler se rompe silenciosamente — devuelve `{}` en vez de fallar explícitamente.

**Severidad:** 🟡 Moderada — funciona hoy, pero frágil ante cambios en el dominio de Competencia.

**Corrección sugerida:** extraer a una constante nombrada `_EVENTO_COMPETENCIA_CONFIGURADA = "IntervaloOTConfigurado"` y documentar la dependencia. Mejor aún: mover a un módulo de constantes compartidas de eventos.

---

## LSP — Liskov Substitution Principle

### ✅ Correcto

- `SQLiteTorneoRepository` implementa `TorneoRepositoryPort` honrando el contrato completo.
- `SQLiteInscripcionRepository` idem.
- `SQLiteUsuarioRepository` idem.

### ⚠️ Issues

**L-01 — `SQLiteTorneoConsulta.obtener_disciplinas` no cumple el contrato del port**

```python
# registro/infrastructure/acl/sqlite_torneo_consulta.py:44-55
async def obtener_disciplinas(self, torneo_id: UUID) -> frozenset[Disciplina]:
    # TODO US-3.4.1: Torneo aún no tiene campo disciplinas — se agrega en INC-3.4.
    # Hasta entonces retornamos todas las disciplinas disponibles (sin restricción).
    ...
    return frozenset(Disciplina)  # ← SIEMPRE devuelve TODAS las disciplinas
```

El contrato del port dice "retorna las disciplinas disponibles **para este torneo**".
La implementación retorna todas las disciplinas existentes independientemente del torneo.

`InscribirAtletaHandler` llama a `obtener_disciplinas` y luego valida que las disciplinas solicitadas estén dentro del set devuelto. Con esta implementación, **la validación de disciplinas por torneo nunca falla** — cualquier combinación de disciplinas es aceptada.

El TODO indica que se sabía: esto debía completarse en INC-3.4 (US-3.4.1). Sin embargo, SP3 cerró y el TODO persiste.

**Severidad:** 🟡 Moderada — la invariante INV-I-01 del dominio ("disciplinas deben estar habilitadas en el torneo") no se verifica en la práctica.

**Corrección:** en SP4 o SP-ADJ-03, leer `disciplinas_torneo` reales de la DB. La columna ya existe en SQLite (agregada en US-3.4.1).

---

## ISP — Interface Segregation Principle

### ✅ Sin violations

- `TorneoConsultaPort` (3 métodos): todos son usados por los handlers que dependen de él. Interfaz cohesiva.
- `UsuarioRepositoryPort`: mínimo (`save` + `find_by_email`). Correcto.
- `InscripcionRepositoryPort`: operaciones de inscripción. Cohesivo.
- `AtletaRepositoryPort`: operaciones de atleta. Cohesivo.

No se detectan interfaces "gordas" que fuerzen a implementar métodos innecesarios.

---

## DIP — Dependency Inversion Principle

### ✅ Correcto

- `InscribirAtletaHandler` depende de `InscripcionRepositoryPort` y `TorneoConsultaPort` — abstracciones. Correcto.
- `CalcularOverallHandler` depende de `EventStorePort` — abstracción. Correcto.
- `CrearTorneoHandler` depende de `TorneoRepositoryPort` — abstracción. Correcto.

### ❌ Issues

**D-01 — `AutenticarUsuarioHandler` recibe `JWTService` concreto** ← CRÍTICO

```python
# identidad/application/commands/autenticar_usuario.py
from identidad.infrastructure.jwt_service import JWTService   # ← infra en application

class AutenticarUsuarioHandler:
    def __init__(self, repo: UsuarioRepositoryPort, jwt_service: JWTService) -> None:
```

Application layer importa e instancia un tipo de `infrastructure/`. Violación de la Regla de Oro.
Si se cambia de PyJWT a python-jose, o se agrega un proveedor externo (Auth0), hay que modificar el handler.

**Corrección:** crear `identidad/domain/ports/token_service_port.py` con:
```python
class TokenServicePort(ABC):
    @abstractmethod
    def generate(self, usuario: Usuario) -> str: ...
    @abstractmethod
    def verify(self, token: str) -> dict: ...
```
`JWTService` implementa ese port. El handler recibe `TokenServicePort`.

**Severidad:** 🔴 Alta — viola la Regla de Oro directamente. Patrón incorrecto que se replica si se agregan handlers de identidad.

---

**D-02 — `RegistrarUsuarioHandler` llama `bcrypt` directamente** ← CRÍTICO

```python
# identidad/application/commands/registrar_usuario.py
import bcrypt                                    # ← biblioteca de infra en application

password_hash = bcrypt.hashpw(cmd.password.encode(), bcrypt.gensalt()).decode()
```

La capa application depende de la biblioteca `bcrypt` directamente. La misma violación que D-01: si se cambia el algoritmo de hashing, hay que modificar el handler.

**Corrección:** el port `TokenServicePort` puede extenderse, o crear un `PasswordHashingPort`:
```python
class PasswordHashingPort(ABC):
    @abstractmethod
    def hash(self, plain: str) -> str: ...
    @abstractmethod
    def verify(self, plain: str, hashed: str) -> bool: ...
```
`BcryptPasswordHashing` implementa en infra. Ambos handlers reciben el port.
Bonus: `AutenticarUsuarioHandler` también usa `bcrypt.checkpw` → mismo fix.

**Severidad:** 🔴 Alta — misma violación que D-01, mismo handler que ya tiene D-01.

---

**D-03 — `identidad/api/dependencies.py` instancia `JWTService()` inline**

```python
# identidad/api/dependencies.py
async def get_current_user(token: ...) -> dict:
    jwt_svc = JWTService()   # ← nueva instancia por cada request
    return jwt_svc.verify(token)
```

Dos problemas: (1) crea un `JWTService` nuevo en cada request — ineficiente y no testeable por inyección;
(2) la dependencia concreta no está abstraída.

**Severidad:** 🟡 Moderada — funciona pero dificulta el testing del layer API y es ineficiente.

**Corrección:** usar `Depends()` con un proveedor singleton, o inyectar via el composition root.

---

## Consolidado por BC

| BC | SRP | OCP | LSP | ISP | DIP | Issues totales |
|----|-----|-----|-----|-----|-----|----------------|
| **Torneo** | ✅ | 🔴 O-01 | ✅ | ✅ | ✅ | 1 crítico |
| **Registro** | ✅ | ✅ | 🟡 L-01 | ✅ | ✅ | 1 moderado |
| **Identidad** | 🟢 S-01 | ✅ | ✅ | ✅ | 🔴 D-01+D-02+D-03 | 3 (2 críticos) |
| **Resultados** | ✅ | 🟡 O-02 | ✅ | ✅ | ✅ | 1 moderado |

---

## Issues a incorporar en SP-ADJ-03

| ID | Nuevo en revisión SOLID | Agrega a | US sugerida |
|----|------------------------|----------|-------------|
| SOLID-01 | Eliminar `_DISCIPLINAS_SP3` de `Torneo` | US-ADJ-3.1 (domain/) | junto con GrillaDeSalida |
| SOLID-02 | `TokenServicePort` + `PasswordHashingPort` en `identidad/domain/ports/` | nueva US-ADJ-3.6 | identidad application refactor |
| SOLID-03 | Fix `JWTService()` inline en `dependencies.py` | US-ADJ-3.6 | junto con anterior |
| SOLID-04 | Constante `_EVENTO_COMPETENCIA_CONFIGURADA` en `calcular_overall.py` | US-ADJ-3.3 | app.py / constants |
| SOLID-05 | Completar `obtener_disciplinas` con datos reales | SP4 | no urgente — datos ya en DB |

---

*Creado: 2026-04-02 — Revisión SOLID SP3*
*Análisis ejecutado por: Claude Code + Victor Valotto*
