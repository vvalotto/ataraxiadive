---
title: "Registro — Command Handlers"
type: arquitectura-componente
bc: registro
capa: application
tipo_componente: handler
responsabilidad: "10 handlers de comando para los 3 roles (registrar/actualizar) + inscripción (inscribir, cancelar, declarar AP)"
interfaces_out:
  - AtletaRepositoryPort
  - JuezRepositoryPort
  - OrganizadorRepositoryPort
  - InscripcionRepositoryPort
  - TorneoConsultaPort
adr_refs: [ADR-005, ADR-007, ADR-020]
last_updated: "2026-05-23"
sources:
  - src/registro/application/commands/registrar_atleta.py
  - src/registro/application/commands/actualizar_atleta.py
  - src/registro/application/commands/registrar_juez.py
  - src/registro/application/commands/actualizar_juez.py
  - src/registro/application/commands/registrar_organizador.py
  - src/registro/application/commands/actualizar_organizador.py
  - src/registro/application/commands/inscribir_atleta.py
  - src/registro/application/commands/cancelar_inscripcion.py
  - src/registro/application/commands/declarar_ap_inscripcion.py
us_origen:
  - US-3.2.3-aggregate-inscripcion-inscribir-cancelar-y-listar
  - US-5.5.1-portal-atleta-completo-shell-inscripcion-ap
  - US-6.3.2-inscripcion-atleta-ap-inline-apto-medico-constancia
  - US-6.4.5-refactoring-declarar-ap-inscripcion-handler-sq-lite
  - US-ADJ-10.2-pagina-mis-datos-del-atleta-patch-registro-atletas-me
  - US-ADJ-11.10-creacion-automatica-de-perfiles-al-registrarse
  - US-ADJ-11.4-entidad-juez-juez-repository-port-endpoints-registro
  - US-ADJ-11.5-entidad-organizador-organizador-repository-port
  - US-ADJ-9.7-sp-adj-09-declarar-ap-en-el-wizard-de-inscripcion
---

# Command Handlers — BC Registro

BC Registro es CRUD puro: los handlers son simples orquestadores sin Event Sourcing.

---

## Handlers de perfil de Atleta

### RegistrarAtletaHandler

| Campo | Detalle |
|-------|---------|
| Command | `RegistrarAtletaCommand(nombre, apellido, email, [fecha_nacimiento, categoria, club, brevet, dni, telefono])` |
| Retorna | `UUID` del atleta creado |
| Guarda | `atleta_id = uuid4()` |
| Excepción | `AtletaYaRegistrado` si ya existe email |

### ActualizarAtletaHandler

Busca por email (del JWT), aplica `atleta.actualizar(...)`, persiste. Lanza `AtletaNoEncontrado`.

---

## Handlers de perfil de Juez

### RegistrarJuezHandler

| Campo | Detalle |
|-------|---------|
| Command | `RegistrarJuezCommand(email, [numero_licencia, federacion])` |
| Retorna | `UUID` del juez creado |
| Excepción | `JuezYaRegistrado` si ya existe email |

### ActualizarJuezHandler

Busca por email, aplica `juez.actualizar(...)`, persiste. Lanza `JuezNoEncontrado`.

---

## Handlers de perfil de Organizador

### RegistrarOrganizadorHandler

| Campo | Detalle |
|-------|---------|
| Command | `RegistrarOrganizadorCommand(email, [nombre_organizacion])` |
| Retorna | `UUID` del organizador creado |
| Excepción | `OrganizadorYaRegistrado` si ya existe email |

### ActualizarOrganizadorHandler

Busca por email, aplica `organizador.actualizar(...)`, persiste. Lanza `OrganizadorNoEncontrado`.

---

## Handlers de Inscripción

### InscribirAtletaHandler

El handler más complejo — valida 4 invariantes contra el aggregate y la ACL:

```
INV-I-05: cmd.disciplinas no puede ser vacío
INV-I-02: torneo_consulta.esta_abierto_para_inscripcion()
INV-I-01: disciplinas ⊆ disciplinas_disponibles_del_torneo
INV-I-04: no existe inscripción previa del atleta en ese torneo
```

Acepta callback opcional `on_inscripcion_confirmada: Callable[[Inscripcion], Awaitable[None]]` para notificaciones — si falla el callback, se ignora (no afecta la inscripción).

### CancelarInscripcionHandler

```
1. find_by_id o lanza InscripcionNoEncontrada
2. fecha_inicio = torneo_consulta.obtener_fecha_inicio(torneo_id)
3. inscripcion.cancelar(fecha_actual, fecha_inicio)  ← INV-I-03
4. repo.save(inscripcion)
```

Lanza `PlazoCancelacionVencido` si `fecha_actual >= fecha_inicio`.

### DeclararAPInscripcionHandler

```
1. find_by_id o lanza InscripcionNoEncontrada
2. inscripcion.declarar_ap(disciplina, APDeclarado(valor, unidad))
   ← lanza DisciplinaNoInscripta o ValueError si unidad inválida
3. repo.save(inscripcion)
```

---

## Relaciones

**Contenedor:** [[arquitectura/registro]]

- Los handlers de perfil son instanciados por [[perfil-registro-adapter]] (ruta de registro inicial)
- Los handlers de inscripción son instanciados directamente en [[router-registro]]
- Usan [[sqlite-repositories-registro]] como puertos de persistencia
- `InscribirAtletaHandler` y `CancelarInscripcionHandler` usan [[torneo-consulta-port]]

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/registro/application/commands/registrar_atleta.py` | Handler: RegistrarAtletaHandler |
| `src/registro/application/commands/actualizar_atleta.py` | Handler: ActualizarAtletaHandler |
| `src/registro/application/commands/registrar_juez.py` | Handler: RegistrarJuezHandler |
| `src/registro/application/commands/actualizar_juez.py` | Handler: ActualizarJuezHandler |
| `src/registro/application/commands/registrar_organizador.py` | Handler: RegistrarOrganizadorHandler |
| `src/registro/application/commands/actualizar_organizador.py` | Handler: ActualizarOrganizadorHandler |
| `src/registro/application/commands/inscribir_atleta.py` | Handler: InscribirAtletaHandler |
| `src/registro/application/commands/cancelar_inscripcion.py` | Handler: CancelarInscripcionHandler |
| `src/registro/application/commands/declarar_ap_inscripcion.py` | Handler: DeclararAPInscripcionHandler |
