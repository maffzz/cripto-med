# Matriz de Trazabilidad - CriptoMed

**Proyecto:** CriptoMed – Plataforma de Gestión de Historiales Médicos  
**Curso:** DS3031 - Ética y Seguridad de Datos  
**Entrega:** Entrega 2  
**Fecha:** Noviembre 2026

---

## Matriz de Trazabilidad

| Requisito | Tipo | Entrega | Estado | Dónde está | Evidencia |
|-----------|------|---------|--------|------------|-----------|
| **Negocio** | | | | | |
| Valor medido con KPIs/OKRs | Negocio | E1 mejorado en E2 | Implementado | Tiempo de acceso reducido de ~10 min a <30 seg (medido en queries) | Medida basada en búsqueda en base de datos vs. archivo físico |
| Cumplimiento de la Ley 29733 | Negocio | E1 mejorado en E2 | Implementado | docs/FINAL_REPORT.md, docs/inventario_datos.md, docs/DPIA.md | Art. 3 (datos sensibles), Art. 5 (medidas técnicas), Art. 10 (notificación), Art. 14 (derechos ARCO) |
| Backups y recuperación (RTO/RPO) | Negocio | E1 mejorado en E2 | Implementado | scripts/backup.sh, scripts/restore.sh, docs/BACKUPS.md | RPO: 24 horas, RTO: <30 minutos (medido en pruebas de restauración) |
| **Seguridad** | | | | | |
| Cifrado en reposo | Seguridad | E1 mejorado en E2 | Implementado | backend/app/crypto.py, scripts/verificar_cifrado.py | AES-256-GCM con llaves versionadas, AAD, 5 campos cifrados |
| Cifrado en tránsito (TLS 1.3 y certificado autofirmado) | Seguridad | E1 mejorado en E2 | Implementado | docker/edge/nginx.conf, scripts/verificar_despliegue.sh | TLS 1.3 exclusivo, certificado autofirmado OpenSSL |
| Hashing de contraseñas | Seguridad | E1 | Implementado | backend/app/auth.py, requirements.txt | bcrypt factor 12, límite 72 bytes |
| RBAC | Seguridad | E1 mejorado en E2 | Implementado | backend/app/rbac.py, backend/app/routers/pacientes.py | 5 roles, mínimo privilegio, filtrado en backend |
| Mínimo privilegio | Seguridad | E1 mejorado en E2 | Implementado | backend/app/rbac.py | Administrativo NO ve diagnóstico, medicación, resultado_test |
| Expiración de sesión por inactividad | Seguridad | E1 | Parcial | backend/app/auth.py (expiración 30 min) | JWT expira en 30 min, pero cierre por inactividad en frontend no implementado explícitamente |
| Logs de auditoría | Seguridad | E1 mejorado en E2 | Implementado | backend/app/audit.py, backend/app/routers/audit_logs.py | 9 acciones registradas, todos los accesos |
| Logs inmutables | Seguridad | E2 | Implementado | backend/scripts/sql/proteger_audit_logs.sql, scripts/verificar_cadena_logs.py | Cadena SHA-256, triggers anti-UPDATE/DELETE, rol de aplicación con solo INSERT/SELECT |
| Política de contraseñas | Seguridad | E1 mejorado en E2 | Implementado | backend/app/routers/auth.py (validate_password_policy) | NIST SP 800-63B: longitud mínima 12, sin rotación obligatoria, verificación contra contraseñas comunes |
| Capacitación y concientización | Seguridad | E1 | Parcial | docs/SECURITY_AWARENESS.md | Política escrita existe, pero no hay evidencia de capacitación ejecutada (no aplicable en prototipo sin personal real) |
| Revocación inmediata de accesos | Seguridad | E1 mejorado en E2 | Implementado | backend/app/models.py (Usuario.activo), backend/app/routers/usuarios.py (PATCH /usuarios/{id}/revocar) | Campo activo booleano, revoca acceso sin cambio de contraseña |
| Herramienta de análisis APLICADA | Seguridad | E2 | Implementado | scripts/security_scan.sh, docs/hallazgos.md, docs/comparativa_antes_despues.md | Suite multi-herramienta (Bandit, Trivy, ZAP, etc.) ejecutada, reducción 61.18% |
| Identificación de riesgos | Seguridad | E2 | Implementado | docs/DPIA.md, docs/inventario_datos.md | DPIA completa con 12 riesgos identificados, probabilidad, impacto, mitigación |
| Plan de respuesta a incidentes | Seguridad | E1 mejorado en E2 | Implementado | docs/FINAL_REPORT.md (sección 6), procedimientos documentados | Plan en 5 fases conforme a NIST SP 800-61, notificación a ANPD en 48h |
| Recomendaciones futuras | Seguridad | E1 mejorado en E2 | Implementado | docs/FINAL_REPORT.md (sección 9) | Lista de mejoras futuras (MFA, HSM, KMS, WAF, Argon2id, etc.) |
| **Funcionales** | | | | | |
| Rol paciente | Funcional | E2 | Implementado | backend/app/routers/pacientes.py (GET /me, /me/accesos, /me/export, PATCH /transferir-doctor) | Paciente puede ver historial, ver accesos, exportar datos, transferir doctor |
| Transferencia de doctor | Funcional | E2 | Implementado | backend/app/routers/pacientes.py (PATCH /transferir-doctor) | Transferencia self-service con confirmación explícita, registrada en audit_logs |
| Vista de accesos del paciente | Funcional | E2 | Implementado | backend/app/routers/pacientes.py (GET /me/accesos) | Lista paginada de accesos con nombre profesional, rol, timestamp, IP |
| Exportación de datos | Funcional | E2 | Implementado | backend/app/routers/pacientes.py (GET /me/export) | Exportación JSON con todos los datos descifrados, registrada como acción exportacion |
| Consentimiento | Funcional | E2 | Implementado | backend/app/models.py (Paciente.consentimiento_fecha, consentimiento_version) | Campos de consentimiento registrados, versión v1.0 |
| **Técnicos** | | | | | |
| Frontend | Técnico | E1 | Implementado | frontend/, docker/edge/Dockerfile | React + Vite + Node 20.19.0, compilado en edge Nginx |
| Backend | Técnico | E1 mejorado en E2 | Implementado | backend/, docker/backend/Dockerfile | FastAPI + Python 3.12.7, Docker |
| Base de datos relacional | Técnico | E1 mejorado en E2 | Implementado | docker/db/init/, docker-compose.yml | PostgreSQL 16 Alpine con roles (owner y aplicación) |
| Certificados digitales | Técnico | E1 | Implementado | scripts/gen_cert.sh, certs/cert.pem | Certificado autofirmado generado con OpenSSL |
| Despliegue | Técnico | E1 mejorado en E2 | Implementado | docker-compose.yml, scripts/dev.sh, docs/DOCKER.md | Docker Compose local con reproducibilidad completa |
| **E2** | | | | | |
| DPIA | E2 | E2 | Implementado | docs/DPIA.md | Evaluación de Impacto en la Protección de Datos completa con ciclo de vida, riesgos y plan de revisión |
| Sección de ética y privacidad | E2 | E2 | Implementado | docs/etica_privacidad.md | Consideraciones éticas (autonomía, consentimiento, tensiones, datos sintéticos, transparencia IA) |
| Informe | E2 | E2 | Implementado | docs/FINAL_REPORT.md | Informe reescrito como narrativa de diseño (no checklist) con 12-15 páginas más anexos |
| Presentación | E2 | E2 | Implementado | docs/presentacion.md | Contenido de 12 diapositivas documentado |
| Demo | E2 | E2 | Implementado | docs/GUION_DEMO.md, scripts/preparar_demo.sh, scripts/demo_rotacion.sh, scripts/demo_alterar_log.sql | Guion de 11 pasos documentado con scripts de preparación y demo |

---

## Resumen

**Total requisitos:** 28  
**Implementados:** 26  
**Parciales:** 2  
**No implementados:** 0  

**Parciales:**
1. Expiración de sesión por inactividad - JWT expira en 30 min pero cierre por inactividad en frontend no está implementado explícitamente
2. Capacitación y concientización - Política escrita existe pero no hay evidencia de capacitación ejecutada (no aplicable en prototipo sin personal real)

**Justificación de parciales:**
- Expiración por inactividad: Mejora futura implementable con refresh token y monitoreo de actividad en backend
- Capacitación: En prototipo académico no hay personal real; en producción se implementaría programa de capacitación con simulacros de phishing y entrenamiento
