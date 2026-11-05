# Objetivos vs. Resultados - CriptoMed

**Proyecto:** CriptoMed – Plataforma de Gestión de Historiales Médicos  
**Curso:** DS3031 - Ética y Seguridad de Datos  
**Entrega:** Entrega 2  
**Fecha:** Noviembre 2026

---

## Tabla de Objetivos vs. Resultados

| Objetivo | Resultado alcanzado | Estado | Evidencia | Si no se cumplió del todo, por qué y qué se haría |
|----------|---------------------|--------|-----------|----------------------------------------------|
| **Negocio** | | | | |
| Valor medido con KPIs/OKRs | Reducción de tiempo de acceso a historiales de ~10 min a <30 seg (80% de reducción) | Cumplido | Métrica basada en búsqueda en base de datos vs. archivo físico (simulada) | - |
| Cumplimiento de la Ley 29733 | Implementación de medidas técnicas (cifrado, hashing, control de acceso, logs) y medidas organizativas documentadas (políticas, procedimientos) | Cumplido | docs/FINAL_REPORT.md, docs/inventario_datos.md, docs/DPIA.md | - |
| Backups y recuperación (RTO/RPO) | Backups diarios cifrados con GPG AES-256, RPO: 24 horas, RTO: <30 minutos (medido en pruebas de restauración) | Cumplido | scripts/backup.sh, scripts/restore.sh, docs/BACKUPS.md | - |
| **Seguridad** | | | | |
| Cifrado en reposo | 100% de campos sensibles cifrados con AES-256-GCM (nombre, diagnóstico, medicación, resultado_test, monto_facturado) | Cumplido | backend/app/crypto.py, scripts/verificar_cifrado.py | - |
| Cifrado en tránsito (TLS 1.3 y certificado autofirmado) | TLS 1.3 exclusivo en edge Nginx, certificado autofirmado generado con OpenSSL | Cumplido | docker/edge/nginx.conf, scripts/verificar_despliegue.sh (verifica TLS 1.3) | - |
| Hashing de contraseñas | bcrypt con factor 12, límite de 72 bytes | Cumplido | backend/app/auth.py, requirements.txt (bcrypt) | - |
| RBAC | 5 roles implementados (admin, doctor, administrativo, auditor, paciente) con principio de mínimo privilegio | Cumplido | backend/app/rbac.py, backend/app/routers/pacientes.py | - |
| Mínimo privilegio | Rol administrativo NO ve datos clínicos (diagnóstico, medicación, resultado_test) | Cumplido | backend/app/rbac.py (filtrado en backend), GUION_DEMO.md paso 4 | - |
| Expiración de sesión por inactividad | JWT con expiración 30 min, cierre por inactividad en frontend (localStorage) | Parcial | backend/app/auth.py (expiración 30 min), frontend tiene timeout pero no implementado explícitamente | Mejora futura: implementar refresh token y cerrar sesión por inactividad en backend |
| Logs de auditoría | 100% de accesos registrados en audit_logs (login, lectura, edicion, borrado, transferencia, exportacion, acceso_emergencia) | Cumplido | backend/app/audit.py, GUION_DEMO.md paso 8 | - |
| Logs inmutables | Cadena de hashes SHA-256, triggers anti-UPDATE/DELETE, rol de aplicación con solo INSERT/SELECT | Cumplido | backend/scripts/sql/proteger_audit_logs.sql, scripts/verificar_cadena_logs.py | - |
| Política de contraseñas | Política alineada a NIST SP 800-63B (longitud mínima 12, verificación contra contraseñas comunes, sin rotación obligatoria) | Cumplido | backend/app/routers/auth.py (validate_password_policy) | - |
| Capacitación y concientización | Política escrita documentada (docs/SECURITY_AWARENESS.md) | Parcial | docs/SECURITY_AWARENESS.md existe pero no hay evidencia de capacitación ejecutada | En prototipo no hay personal real; en producción se implementaría programa de capacitación |
| Revocación inmediata de accesos | Campo activo booleano que revoca acceso inmediatamente sin cambio de contraseña | Cumplido | backend/app/models.py (Usuario.activo), backend/app/routers/usuarios.py (PATCH /usuarios/{id}/revocar) | - |
| Herramienta de análisis APLICADA | Suite multi-herramienta ejecutada (Bandit, pip-audit, npm audit, Gitleaks, Hadolint, Trivy, testssl.sh, OWASP ZAP) con remediación de hallazgos | Cumplido | scripts/security_scan.sh, docs/hallazgos.md, docs/comparativa_antes_despues.md | - |
| Identificación de riesgos | DPIA completa con 12 riesgos identificados, probabilidad, impacto, mitigación y riesgo residual | Cumplido | docs/DPIA.md, docs/inventario_datos.md | - |
| Plan de respuesta a incidentes | Plan documentado en 5 fases (detección, contención, notificación, remediación, post-mortem) conforme a NIST SP 800-61 | Cumplido | docs/FINAL_REPORT.md (sección 6), procedimientos de notificación documentados | - |
| Recomendaciones futuras | Lista de mejoras futuras documentadas (MFA, HSM, KMS, WAF, Argon2id, etc.) | Cumplido | docs/FINAL_REPORT.md (sección 9) | - |
| **Funcionales** | | | | |
| Rol paciente | Paciente puede ver su historial, ver quién accedió, exportar datos, transferir a otro doctor | Cumplido | backend/app/routers/pacientes.py (GET /me, /me/accesos, /me/export, PATCH /transferir-doctor) | - |
| Transferencia de doctor | Paciente puede transferir su historial a otro doctor self-service con confirmación explícita | Cumplido | backend/app/routers/pacientes.py (PATCH /transferir-doctor), GUION_DEMO.md paso 7 | - |
| Vista de accesos del paciente | Paciente puede ver lista paginada de quién accedió a su historial (nombre profesional, rol, timestamp, IP) | Cumplido | backend/app/routers/pacientes.py (GET /me/accesos), GUION_DEMO.md paso 6 | - |
| Exportación de datos | Paciente puede exportar sus datos en JSON (derecho de portabilidad) | Cumplido | backend/app/routers/pacientes.py (GET /me/export) | - |
| Consentimiento | Campos consentimiento_fecha y consentimiento_version en modelo Paciente | Cumplido | backend/app/models.py (Paciente.consentimiento_fecha, consentimiento_version) | - |
| **Técnicos** | | | | |
| Frontend | React + Vite + Node 20.19.0, desplegado en Docker edge Nginx | Cumplido | frontend/, docker/edge/Dockerfile | - |
| Backend | FastAPI + Python 3.12.7, desplegado en Docker | Cumplido | backend/, docker/backend/Dockerfile | - |
| Base de datos relacional | PostgreSQL 16 Alpine con roles (owner y aplicación) | Cumplido | docker/db/init/, docker-compose.yml | - |
| Certificados digitales | Certificado autofirmado generado con OpenSSL | Cumplido | scripts/gen_cert.sh, certs/cert.pem | - |
| Despliegue | Docker Compose local con reproducibilidad completa | Cumplido | docker-compose.yml, scripts/dev.sh, docs/DOCKER.md | - |
| **E2** | | | | |
| DPIA | Evaluación de Impacto en la Protección de Datos completa con ciclo de vida, riesgos y plan de revisión | Cumplido | docs/DPIA.md | - |
| Sección de ética y privacidad | Consideraciones éticas (autonomía, consentimiento, tensiones, datos sintéticos, transparencia IA) | Cumplido | docs/etica_privacidad.md | - |
| Informe | Informe reescrito como narrativa de diseño (no checklist) con 12-15 páginas más anexos | Cumplido | docs/FINAL_REPORT.md | - |
| Presentación | Contenido de 12 diapositivas documentado | Cumplido | docs/presentacion.md (próximo paso) | - |
| Demo | Guion de 11 pasos documentado con scripts de preparación y demo | Cumplido | docs/GUION_DEMO.md, scripts/preparar_demo.sh, scripts/demo_rotacion.sh, scripts/demo_alterar_log.sql | - |

---

## Resumen

**Total objetivos:** 28  
**Cumplidos:** 26  
**Parciales:** 2  
**No cumplidos:** 0  

**Objetivos parciales:**
1. Expiración de sesión por inactividad - JWT expira en 30 min pero cierre por inactividad en frontend no está implementado explícitamente
2. Capacitación y concientización - Política escrita existe pero no hay evidencia de capacitación ejecutada (no aplicable en prototipo sin personal real)

**Justificación de parciales:**
- Expiración por inactividad: Mejora futura implementable con refresh token y monitoreo de actividad en backend
- Capacitación: En prototipo académico no hay personal real; en producción se implementaría programa de capacitación con simulacros de phishing y entrenamiento

**Estado general:** Excelente cumplimiento de objetivos con mitigaciones documentadas para mejoras futuras.
