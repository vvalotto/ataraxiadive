# Complejidad Ciclomática (CC) por BC · Capa · Módulo — Backend Python
> Herramienta: `radon cc` v6.0.1  
> Fuente: `src/`  
> Fecha: 2026-05-18

**Escala:** A (1–5) · B (6–10) · C (11–15) · D (16–20) · E (21–25) · F (≥26)

---

## BC: `competencia`
**Totales:** 509 bloques · CC prom 1.80 (A) · CC máx 9 (B)

### Capa: `domain/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|
| `tarjeta_asignacion.py` | 5 | 5.2 | 7 | B | – |
| `resolucion_tarjeta.py` | 6 | 3.7 | 7 | A | – |
| `tarjeta_asignada.py` | 3 | 3.3 | 5 | A | – |
| `rp_final.py` | 3 | 3.3 | 4 | A | – |
| `grilla_de_salida.py` | 18 | 2.4 | 4 | A | – |
| `calculador_hash_competencia.py` | 3 | 2.3 | 3 | A | – |
| `performances_estado_port.py` | 4 | 2.0 | 3 | A | – |
| `intervalo_disciplina.py` | 3 | 2.0 | 3 | A | – |
| `penalizacion_tecnica.py` | 3 | 2.0 | 3 | A | – |
| `competencia.py` | 28 | 1.9 | 6 | A | – |
| `ap.py` | 4 | 1.8 | 3 | A | – |
| `performance.py` | 29 | 1.6 | 4 | A | – |
| `atleta_nombre_port.py` | 2 | 1.5 | 2 | A | – |
| `disciplina_descriptor_port.py` | 2 | 1.5 | 2 | A | – |
| `motivo_dq.py` | 2 | 1.5 | 2 | A | – |
| `ap_registrado.py` | 3 | 1.3 | 2 | A | – |
| `atleta_llamado.py` | 3 | 1.3 | 2 | A | – |
| `competencia_finalizada.py` | 3 | 1.3 | 2 | A | – |
| `competencia_iniciada.py` | 3 | 1.3 | 2 | A | – |
| `dns_registrado.py` | 3 | 1.3 | 2 | A | – |
| `grilla_confirmada.py` | 3 | 1.3 | 2 | A | – |
| `grilla_de_salida_ajustada.py` | 3 | 1.3 | 2 | A | – |
| `grilla_de_salida_generada.py` | 3 | 1.3 | 2 | A | – |
| `intervalo_ot_configurado.py` | 3 | 1.3 | 2 | A | – |
| `juez_performance_asignado.py` | 3 | 1.3 | 2 | A | – |
| `resultado_corregido.py` | 3 | 1.3 | 2 | A | – |
| `resultado_corregido_tras_dns.py` | 3 | 1.3 | 2 | A | – |
| `resultado_registrado.py` | 3 | 1.3 | 2 | A | – |
| `revision_resuelta.py` | 3 | 1.3 | 2 | A | – |
| `performances_ap_port.py` | 3 | 1.3 | 2 | A | – |
| `performance_state.py` | 10 | 1.3 | 2 | A | – |
| `performance_events.py` | 8 | 1.2 | 2 | A | – |
| `andariveles_activos_port.py` | 4 | 1.2 | 2 | A | – |
| `competencia_estado_port.py` | 4 | 1.2 | 2 | A | – |
| `competencias_por_torneo_port.py` | 5 | 1.2 | 2 | A | – |
| `exceptions.py` | 22 | 1.0 | 1 | A | – |
| `cambio_grilla.py` | 1 | 1.0 | 1 | A | – |
| `entrada_grilla.py` | 1 | 1.0 | 1 | A | – |
| `estado_competencia.py` | 1 | 1.0 | 1 | A | – |
| `estado_performance.py` | 1 | 1.0 | 1 | A | – |
| `tipo_penalizacion.py` | 1 | 1.0 | 1 | A | – |
| `tipo_tarjeta.py` | 1 | 1.0 | 1 | A | – |
| **subtotal** | **219** | **1.74** | **7** | **A** | |

### Capa: `application/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|
| `_p08_finalizacion.py` | 1 | 6.0 | 6 | B | – |
| `finalizar_competencia_manual.py` | 4 | 3.5 | 7 | A | – |
| `obtener_grilla.py` | 9 | 2.9 | 9 | A | – |
| `obtener_proximas_performances.py` | 8 | 2.6 | 6 | A | – |
| `obtener_performance_actual.py` | 7 | 2.6 | 4 | A | – |
| `configurar_intervalo_ot.py` | 5 | 2.2 | 4 | A | – |
| `obtener_progreso.py` | 5 | 2.2 | 4 | A | – |
| `registrar_dns.py` | 6 | 2.0 | 4 | A | – |
| `registrar_resultado.py` | 7 | 1.9 | 4 | A | – |
| `asignar_tarjeta.py` | 6 | 1.8 | 3 | A | – |
| `resolver_revision.py` | 6 | 1.8 | 3 | A | – |
| `obtener_eventos.py` | 6 | 1.8 | 3 | A | – |
| `obtener_audit_log.py` | 9 | 1.8 | 4 | A | – |
| `asignar_juez_performance.py` | 4 | 1.8 | 3 | A | – |
| `confirmar_grilla.py` | 4 | 1.8 | 3 | A | – |
| `iniciar_competencia.py` | 4 | 1.8 | 3 | A | – |
| `corregir_resultado.py` | 6 | 1.7 | 3 | A | – |
| `generar_grilla.py` | 6 | 1.7 | 3 | A | – |
| `ajustar_grilla.py` | 5 | 1.6 | 3 | A | – |
| `obtener_competencias_por_torneo.py` | 5 | 1.6 | 3 | A | – |
| `obtener_estado_competencia.py` | 5 | 1.6 | 3 | A | – |
| `registrar_ap.py` | 12 | 1.6 | 3 | A | – |
| `llamar_atleta.py` | 10 | 1.5 | 3 | A | – |
| `_handler_utils.py` | 6 | 1.3 | 2 | A | – |
| `obtener_andariveles_activos.py` | 4 | 1.2 | 2 | A | – |
| `corregir_resultado_tras_dns.py` | 5 | 1.2 | 2 | A | – |
| `_stream_ids.py` | 2 | 1.0 | 1 | A | – |
| **subtotal** | **157** | **1.92** | **9** | **A** | |

### Capa: `infrastructure/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|
| `performances_estado_adapter.py` | 3 | 4.0 | 6 | A | – |
| `andariveles_activos_adapter.py` | 5 | 3.4 | 5 | A | – |
| `performances_ap_adapter.py` | 4 | 2.5 | 4 | A | – |
| `atleta_nombre_adapter.py` | 3 | 2.3 | 3 | A | – |
| `competencia_estado_adapter.py` | 6 | 2.0 | 3 | A | – |
| `sqlite_competencias_por_torneo.py` | 6 | 1.7 | 2 | A | – |
| `disciplina_descriptor_adapter.py` | 2 | 1.5 | 2 | A | – |
| `competencia_estado_stub.py` | 4 | 1.2 | 2 | A | – |
| `env.py` | 2 | 1.0 | 1 | A | – |
| `0001_create_events_table.py` | 2 | 1.0 | 1 | A | – |
| **subtotal** | **37** | **2.16** | **6** | **A** | |

### Capa: `api/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|
| `router.py` | 75 | 1.8 | 6 | A | – |
| `dependencies.py` | 16 | 1.0 | 1 | A | – |
| `exception_handlers.py` | 1 | 1.0 | 1 | A | – |
| `schemas.py` | 4 | 1.0 | 1 | A | – |
| **subtotal** | **96** | **1.60** | **6** | **A** | |

### Capa: `raiz/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|

---

## BC: `torneo`
**Totales:** 142 bloques · CC prom 1.68 (A) · CC máx 5 (A)

### Capa: `domain/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|
| `disciplina_torneo.py` | 4 | 2.0 | 3 | A | – |
| `grupo_etario.py` | 2 | 2.0 | 3 | A | – |
| `torneo.py` | 21 | 1.8 | 3 | A | – |
| `torneo_repository_port.py` | 4 | 1.2 | 2 | A | – |
| `exceptions.py` | 9 | 1.0 | 1 | A | – |
| `entidad_organizadora.py` | 1 | 1.0 | 1 | A | – |
| `estado_torneo.py` | 1 | 1.0 | 1 | A | – |
| `sede.py` | 1 | 1.0 | 1 | A | – |
| `tipo_reglamento.py` | 1 | 1.0 | 1 | A | – |
| **subtotal** | **44** | **1.55** | **3** | **A** | |

### Capa: `application/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|
| `obtener_disciplinas_juez.py` | 3 | 2.0 | 3 | A | – |
| `actualizar_torneo.py` | 4 | 1.8 | 3 | A | – |
| `asignar_disciplinas.py` | 4 | 1.8 | 3 | A | – |
| `asignar_juez.py` | 4 | 1.8 | 3 | A | – |
| `transicionar_torneo.py` | 20 | 1.8 | 3 | A | – |
| `obtener_torneo.py` | 8 | 1.5 | 3 | A | – |
| `crear_torneo.py` | 4 | 1.2 | 2 | A | – |
| **subtotal** | **47** | **1.68** | **3** | **A** | |

### Capa: `infrastructure/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|
| `sqlite_torneo_repository.py` | 16 | 1.8 | 3 | A | – |
| **subtotal** | **16** | **1.81** | **3** | **A** | |

### Capa: `api/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|
| `router.py` | 34 | 1.8 | 5 | A | – |
| `exception_handlers.py` | 1 | 1.0 | 1 | A | – |
| **subtotal** | **35** | **1.80** | **5** | **A** | |

### Capa: `raiz/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|

---

## BC: `registro`
**Totales:** 211 bloques · CC prom 2.10 (A) · CC máx 13 (C)

### Capa: `domain/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|
| `atleta.py` | 4 | 9.0 | 13 | B | **2** ⚠ |
| `organizador.py` | 3 | 4.0 | 5 | A | – |
| `juez.py` | 4 | 3.0 | 4 | A | – |
| `inscripcion.py` | 9 | 2.3 | 3 | A | – |
| `ap_declarado.py` | 3 | 2.3 | 3 | A | – |
| `adjunto_storage_port.py` | 2 | 1.5 | 2 | A | – |
| `atleta_repository_port.py` | 4 | 1.2 | 2 | A | – |
| `juez_repository_port.py` | 4 | 1.2 | 2 | A | – |
| `organizador_repository_port.py` | 4 | 1.2 | 2 | A | – |
| `torneo_consulta_port.py` | 4 | 1.2 | 2 | A | – |
| `inscripcion_repository_port.py` | 7 | 1.1 | 2 | A | – |
| `exceptions.py` | 14 | 1.0 | 1 | A | – |
| `categoria.py` | 1 | 1.0 | 1 | A | – |
| `estado_inscripcion.py` | 1 | 1.0 | 1 | A | – |
| **subtotal** | **64** | **2.11** | **13** | **A** | |

### Capa: `application/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|
| `inscribir_atleta.py` | 4 | 3.5 | 7 | A | – |
| `verificar_completitud_ap.py` | 4 | 2.8 | 5 | A | – |
| `obtener_atleta.py` | 3 | 2.0 | 3 | A | – |
| `obtener_juez.py` | 3 | 2.0 | 3 | A | – |
| `obtener_organizador.py` | 3 | 2.0 | 3 | A | – |
| `actualizar_atleta.py` | 4 | 1.8 | 3 | A | – |
| `actualizar_juez.py` | 4 | 1.8 | 3 | A | – |
| `actualizar_organizador.py` | 4 | 1.8 | 3 | A | – |
| `cancelar_inscripcion.py` | 4 | 1.8 | 3 | A | – |
| `declarar_ap_inscripcion.py` | 4 | 1.8 | 3 | A | – |
| `registrar_atleta.py` | 4 | 1.8 | 3 | A | – |
| `registrar_juez.py` | 4 | 1.8 | 3 | A | – |
| `registrar_organizador.py` | 4 | 1.8 | 3 | A | – |
| `listar_inscriptos.py` | 3 | 1.3 | 2 | A | – |
| **subtotal** | **52** | **1.98** | **7** | **A** | |

### Capa: `infrastructure/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|
| `perfil_registro_adapter.py` | 3 | 4.3 | 7 | A | – |
| `sqlite_atleta_repository.py` | 9 | 2.7 | 5 | A | – |
| `local_adjunto_storage.py` | 3 | 2.3 | 3 | A | – |
| `sqlite_torneo_consulta.py` | 5 | 2.2 | 3 | A | – |
| `sqlite_inscripcion_repository.py` | 15 | 1.9 | 5 | A | – |
| `sqlite_juez_repository.py` | 7 | 1.6 | 2 | A | – |
| `sqlite_organizador_repository.py` | 7 | 1.6 | 2 | A | – |
| **subtotal** | **49** | **2.16** | **7** | **A** | |

### Capa: `api/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|
| `router.py` | 46 | 2.2 | 7 | A | – |
| **subtotal** | **46** | **2.15** | **7** | **A** | |

### Capa: `raiz/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|

---

## BC: `resultados`
**Totales:** 160 bloques · CC prom 2.61 (A) · CC máx 17 (D)

### Capa: `domain/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|
| `algoritmo_faas.py` | 8 | 4.8 | 10 | A | – |
| `ranking_overall.py` | 16 | 2.8 | 9 | A | – |
| `ranking_competencia.py` | 20 | 2.7 | 10 | A | – |
| `algoritmo_puntaje.py` | 2 | 1.5 | 2 | A | – |
| `resultados_competencia_port.py` | 5 | 1.4 | 2 | A | – |
| `ranking_overall_calculado.py` | 3 | 1.3 | 2 | A | – |
| `resultados_calculados.py` | 3 | 1.3 | 2 | A | – |
| `exceptions.py` | 5 | 1.0 | 1 | A | – |
| `entrada_overall.py` | 1 | 1.0 | 1 | A | – |
| `entrada_ranking.py` | 1 | 1.0 | 1 | A | – |
| **subtotal** | **64** | **2.53** | **10** | **A** | |

### Capa: `application/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|
| `obtener_ranking_provisional.py` | 8 | 6.5 | 17 | B | **2** ⚠ |
| `exportar_resultados.py` | 26 | 2.7 | 7 | A | – |
| `calcular_overall.py` | 6 | 2.3 | 4 | A | – |
| `obtener_ranking.py` | 6 | 2.0 | 4 | A | – |
| `calcular_ranking.py` | 8 | 1.9 | 3 | A | – |
| `obtener_overall.py` | 6 | 1.7 | 3 | A | – |
| **subtotal** | **60** | **2.90** | **17** | **A** | |

### Capa: `infrastructure/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|
| `resultados_competencia_adapter.py` | 12 | 2.4 | 4 | A | – |
| `atleta_categoria_adapter.py` | 3 | 2.3 | 3 | A | – |
| `atleta_info_adapter.py` | 4 | 2.0 | 3 | A | – |
| `disciplina_descriptor_adapter.py` | 2 | 1.5 | 2 | A | – |
| **subtotal** | **21** | **2.24** | **4** | **A** | |

### Capa: `api/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|
| `router.py` | 15 | 2.3 | 6 | A | – |
| **subtotal** | **15** | **2.33** | **6** | **A** | |

### Capa: `raiz/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|

---

## BC: `identidad`
**Totales:** 118 bloques · CC prom 2.11 (A) · CC máx 11 (C)

### Capa: `domain/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|
| `usuario.py` | 3 | 3.0 | 4 | A | – |
| `exceptions.py` | 28 | 1.5 | 2 | A | – |
| `perfil_registro_port.py` | 2 | 1.5 | 2 | A | – |
| `password_hashing_port.py` | 3 | 1.3 | 2 | A | – |
| `token_service_port.py` | 4 | 1.2 | 2 | A | – |
| `usuario_repository_port.py` | 6 | 1.2 | 2 | A | – |
| `rol.py` | 1 | 1.0 | 1 | A | – |
| **subtotal** | **47** | **1.51** | **4** | **A** | |

### Capa: `application/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|
| `reset_password.py` | 4 | 4.2 | 9 | A | – |
| `cambiar_password.py` | 4 | 3.2 | 6 | A | – |
| `registrar_usuario.py` | 8 | 3.1 | 11 | A | **1** ⚠ |
| `autenticar_usuario.py` | 6 | 2.7 | 7 | A | – |
| `solicitar_reset_password.py` | 4 | 1.8 | 3 | A | – |
| **subtotal** | **26** | **3.00** | **11** | **A** | |

### Capa: `infrastructure/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|
| `sqlite_usuario_repository.py` | 13 | 2.2 | 4 | A | – |
| `jwt_service.py` | 5 | 1.6 | 2 | A | – |
| `bcrypt_password_hasher.py` | 3 | 1.3 | 2 | A | – |
| **subtotal** | **21** | **1.90** | **4** | **A** | |

### Capa: `api/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|
| `router.py` | 16 | 2.9 | 10 | A | – |
| `dependencies.py` | 8 | 1.6 | 2 | A | – |
| **subtotal** | **24** | **2.50** | **10** | **A** | |

### Capa: `raiz/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|

---

## BC: `notificaciones`
**Totales:** 105 bloques · CC prom 2.06 (A) · CC máx 6 (B)

### Capa: `domain/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|
| `contenido_email.py` | 2 | 5.5 | 6 | B | – |
| `destinatario.py` | 2 | 4.5 | 5 | A | – |
| `evento_fuente_id.py` | 3 | 2.3 | 3 | A | – |
| `notificacion_id.py` | 3 | 2.0 | 3 | A | – |
| `notificacion.py` | 20 | 1.7 | 4 | A | – |
| `email_port.py` | 2 | 1.5 | 2 | A | – |
| `notificacion_enviada.py` | 3 | 1.3 | 2 | A | – |
| `notificacion_fallida.py` | 3 | 1.3 | 2 | A | – |
| `notificacion_solicitada.py` | 3 | 1.3 | 2 | A | – |
| `notificacion_repository.py` | 4 | 1.2 | 2 | A | – |
| `exceptions.py` | 4 | 1.0 | 1 | A | – |
| `canal_envio.py` | 1 | 1.0 | 1 | A | – |
| **subtotal** | **50** | **1.84** | **6** | **A** | |

### Capa: `application/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|
| `enviar_notificacion.py` | 4 | 2.8 | 5 | A | – |
| `politica_p10.py` | 6 | 2.2 | 4 | A | – |
| `_helpers.py` | 1 | 2.0 | 2 | A | – |
| `solicitar_envio.py` | 5 | 1.8 | 3 | A | – |
| `politica_p11.py` | 10 | 1.8 | 4 | A | – |
| **subtotal** | **26** | **2.04** | **5** | **A** | |

### Capa: `infrastructure/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|
| `resend_email_adapter.py` | 5 | 4.6 | 6 | A | – |
| `logging_email_adapter.py` | 2 | 4.5 | 5 | A | – |
| `sqlite_notificacion_event_store.py` | 7 | 2.1 | 3 | A | – |
| `resultados_publicados_template.py` | 7 | 1.9 | 3 | A | – |
| `sqlite_notificacion_repository.py` | 5 | 1.4 | 2 | A | – |
| `inscripcion_confirmada_template.py` | 3 | 1.3 | 2 | A | – |
| **subtotal** | **29** | **2.45** | **6** | **A** | |

### Capa: `api/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|

### Capa: `raiz/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|

---

## BC: `shared`
**Totales:** 35 bloques · CC prom 1.97 (A) · CC máx 9 (B)

### Capa: `domain/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|
| `tiempo_ap.py` | 3 | 6.0 | 9 | B | – |
| `disciplina_descriptor.py` | 4 | 2.2 | 3 | A | – |
| `domain_event.py` | 3 | 1.3 | 2 | A | – |
| `aggregate_root.py` | 4 | 1.2 | 2 | A | – |
| `disciplina.py` | 5 | 1.2 | 2 | A | – |
| `event_store_port.py` | 6 | 1.2 | 2 | A | – |
| `unidad_medida.py` | 1 | 1.0 | 1 | A | – |
| **subtotal** | **26** | **1.92** | **9** | **A** | |

### Capa: `infrastructure/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|
| `sqlite_event_store.py` | 9 | 2.1 | 4 | A | – |
| **subtotal** | **9** | **2.11** | **4** | **A** | |

### Capa: `api/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|

### Capa: `raiz/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|

---

## BC: `app`
**Totales:** 19 bloques · CC prom 3.58 (A) · CC máx 11 (C)

### Capa: `raiz/`
| Módulo | Bloques | CC Prom | CC Máx | Rank | Bloques C+ |
|--------|:-------:|:-------:|:------:|:----:|:----------:|
| `app.py` | 19 | 3.6 | 11 | A | **1** ⚠ |
| **subtotal** | **19** | **3.58** | **11** | **A** | |
