# Índice de Mantenibilidad (MI) por BC · Capa · Módulo — Backend Python
> Herramienta: `radon mi` v6.0.1  
> Fuente: `src/`  
> Fecha: 2026-05-18

**Escala:** A (MI ≥ 20) · B (10 ≤ MI < 20) · C (MI < 10)

---

## BC: `competencia`
**Totales:** MI prom 71.12 · MI mín 29.17 · 47 archivos (excl. __init__ vacíos)

### Capa: `domain/`
| Módulo | MI | Rank |
|--------|---:|:----:|
| `grilla_de_salida.py` | 32.19 | A |
| `resolucion_tarjeta.py` | 43.37 | A |
| `performance.py` | 50.38 | A |
| `tarjeta_asignacion.py` | 50.63 | A |
| `competencia.py` | 53.30 | A |
| `revision_resuelta.py` | 55.25 | A |
| `rp_final.py` | 55.60 | A |
| `performance_events.py` | 59.91 | A |
| `performance_state.py` | 63.31 | A |
| `penalizacion_tecnica.py` | 66.83 | A |
| `calculador_hash_competencia.py` | 69.32 | A |
| `motivo_dq.py` | 69.99 | A |
| `tarjeta_asignada.py` | 70.82 | A |
| `andariveles_activos_port.py` | 82.00 | A |
| `performances_estado_port.py` | 83.67 | A |
| `competencia_finalizada.py` | 86.68 | A |
| `intervalo_ot_configurado.py` | 89.45 | A |
| `entrada_grilla.py` | 93.52 | A |
| `ap.py` | 95.42 | A |
| `intervalo_disciplina.py` | 98.14 | A |
| **prom capa** | **68.49** | **A** |

### Capa: `application/`
| Módulo | MI | Rank |
|--------|---:|:----:|
| `resolver_revision.py` | 48.89 | A |
| `obtener_grilla.py` | 53.76 | A |
| `obtener_audit_log.py` | 57.23 | A |
| `_handler_utils.py` | 64.36 | A |
| `obtener_proximas_performances.py` | 68.49 | A |
| `finalizar_competencia_manual.py` | 71.22 | A |
| `obtener_performance_actual.py` | 71.54 | A |
| `obtener_progreso.py` | 72.84 | A |
| `asignar_tarjeta.py` | 73.65 | A |
| `obtener_estado_competencia.py` | 74.54 | A |
| `registrar_ap.py` | 76.53 | A |
| `llamar_atleta.py` | 79.75 | A |
| `configurar_intervalo_ot.py` | 82.52 | A |
| `registrar_resultado.py` | 83.87 | A |
| `registrar_dns.py` | 85.13 | A |
| `obtener_eventos.py` | 86.44 | A |
| `_p08_finalizacion.py` | 87.48 | A |
| `corregir_resultado.py` | 90.00 | A |
| **prom capa** | **73.79** | **A** |

### Capa: `infrastructure/`
| Módulo | MI | Rank |
|--------|---:|:----:|
| `sqlite_competencias_por_torneo.py` | 56.24 | A |
| `performances_ap_adapter.py` | 57.96 | A |
| `andariveles_activos_adapter.py` | 75.03 | A |
| `performances_estado_adapter.py` | 80.52 | A |
| `env.py` | 83.80 | A |
| `0001_create_events_table.py` | 84.51 | A |
| `competencia_estado_adapter.py` | 84.79 | A |
| `atleta_nombre_adapter.py` | 92.64 | A |
| **prom capa** | **76.94** | **A** |

### Capa: `api/`
| Módulo | MI | Rank |
|--------|---:|:----:|
| `router.py` | 29.17 | A ⚠ |
| **prom capa** | **29.17** | **A** |

---

## BC: `torneo`
**Totales:** MI prom 58.22 · MI mín 36.69 · 11 archivos (excl. __init__ vacíos)

### Capa: `domain/`
| Módulo | MI | Rank |
|--------|---:|:----:|
| `torneo.py` | 42.79 | A |
| `disciplina_torneo.py` | 65.17 | A |
| `grupo_etario.py` | 73.04 | A |
| **prom capa** | **60.33** | **A** |

### Capa: `application/`
| Módulo | MI | Rank |
|--------|---:|:----:|
| `transicionar_torneo.py` | 49.54 | A |
| `actualizar_torneo.py` | 60.51 | A |
| `obtener_torneo.py` | 63.59 | A |
| `asignar_juez.py` | 64.61 | A |
| `asignar_disciplinas.py` | 65.44 | A |
| `obtener_disciplinas_juez.py` | 69.72 | A |
| **prom capa** | **62.23** | **A** |

### Capa: `infrastructure/`
| Módulo | MI | Rank |
|--------|---:|:----:|
| `sqlite_torneo_repository.py` | 49.35 | A |
| **prom capa** | **49.35** | **A** |

### Capa: `api/`
| Módulo | MI | Rank |
|--------|---:|:----:|
| `router.py` | 36.69 | A |
| **prom capa** | **36.69** | **A** |

---

## BC: `registro`
**Totales:** MI prom 59.29 · MI mín 23.26 · 26 archivos (excl. __init__ vacíos)

### Capa: `domain/`
| Módulo | MI | Rank |
|--------|---:|:----:|
| `atleta.py` | 37.91 | A |
| `inscripcion.py` | 43.31 | A |
| `juez.py` | 53.16 | A |
| `organizador.py` | 55.68 | A |
| `ap_declarado.py` | 67.75 | A |
| **prom capa** | **51.56** | **A** |

### Capa: `application/`
| Módulo | MI | Rank |
|--------|---:|:----:|
| `actualizar_atleta.py` | 51.89 | A |
| `verificar_completitud_ap.py` | 59.15 | A |
| `registrar_juez.py` | 59.78 | A |
| `registrar_atleta.py` | 61.81 | A |
| `actualizar_organizador.py` | 61.84 | A |
| `registrar_organizador.py` | 61.84 | A |
| `cancelar_inscripcion.py` | 64.61 | A |
| `declarar_ap_inscripcion.py` | 64.61 | A |
| `inscribir_atleta.py` | 66.98 | A |
| `obtener_atleta.py` | 70.42 | A |
| `obtener_juez.py` | 71.18 | A |
| `obtener_organizador.py` | 71.18 | A |
| `actualizar_juez.py` | 73.11 | A |
| **prom capa** | **64.49** | **A** |

### Capa: `infrastructure/`
| Módulo | MI | Rank |
|--------|---:|:----:|
| `sqlite_inscripcion_repository.py` | 44.36 | A |
| `sqlite_atleta_repository.py` | 56.50 | A |
| `perfil_registro_adapter.py` | 56.71 | A |
| `local_adjunto_storage.py` | 63.12 | A |
| `sqlite_torneo_consulta.py` | 65.14 | A |
| `sqlite_juez_repository.py` | 67.99 | A |
| `sqlite_organizador_repository.py` | 68.17 | A |
| **prom capa** | **60.28** | **A** |

### Capa: `api/`
| Módulo | MI | Rank |
|--------|---:|:----:|
| `router.py` | 23.26 | A ⚠ |
| **prom capa** | **23.26** | **A** |

---

## BC: `resultados`
**Totales:** MI prom 62.04 · MI mín 21.67 · 14 archivos (excl. __init__ vacíos)

### Capa: `domain/`
| Módulo | MI | Rank |
|--------|---:|:----:|
| `ranking_competencia.py` | 48.38 | A |
| `ranking_overall.py` | 52.07 | A |
| `algoritmo_faas.py` | 61.93 | A |
| `resultados_competencia_port.py` | 83.04 | A |
| `entrada_ranking.py` | 88.36 | A |
| **prom capa** | **66.76** | **A** |

### Capa: `application/`
| Módulo | MI | Rank |
|--------|---:|:----:|
| `exportar_resultados.py` | 21.67 | A ⚠ |
| `obtener_ranking_provisional.py` | 45.21 | A |
| `calcular_overall.py` | 74.65 | A |
| `obtener_ranking.py` | 77.81 | A |
| `calcular_ranking.py` | 80.83 | A |
| **prom capa** | **60.03** | **A** |

### Capa: `infrastructure/`
| Módulo | MI | Rank |
|--------|---:|:----:|
| `atleta_info_adapter.py` | 58.77 | A |
| `resultados_competencia_adapter.py` | 63.43 | A |
| `atleta_categoria_adapter.py` | 63.61 | A |
| **prom capa** | **61.94** | **A** |

### Capa: `api/`
| Módulo | MI | Rank |
|--------|---:|:----:|
| `router.py` | 48.78 | A |
| **prom capa** | **48.78** | **A** |

---

## BC: `identidad`
**Totales:** MI prom 54.59 · MI mín 39.20 · 10 archivos (excl. __init__ vacíos)

### Capa: `domain/`
| Módulo | MI | Rank |
|--------|---:|:----:|
| `usuario.py` | 68.33 | A |
| **prom capa** | **68.33** | **A** |

### Capa: `application/`
| Módulo | MI | Rank |
|--------|---:|:----:|
| `registrar_usuario.py` | 45.58 | A |
| `autenticar_usuario.py` | 49.14 | A |
| `reset_password.py` | 50.46 | A |
| `cambiar_password.py` | 54.21 | A |
| `solicitar_reset_password.py` | 64.23 | A |
| **prom capa** | **52.72** | **A** |

### Capa: `infrastructure/`
| Módulo | MI | Rank |
|--------|---:|:----:|
| `sqlite_usuario_repository.py` | 52.19 | A |
| `jwt_service.py` | 65.77 | A |
| **prom capa** | **58.98** | **A** |

### Capa: `api/`
| Módulo | MI | Rank |
|--------|---:|:----:|
| `router.py` | 39.20 | A |
| `dependencies.py` | 56.76 | A |
| **prom capa** | **47.98** | **A** |

---

## BC: `notificaciones`
**Totales:** MI prom 58.52 · MI mín 39.58 · 15 archivos (excl. __init__ vacíos)

### Capa: `domain/`
| Módulo | MI | Rank |
|--------|---:|:----:|
| `notificacion.py` | 39.58 | A |
| `contenido_email.py` | 60.33 | A |
| `notificacion_solicitada.py` | 60.85 | A |
| `destinatario.py` | 61.38 | A |
| `notificacion_enviada.py` | 66.01 | A |
| `evento_fuente_id.py` | 67.81 | A |
| **prom capa** | **59.33** | **A** |

### Capa: `application/`
| Módulo | MI | Rank |
|--------|---:|:----:|
| `politica_p11.py` | 43.74 | A |
| `politica_p10.py` | 50.38 | A |
| `solicitar_envio.py` | 61.75 | A |
| `enviar_notificacion.py` | 65.86 | A |
| **prom capa** | **55.43** | **A** |

### Capa: `infrastructure/`
| Módulo | MI | Rank |
|--------|---:|:----:|
| `resend_email_adapter.py` | 44.97 | A |
| `sqlite_notificacion_event_store.py` | 48.38 | A |
| `resultados_publicados_template.py` | 50.58 | A |
| `sqlite_notificacion_repository.py` | 70.15 | A |
| `logging_email_adapter.py` | 85.98 | A |
| **prom capa** | **60.01** | **A** |

---

## BC: `shared`
**Totales:** MI prom 69.62 · MI mín 49.33 · 4 archivos (excl. __init__ vacíos)

### Capa: `domain/`
| Módulo | MI | Rank |
|--------|---:|:----:|
| `tiempo_ap.py` | 49.33 | A |
| `disciplina.py` | 85.24 | A |
| `disciplina_descriptor.py` | 88.35 | A |
| **prom capa** | **74.31** | **A** |

### Capa: `infrastructure/`
| Módulo | MI | Rank |
|--------|---:|:----:|
| `sqlite_event_store.py` | 55.56 | A |
| **prom capa** | **55.56** | **A** |

---

## BC: `app`
**Totales:** MI prom 28.52 · MI mín 28.52 · 1 archivos (excl. __init__ vacíos)

### Capa: `raiz/`
| Módulo | MI | Rank |
|--------|---:|:----:|
| `app.py` | 28.52 | A ⚠ |
| **prom capa** | **28.52** | **A** |
