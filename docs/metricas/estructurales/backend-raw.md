# Métricas RAW por BC · Capa · Módulo — Backend Python
> Herramienta: `radon raw` v6.0.1  
> Fuente: `src/`  
> Fecha: 2026-05-18

---

## BC: `competencia`
**Totales:** 8346 LOC · 5305 SLOC · 103 archivos

### Capa: `domain/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| `performance.py` | 545 | 353 | 73 | 9 |
| `competencia.py` | 502 | 322 | 74 | 8 |
| `grilla_de_salida.py` | 283 | 252 | 29 | 0 |
| `performance_events.py` | 211 | 191 | 19 | 0 |
| `exceptions.py` | 126 | 23 | 52 | 2 |
| `resolucion_tarjeta.py` | 108 | 88 | 14 | 0 |
| `performance_state.py` | 92 | 66 | 23 | 2 |
| `tarjeta_asignada.py` | 88 | 62 | 11 | 0 |
| `andariveles_activos_port.py` | 80 | 28 | 18 | 0 |
| `competencia_finalizada.py` | 76 | 45 | 12 | 0 |
| `tarjeta_asignacion.py` | 73 | 60 | 10 | 1 |
| `resultado_corregido.py` | 72 | 45 | 10 | 0 |
| `revision_resuelta.py` | 64 | 54 | 8 | 0 |
| `resultado_registrado.py` | 63 | 39 | 10 | 0 |
| `atleta_llamado.py` | 62 | 39 | 10 | 0 |
| `ap_registrado.py` | 59 | 36 | 10 | 0 |
| `dns_registrado.py` | 59 | 36 | 10 | 0 |
| `resultado_corregido_tras_dns.py` | 58 | 42 | 9 | 0 |
| `grilla_de_salida_generada.py` | 57 | 33 | 10 | 0 |
| `performances_estado_port.py` | 57 | 20 | 15 | 0 |
| `intervalo_ot_configurado.py` | 55 | 33 | 10 | 0 |
| `competencia_estado_port.py` | 55 | 11 | 16 | 0 |
| `competencia_iniciada.py` | 54 | 30 | 11 | 0 |
| `performances_ap_port.py` | 54 | 15 | 15 | 0 |
| `grilla_de_salida_ajustada.py` | 53 | 30 | 10 | 0 |
| `grilla_confirmada.py` | 50 | 27 | 11 | 0 |
| `juez_performance_asignado.py` | 43 | 33 | 8 | 0 |
| `competencias_por_torneo_port.py` | 39 | 23 | 10 | 0 |
| `rp_final.py` | 38 | 24 | 10 | 0 |
| `__init__.py` | 36 | 33 | 2 | 0 |
| `ap.py` | 36 | 14 | 12 | 0 |
| `calculador_hash_competencia.py` | 33 | 23 | 7 | 0 |
| `entrada_grilla.py` | 31 | 12 | 7 | 0 |
| `intervalo_disciplina.py` | 30 | 9 | 11 | 0 |
| `disciplina_descriptor_port.py` | 28 | 7 | 9 | 0 |
| `atleta_nombre_port.py` | 26 | 6 | 8 | 0 |
| `penalizacion_tecnica.py` | 24 | 13 | 8 | 0 |
| `__init__.py` | 23 | 20 | 2 | 0 |
| `__init__.py` | 22 | 19 | 2 | 0 |
| `cambio_grilla.py` | 22 | 9 | 6 | 0 |
| `estado_performance.py` | 22 | 9 | 6 | 6 |
| `motivo_dq.py` | 20 | 11 | 6 | 0 |
| `tipo_tarjeta.py` | 20 | 7 | 6 | 0 |
| `estado_competencia.py` | 18 | 7 | 6 | 0 |
| `tipo_penalizacion.py` | 14 | 7 | 5 | 0 |
| `__init__.py` | 5 | 2 | 2 | 0 |
| `event_store_port.py` | 5 | 2 | 2 | 0 |
| `__init__.py` | 5 | 2 | 2 | 0 |
| `disciplina.py` | 5 | 2 | 2 | 0 |
| `disciplina_descriptor.py` | 5 | 2 | 2 | 0 |
| `unidad_medida.py` | 5 | 2 | 2 | 0 |
| `__init__.py` | 1 | 0 | 0 | 0 |
| **subtotal** | **3612** | **2278** | | |

### Capa: `application/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| `registrar_ap.py` | 187 | 100 | 44 | 5 |
| `asignar_tarjeta.py` | 151 | 91 | 29 | 3 |
| `llamar_atleta.py` | 146 | 75 | 33 | 4 |
| `generar_grilla.py` | 138 | 81 | 24 | 3 |
| `obtener_grilla.py` | 138 | 109 | 20 | 1 |
| `registrar_dns.py` | 121 | 55 | 32 | 7 |
| `registrar_resultado.py` | 120 | 52 | 33 | 6 |
| `corregir_resultado.py` | 112 | 47 | 30 | 6 |
| `resolver_revision.py` | 108 | 86 | 18 | 0 |
| `configurar_intervalo_ot.py` | 105 | 49 | 27 | 3 |
| `obtener_proximas_performances.py` | 104 | 68 | 23 | 2 |
| `finalizar_competencia_manual.py` | 102 | 72 | 18 | 0 |
| `obtener_audit_log.py` | 93 | 64 | 22 | 1 |
| `obtener_performance_actual.py` | 92 | 60 | 21 | 2 |
| `ajustar_grilla.py` | 84 | 32 | 25 | 3 |
| `_handler_utils.py` | 76 | 53 | 16 | 0 |
| `_p08_finalizacion.py` | 71 | 45 | 12 | 0 |
| `corregir_resultado_tras_dns.py` | 70 | 53 | 12 | 0 |
| `iniciar_competencia.py` | 66 | 30 | 17 | 0 |
| `confirmar_grilla.py` | 65 | 29 | 17 | 0 |
| `obtener_eventos.py` | 64 | 35 | 16 | 4 |
| `obtener_progreso.py` | 61 | 36 | 17 | 1 |
| `obtener_andariveles_activos.py` | 60 | 22 | 18 | 2 |
| `obtener_estado_competencia.py` | 59 | 37 | 14 | 1 |
| `obtener_competencias_por_torneo.py` | 43 | 25 | 13 | 0 |
| `asignar_juez_performance.py` | 42 | 31 | 10 | 0 |
| `__init__.py` | 37 | 34 | 2 | 0 |
| `_stream_ids.py` | 30 | 10 | 9 | 0 |
| **subtotal** | **2545** | **1481** | | |

### Capa: `infrastructure/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| `andariveles_activos_adapter.py` | 134 | 78 | 24 | 1 |
| `sqlite_competencias_por_torneo.py` | 104 | 89 | 13 | 0 |
| `performances_estado_adapter.py` | 69 | 39 | 16 | 0 |
| `performances_ap_adapter.py` | 66 | 55 | 9 | 0 |
| `env.py` | 50 | 31 | 13 | 0 |
| `competencia_estado_adapter.py` | 49 | 20 | 15 | 0 |
| `0001_create_events_table.py` | 47 | 33 | 9 | 0 |
| `competencia_estado_stub.py` | 38 | 11 | 12 | 0 |
| `atleta_nombre_adapter.py` | 33 | 18 | 9 | 0 |
| `disciplina_descriptor_adapter.py` | 15 | 7 | 5 | 0 |
| `__init__.py` | 8 | 5 | 2 | 0 |
| `sqlite_event_store.py` | 8 | 5 | 2 | 0 |
| **subtotal** | **621** | **391** | | |

### Capa: `api/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| `router.py` | 1322 | 1003 | 198 | 7 |
| `dependencies.py` | 182 | 121 | 44 | 0 |
| `schemas.py` | 35 | 15 | 15 | 0 |
| `exception_handlers.py` | 29 | 16 | 7 | 0 |
| **subtotal** | **1568** | **1155** | | |

### Capa: `raiz/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| **subtotal** | **0** | **0** | | |

---

## BC: `torneo`
**Totales:** 19760 LOC · 14015 SLOC · 31 archivos

### Capa: `domain/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| `__init__.py` | 18429 | 12961 | 3462 | 187 |
| `torneo.py` | 173 | 138 | 30 | 0 |
| `exceptions.py` | 34 | 18 | 16 | 0 |
| `disciplina_torneo.py` | 31 | 19 | 9 | 0 |
| `grupo_etario.py` | 20 | 13 | 7 | 0 |
| `__init__.py` | 17 | 16 | 1 | 0 |
| `torneo_repository_port.py` | 15 | 10 | 5 | 0 |
| `estado_torneo.py` | 11 | 9 | 2 | 0 |
| `sede.py` | 8 | 6 | 2 | 0 |
| `entidad_organizadora.py` | 7 | 5 | 2 | 1 |
| `tipo_reglamento.py` | 7 | 5 | 2 | 0 |
| `__init__.py` | 6 | 5 | 1 | 0 |
| `__init__.py` | 3 | 2 | 1 | 0 |
| **subtotal** | **18761** | **13207** | | |

### Capa: `application/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| `transicionar_torneo.py` | 85 | 61 | 24 | 0 |
| `crear_torneo.py` | 45 | 38 | 7 | 0 |
| `actualizar_torneo.py` | 42 | 35 | 7 | 0 |
| `obtener_torneo.py` | 37 | 25 | 12 | 0 |
| `asignar_juez.py` | 29 | 20 | 8 | 0 |
| `asignar_disciplinas.py` | 28 | 19 | 8 | 0 |
| `__init__.py` | 24 | 23 | 1 | 0 |
| `obtener_disciplinas_juez.py` | 20 | 13 | 6 | 0 |
| `__init__.py` | 13 | 12 | 1 | 0 |
| **subtotal** | **323** | **246** | | |

### Capa: `infrastructure/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| `sqlite_torneo_repository.py` | 175 | 152 | 23 | 1 |
| `__init__.py` | 3 | 2 | 1 | 0 |
| **subtotal** | **178** | **154** | | |

### Capa: `api/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| `router.py` | 383 | 304 | 74 | 8 |
| `exception_handlers.py` | 112 | 102 | 10 | 0 |
| `__init__.py` | 3 | 2 | 1 | 0 |
| **subtotal** | **498** | **408** | | |

### Capa: `raiz/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| **subtotal** | **0** | **0** | | |

---

## BC: `registro`
**Totales:** 2353 LOC · 1907 SLOC · 50 archivos

### Capa: `domain/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| `inscripcion.py` | 83 | 68 | 13 | 0 |
| `atleta.py` | 79 | 70 | 9 | 0 |
| `exceptions.py` | 54 | 28 | 26 | 0 |
| `juez.py` | 38 | 30 | 8 | 0 |
| `inscripcion_repository_port.py` | 28 | 19 | 9 | 0 |
| `organizador.py` | 26 | 19 | 6 | 0 |
| `ap_declarado.py` | 24 | 18 | 6 | 0 |
| `torneo_consulta_port.py` | 20 | 12 | 7 | 0 |
| `atleta_repository_port.py` | 17 | 11 | 6 | 0 |
| `juez_repository_port.py` | 17 | 11 | 6 | 0 |
| `organizador_repository_port.py` | 17 | 11 | 6 | 0 |
| `adjunto_storage_port.py` | 16 | 13 | 3 | 0 |
| `categoria.py` | 12 | 9 | 3 | 0 |
| `estado_inscripcion.py` | 8 | 5 | 3 | 0 |
| **subtotal** | **439** | **324** | | |

### Capa: `application/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| `inscribir_atleta.py` | 71 | 60 | 11 | 4 |
| `registrar_atleta.py` | 48 | 40 | 8 | 1 |
| `verificar_completitud_ap.py` | 46 | 39 | 7 | 0 |
| `actualizar_atleta.py` | 44 | 37 | 7 | 0 |
| `cancelar_inscripcion.py` | 34 | 26 | 8 | 0 |
| `registrar_juez.py` | 34 | 26 | 8 | 0 |
| `registrar_organizador.py` | 34 | 26 | 8 | 0 |
| `actualizar_juez.py` | 30 | 22 | 8 | 1 |
| `actualizar_organizador.py` | 29 | 20 | 9 | 0 |
| `declarar_ap_inscripcion.py` | 28 | 21 | 7 | 0 |
| `obtener_atleta.py` | 18 | 13 | 5 | 0 |
| `obtener_juez.py` | 16 | 12 | 4 | 0 |
| `obtener_organizador.py` | 16 | 12 | 4 | 0 |
| `listar_inscriptos.py` | 14 | 9 | 5 | 0 |
| **subtotal** | **462** | **363** | | |

### Capa: `infrastructure/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| `sqlite_inscripcion_repository.py` | 174 | 149 | 25 | 0 |
| `sqlite_atleta_repository.py` | 141 | 123 | 14 | 4 |
| `sqlite_juez_repository.py` | 77 | 64 | 12 | 1 |
| `perfil_registro_adapter.py` | 76 | 69 | 7 | 0 |
| `sqlite_organizador_repository.py` | 74 | 61 | 12 | 1 |
| `sqlite_torneo_consulta.py` | 55 | 42 | 10 | 2 |
| `local_adjunto_storage.py` | 26 | 21 | 5 | 0 |
| `__init__.py` | 1 | 0 | 0 | 0 |
| **subtotal** | **624** | **529** | | |

### Capa: `api/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| `router.py` | 828 | 691 | 125 | 18 |
| **subtotal** | **828** | **691** | | |

### Capa: `raiz/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| **subtotal** | **0** | **0** | | |

---

## BC: `resultados`
**Totales:** 2662 LOC · 1801 SLOC · 34 archivos

### Capa: `domain/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| `ranking_competencia.py` | 314 | 220 | 55 | 7 |
| `ranking_overall.py` | 224 | 159 | 40 | 3 |
| `algoritmo_faas.py` | 114 | 73 | 25 | 2 |
| `resultados_competencia_port.py` | 74 | 26 | 19 | 0 |
| `resultados_calculados.py` | 57 | 33 | 10 | 0 |
| `ranking_overall_calculado.py` | 45 | 33 | 8 | 0 |
| `algoritmo_puntaje.py` | 38 | 13 | 10 | 0 |
| `entrada_ranking.py` | 36 | 16 | 7 | 0 |
| `entrada_overall.py` | 30 | 13 | 7 | 0 |
| `exceptions.py` | 23 | 6 | 11 | 0 |
| `__init__.py` | 15 | 12 | 2 | 0 |
| `__init__.py` | 6 | 3 | 2 | 0 |
| `__init__.py` | 6 | 3 | 2 | 0 |
| `__init__.py` | 6 | 3 | 2 | 0 |
| `__init__.py` | 1 | 0 | 0 | 0 |
| **subtotal** | **989** | **613** | | |

### Capa: `application/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| `exportar_resultados.py` | 421 | 345 | 68 | 0 |
| `obtener_ranking_provisional.py` | 219 | 166 | 37 | 0 |
| `calcular_ranking.py` | 126 | 69 | 30 | 3 |
| `obtener_ranking.py` | 120 | 57 | 29 | 3 |
| `calcular_overall.py` | 84 | 54 | 18 | 0 |
| `obtener_overall.py` | 74 | 43 | 18 | 0 |
| **subtotal** | **1044** | **734** | | |

### Capa: `infrastructure/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| `resultados_competencia_adapter.py` | 155 | 99 | 39 | 0 |
| `atleta_info_adapter.py` | 51 | 35 | 13 | 0 |
| `atleta_categoria_adapter.py` | 29 | 19 | 8 | 0 |
| `disciplina_descriptor_adapter.py` | 15 | 7 | 5 | 0 |
| **subtotal** | **250** | **160** | | |

### Capa: `api/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| `router.py` | 379 | 294 | 60 | 3 |
| **subtotal** | **379** | **294** | | |

### Capa: `raiz/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| **subtotal** | **0** | **0** | | |

---

## BC: `identidad`
**Totales:** 1227 LOC · 979 SLOC · 29 archivos

### Capa: `domain/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| `exceptions.py` | 73 | 45 | 28 | 0 |
| `usuario.py` | 33 | 27 | 6 | 1 |
| `token_service_port.py` | 25 | 13 | 8 | 0 |
| `usuario_repository_port.py` | 24 | 16 | 8 | 0 |
| `perfil_registro_port.py` | 21 | 17 | 4 | 0 |
| `password_hashing_port.py` | 15 | 7 | 5 | 0 |
| `rol.py` | 10 | 7 | 3 | 0 |
| `__init__.py` | 9 | 8 | 1 | 0 |
| **subtotal** | **210** | **140** | | |

### Capa: `application/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| `registrar_usuario.py` | 152 | 133 | 18 | 2 |
| `autenticar_usuario.py` | 62 | 46 | 16 | 0 |
| `reset_password.py` | 56 | 43 | 13 | 0 |
| `solicitar_reset_password.py` | 51 | 43 | 8 | 0 |
| `cambiar_password.py` | 46 | 35 | 11 | 0 |
| **subtotal** | **367** | **300** | | |

### Capa: `infrastructure/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| `sqlite_usuario_repository.py` | 161 | 137 | 22 | 2 |
| `jwt_service.py` | 52 | 41 | 10 | 1 |
| `bcrypt_password_hasher.py` | 15 | 8 | 6 | 0 |
| **subtotal** | **228** | **186** | | |

### Capa: `api/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| `router.py` | 315 | 273 | 40 | 3 |
| `dependencies.py` | 107 | 80 | 24 | 3 |
| **subtotal** | **422** | **353** | | |

### Capa: `raiz/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| **subtotal** | **0** | **0** | | |

---

## BC: `notificaciones`
**Totales:** 1279 LOC · 1036 SLOC · 39 archivos

### Capa: `domain/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| `notificacion.py` | 219 | 192 | 26 | 2 |
| `notificacion_solicitada.py` | 48 | 42 | 6 | 0 |
| `notificacion_enviada.py` | 36 | 30 | 6 | 0 |
| `notificacion_fallida.py` | 36 | 30 | 6 | 0 |
| `notificacion_repository.py` | 21 | 16 | 5 | 0 |
| `destinatario.py` | 20 | 14 | 6 | 0 |
| `exceptions.py` | 19 | 5 | 9 | 0 |
| `contenido_email.py` | 18 | 13 | 5 | 0 |
| `notificacion_id.py` | 16 | 11 | 5 | 0 |
| `email_port.py` | 15 | 11 | 4 | 0 |
| `__init__.py` | 15 | 12 | 2 | 0 |
| `evento_fuente_id.py` | 15 | 10 | 5 | 0 |
| `__init__.py` | 11 | 8 | 2 | 0 |
| `canal_envio.py` | 8 | 5 | 3 | 0 |
| `__init__.py` | 6 | 3 | 2 | 0 |
| `__init__.py` | 5 | 2 | 2 | 0 |
| **subtotal** | **508** | **404** | | |

### Capa: `application/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| `politica_p11.py` | 109 | 93 | 16 | 0 |
| `politica_p10.py` | 72 | 61 | 11 | 0 |
| `solicitar_envio.py` | 48 | 39 | 9 | 0 |
| `enviar_notificacion.py` | 47 | 37 | 10 | 1 |
| `_helpers.py` | 25 | 16 | 5 | 0 |
| `__init__.py` | 19 | 18 | 1 | 0 |
| `__init__.py` | 15 | 14 | 1 | 0 |
| **subtotal** | **335** | **278** | | |

### Capa: `infrastructure/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| `sqlite_notificacion_event_store.py` | 116 | 102 | 13 | 0 |
| `resend_email_adapter.py` | 97 | 81 | 15 | 0 |
| `resultados_publicados_template.py` | 72 | 59 | 13 | 0 |
| `logging_email_adapter.py` | 49 | 36 | 8 | 0 |
| `inscripcion_confirmada_template.py` | 34 | 28 | 6 | 0 |
| `sqlite_notificacion_repository.py` | 28 | 21 | 7 | 0 |
| `__init__.py` | 13 | 10 | 2 | 0 |
| `__init__.py` | 8 | 7 | 1 | 0 |
| `__init__.py` | 7 | 4 | 2 | 0 |
| `__init__.py` | 7 | 4 | 2 | 0 |
| `__init__.py` | 5 | 2 | 2 | 0 |
| **subtotal** | **436** | **354** | | |

### Capa: `api/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| **subtotal** | **0** | **0** | | |

### Capa: `raiz/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| **subtotal** | **0** | **0** | | |

---

## BC: `shared`
**Totales:** 534 LOC · 306 SLOC · 17 archivos

### Capa: `domain/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| `event_store_port.py` | 86 | 20 | 21 | 0 |
| `disciplina.py` | 56 | 36 | 10 | 13 |
| `disciplina_descriptor.py` | 56 | 26 | 13 | 0 |
| `tiempo_ap.py` | 42 | 28 | 10 | 0 |
| `domain_event.py` | 40 | 15 | 10 | 0 |
| `aggregate_root.py` | 38 | 11 | 11 | 0 |
| `unidad_medida.py` | 12 | 5 | 5 | 0 |
| `__init__.py` | 8 | 5 | 2 | 0 |
| `__init__.py` | 6 | 3 | 2 | 0 |
| `__init__.py` | 5 | 2 | 2 | 0 |
| **subtotal** | **349** | **151** | | |

### Capa: `infrastructure/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| `sqlite_event_store.py` | 177 | 153 | 18 | 0 |
| `__init__.py` | 1 | 0 | 0 | 0 |
| `__init__.py` | 1 | 0 | 0 | 0 |
| **subtotal** | **179** | **153** | | |

### Capa: `api/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| `dependencies.py` | 5 | 2 | 2 | 0 |
| `__init__.py` | 1 | 0 | 0 | 0 |
| **subtotal** | **6** | **2** | | |

### Capa: `raiz/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| **subtotal** | **0** | **0** | | |

---

## BC: `app`
**Totales:** 694 LOC · 571 SLOC · 1 archivos

### Capa: `raiz/`
| Módulo | LOC | SLOC | Blancos | Comentarios |
|--------|----:|-----:|--------:|------------:|
| `app.py` | 694 | 571 | 92 | 6 |
| **subtotal** | **694** | **571** | | |
