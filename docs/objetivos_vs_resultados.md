# Objetivos vs. Resultados - CriptoMed

**Proyecto:** CriptoMed – Plataforma de Gestión de Historiales Médicos  
**Curso:** DS3031 - Ética y Seguridad de Datos  
**Entrega:** Entrega 2  
**Fecha:** Noviembre 2026

---

## Tabla de Objetivos vs. Resultados

| Objetivo | Resultado alcanzado | Estado | Evidencia | Notas |
|----------|---------------------|--------|-----------|-------|
| **Negocio** | | | | |
| Valor medido con KPIs/OKRs | La demo consulta historiales en menos de 30 segundos; la comparación con 10 minutos es una estimación frente a un proceso manual, no un estudio cronometrado en una clínica | ⚠️ Parcial | Demo y medición interna documentada | Validar con usuarios y línea base real antes de afirmar una reducción de 80% |
| Cumplimiento de la Ley 29733 | Hay controles técnicos y documentación orientados a privacidad; no existe validación legal ni evidencia de cumplimiento integral | ⚠️ Parcial | docs/FINAL_REPORT.md, docs/inventario_datos.md, docs/DPIA.md | La DPIA identifica riesgo residual alto de retención; solo demo con datos sintéticos |
| Backups y recuperación (RTO/RPO) | Backup cifrado manual; retiene los 7 archivos más recientes. No hay scheduler, off-site ni WAL. RPO/RTO actuales no garantizados | ⚠️ Parcial | scripts/backup.sh, scripts/restore.sh, docs/BACKUPS.md | La medición de restauración del 2026-11-04 es histórica y debe repetirse con la versión actual |
| **Seguridad** | | | | |
| Cifrado en reposo | Cinco campos de paciente cifrados con AES-256-GCM; otros datos de salud/cuasi-identificadores no están cifrados campo por campo | ⚠️ Parcial | backend/app/crypto.py, scripts/verificar_cifrado.py | No afirmar que el 100% de datos sensibles está cifrado |
| Cifrado en tránsito (TLS 1.3 y certificado autofirmado) | TLS 1.3 exclusivo en edge Nginx, certificado autofirmado OpenSSL | ✅ Cumplido | docker/edge/nginx.conf, scripts/verificar_despliegue.sh | - |
| Hashing de contraseñas | bcrypt con factor 12, límite de 72 bytes (OWASP Password Storage Cheat Sheet) | ✅ Cumplido | backend/app/auth.py, requirements.txt | - |
| RBAC | 5 roles (admin, doctor, administrativo, auditor, paciente) con principio de mínimo privilegio | ✅ Cumplido | backend/app/rbac.py, backend/app/routers/pacientes.py | - |
| Mínimo privilegio | Administrativo NO ve datos clínicos (diagnóstico, medicación, resultado_test); filtrado en backend | ✅ Cumplido | backend/app/rbac.py, docs/GUION_DEMO.md paso 4 | - |
| Expiración de sesión por inactividad | Temporizador frontend de 15 min; JWT configurable (30 min en `.env.example`, 15 min como fallback del backend) | Implementado con configuración a aclarar | frontend/src/context/AuthContext.jsx, backend/app/config.py, .env.example | Alinear los valores y comprobar expiración en despliegue |
| Logs de auditoría | Se registran las acciones instrumentadas (incluye login, exportación y acceso de emergencia); no se ha demostrado que el 100% de accesos/lecturas quede registrado | ⚠️ Parcial | backend/app/audit.py, docs/GUION_DEMO.md paso 8 | Verificar cobertura de cada ruta/API |
| Integridad de auditoría | Cadena SHA-256, triggers anti-UPDATE/DELETE y rol de aplicación restringido | Implementado con límite | backend/scripts/sql/proteger_audit_logs.sql, scripts/verificar_cadena_logs.py | Detectable ante alteraciones desde el rol de aplicación; no es inmutable frente a un administrador privilegiado ni tiene anclaje externo |
| Política de contraseñas | NIST SP 800-63B: longitud mínima 12, zxcvbn puntuación ≥3, sin rotación obligatoria, rechaza datos personales | ✅ Cumplido | backend/app/auth.py (validate_password_policy) | - |
| Capacitación y concientización | Política de seguridad y concientización documentada: roles, contraseñas, incidentes, uso aceptable, derechos de titulares, plan de capacitación para producción | ✅ Cumplido | docs/SECURITY_AWARENESS.md | En prototipo se documenta la política; en producción se ejecuta con capacitaciones periódicas y simulacros |
| Revocación inmediata de accesos | Campo `activo` booleano revoca el acceso en cada request sin necesidad de cambiar contraseña | ✅ Cumplido | backend/app/models.py (Usuario.activo), backend/app/routers/usuarios.py (PATCH /revocar) | - |
| Herramienta de análisis APLICADA | Suite multi-herramienta ejecutada (Bandit, pip-audit, npm audit, Gitleaks, Hadolint, Trivy, testssl.sh, OWASP ZAP); reducción 61.18% en hallazgos (3,596 → 1,396) | ✅ Cumplido | scripts/security_scan.sh, docs/hallazgos.md, docs/comparativa_antes_despues.md | - |
| Identificación de riesgos | DPIA con 12 riesgos: probabilidad, impacto (1-5), mitigaciones reales y riesgo residual | ✅ Cumplido | docs/DPIA.md, docs/inventario_datos.md | - |
| Plan de respuesta a incidentes | Plan en 5 fases (detección, contención, notificación ANPD en 48h, remediación, post-mortem) conforme a NIST SP 800-61 | ✅ Cumplido | docs/FINAL_REPORT.md (sección 6) | - |
| Recomendaciones futuras | MFA, HSM/KMS, WAF, Argon2id, cookie HttpOnly, SIEM, Zero Trust documentados | ✅ Cumplido | docs/FINAL_REPORT.md (sección 9) | - |
| **Funcionales** | | | | |
| Rol paciente | Historial propio, vista de accesos, exportación JSON, transferencia de doctor con confirmación explícita | ✅ Cumplido | backend/app/routers/pacientes.py (GET /me, /me/accesos, /me/export, PATCH /transferir-doctor) | - |
| Transferencia de doctor | Self-service con modal de confirmación, revoca acceso del doctor anterior inmediatamente, registrado en cadena SHA-256 | ✅ Cumplido | backend/app/routers/pacientes.py (PATCH /transferir-doctor), docs/GUION_DEMO.md paso 7 | - |
| Vista de accesos del paciente | Lista paginada con nombre profesional, rol, timestamp (hora Lima), IP y tipo de acción incluyendo emergencias | ✅ Cumplido | backend/app/routers/pacientes.py (GET /me/accesos), frontend/src/pages/MiHistorial.jsx | - |
| Exportación de datos | JSON con todos los campos descifrados, acción `exportacion` registrada en cadena SHA-256 (Derecho de Portabilidad Ley 29733) | ✅ Cumplido | backend/app/routers/pacientes.py (GET /me/export) | - |
| Consentimiento | Se almacenan fecha y versión; no hay flujo que recoja y pruebe una aceptación válida | ⚠️ Parcial | backend/app/models.py, frontend/src/pages/MiHistorial.jsx | Los campos no demuestran consentimiento informado |
| **Técnicos** | | | | |
| Frontend | React + Vite + Node 20.19.0, compilado en Docker multi-stage, servido por Nginx | ✅ Cumplido | frontend/, docker/edge/Dockerfile | - |
| Backend | FastAPI + Python 3.12.7, usuario no root (UID 10001), read-only filesystem | ✅ Cumplido | backend/, docker/backend/Dockerfile | - |
| Base de datos relacional | PostgreSQL 16 Alpine con dos roles (owner para DDL, app_user para DML) | ✅ Cumplido | docker/db/init/, docker-compose.yml | - |
| Certificados digitales | Certificado autofirmado con SAN (DNS:localhost, IP:127.0.0.1) generado con OpenSSL | ✅ Cumplido | scripts/gen_cert.sh, certs/cert.pem | - |
| Despliegue | Docker Compose local reproducible: un comando (`./scripts/dev.sh deploy`) levanta todo | ✅ Cumplido | docker-compose.yml, scripts/dev.sh, docs/DOCKER.md | - |
| **E2** | | | | |
| DPIA | DPIA completa: descripción sistemática, ciclo de vida, necesidad y proporcionalidad, 12 riesgos, plan de revisión | ✅ Cumplido | docs/DPIA.md | - |
| Sección de ética y privacidad | Autonomía, minimización, tensiones éticas (cancelación vs. conservación, seguridad vs. emergencia), datos sintéticos, transparencia IA | ✅ Cumplido | docs/etica_privacidad.md | - |
| Informe | Narrativa de diseño con formato Decisión→Por qué→Estándar→Evidencia; no checklist | ✅ Cumplido | docs/FINAL_REPORT.md | - |
| Presentación | 12 diapositivas con contenido, notas del orador e indicación de capturas | ✅ Cumplido | docs/presentacion.md | - |
| Demo | Guion de 11 pasos con scripts automatizados, capturas reales y respuestas a preguntas probables | ✅ Cumplido | docs/GUION_DEMO.md, scripts/preparar_demo.sh, scripts/demo_rotacion.sh, scripts/demo_alterar_log.sql | - |

---

## Resumen

No se declara un resultado de **28/28** ni cumplimiento legal integral. Varias funciones están implementadas, pero los objetivos de cumplimiento, cifrado completo, cobertura de auditoría, consentimiento y recuperación siguen parciales o requieren evidencia reproducible. El prototipo se limita a una demostración local con datos sintéticos. Consulte cada fila y la DPIA antes de presentar resultados.
