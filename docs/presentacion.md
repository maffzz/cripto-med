# Presentación - CriptoMed

**Proyecto:** CriptoMed – Plataforma de Gestión de Historiales Médicos  
**Curso:** DS3031 - Ética y Seguridad de Datos  
**Estudiante:** María Lazon  
**Fecha:** Noviembre 2026  
**Diapositivas:** 12

---

## Diapositiva 1: Portada y problema

**Título:** CriptoMed: Gestión Segura de Historiales Médicos para Clínicas Pequeñas en Perú

**Viñetas:**
- Problema: Clínicas pequeñas manejan historiales en papel o spreadsheets sin protección
- Riesgos: Pérdida de información, acceso no autorizado, incumplimiento de Ley 29733
- Solución: Plataforma web con cifrado AES-256-GCM, RBAC, logs inmutables y TLS 1.3
- Resultado: 100% de campos sensibles cifrados, reducción del 61.18% en hallazgos de seguridad

**Notas del orador:**
> "Buenos días. Mi proyecto es CriptoMed, una plataforma para que clínicas pequeñas en Perú gestionen historiales médicos de forma segura. El problema es que actualmente usan papel o spreadsheets sin protección, lo que expone datos sensibles. Mi solución cifra datos con AES-256-GCM, controla accesos por roles y registra todo en logs inmutables. Logré reducir los hallazgos de seguridad en un 61% tras aplicar herramientas de análisis."

**Captura/diagrama:** Captura de la aplicación en https://localhost:8443

---

## Diapositiva 2: Contexto y usuarios

**Título:** Contexto normativo y usuarios

**Viñetas:**
- Ley 29733: Datos de salud son sensibles (Art. 3), medidas técnicas obligatorias (Art. 5), notificación de incidentes a ANPD (Art. 10)
- Reglamento D.S. 016-2024-JUS: Obligaciones de responsables y encargados (Decreto Supremo N° 016-2024-JUS, 30 noviembre 2024)
- ANPD: Autoridad Nacional de Protección de Datos Personales
- Usuarios: 5 roles (admin, doctor, administrativo, auditor, paciente)
- Caso de uso: Clínica pequeña con 3 doctores, 2 administrativos, ~55,000 pacientes

**Notas del orador:**
> "El marco normativo peruano establece que los datos de salud son sensibles y requieren medidas técnicas como cifrado y control de acceso. El Reglamento define obligaciones específicas para responsables y encargados. Mi sistema tiene 5 roles para implementar mínimo privilegio: admin, doctor, administrativo, auditor y paciente. El caso de uso es una clínica pequeña con miles de pacientes."

**Captura/diagrama:** Tabla de roles del README

---

## Diapositiva 3: Resumen de la Entrega 1

**Título:** Entrega 1: Fundamentos

**Viñetas:**
- Dataset: Healthcare Dataset (55,500 registros sintéticos) + CIE-10 (14,409 códigos)
- Caso de negocio: Reducir tiempo de acceso de ~10 min a <30 seg
- KPIs: Campos sensibles cifrados, accesos registrados, cumplimiento Ley 29733
- Arquitectura base: FastAPI + React + PostgreSQL, desplegado en Render y GitHub Pages
- Cifrado inicial: Fernet (AES-128-CBC + HMAC)
- Limitación: Fernet no es estándar NIST, usa 128 bits

**Notas del orador:**
> "En la Entrega 1, usé un dataset sintético de 55,000 pacientes y códigos CIE-10 de la OMS. El objetivo era reducir el tiempo de acceso de 10 minutos a menos de 30 segundos. La arquitectura base usaba FastAPI, React y PostgreSQL, desplegado en servicios cloud. Inicialmente cifré con Fernet, que usa AES-128. Esto fue una limitación que corregí en la Entrega 2."

**Captura/diagrama:** Diagrama de arquitectura de la Entrega 1 (opcional)

---

## Diapositiva 4: Arquitectura final

**Título:** Arquitectura Docker Compose (Entrega 2)

**Viñetas:**
- Migración a despliegue local con Docker Compose para control de aislamiento de red
- Servicios: Edge Nginx (TLS 1.3), Backend FastAPI, PostgreSQL 16, Init (seed), Backup
- Redes: app_net (no internal para edge), db_net (internal para PostgreSQL)
- Solo edge publica puerto 8443 al host
- Contenedores no-root, cap_drop ALL, read-only filesystem, tmpfs

**Notas del orador:**
> "Para la Entrega 2, migré a despliegue local con Docker Compose. Esto me da control completo sobre aislamiento de red y terminación TLS. La arquitectura tiene edge Nginx que termina TLS 1.3, backend FastAPI, PostgreSQL en red interna, y servicios de inicialización y backup. Solo el edge publica un puerto al host. Implementé contenedores no-root, capacidades mínimas y filesystem de solo lectura."

**Captura/diagrama:** Diagrama Mermaid de arquitectura del README

---

## Diapositiva 5: Cifrado en reposo y rotación de llaves

**Título:** Migración a AES-256-GCM

**Viñetas:**
- Decisión: Migrar de Fernet (AES-128) a AES-256-GCM (FIPS 197, NIST SP 800-38D)
- Por qué: AES-256 es estándar NIST, GCM tiene autenticación integrada (tag)
- Llaves versionadas: ENC_KEYS formato v1:base64url, v2:base64url, ENC_KEY_CURRENT define la activa
- AAD (datos asociados): pacientes.nombre.{id} previene copia entre registros
- Rotación: script rotate_keys.py migra datos en lotes con rollback ante fallo
- Evidencia: SELECT muestra campos con prefijo v2:..., scripts/verificar_cifrado.py

**Notas del orador:**
> "Migré de Fernet a AES-256-GCM porque este es estándar NIST y usa 256 bits. Las llaves están versionadas, permitiendo rotación sin interrumpir el servicio. El AAD vincula el cifrado al ID del paciente, evitando que un atacante copie valores cifrados entre registros. Este cambio respondió a la observación del profesor en la Entrega 1."

**Captura/diagrama:** Captura de SELECT con datos cifrados (v2:...)

---

## Diapositiva 6: Identidad y acceso

**Título:** Autenticación, RBAC y transferencia del paciente

**Viñetas:**
- Contraseñas: bcrypt factor 12, política NIST SP 800-63B (sin rotación obligatoria)
- JWT: HS256, expiración 30 min, verificación de activo en cada request
- Bloqueo: 5 intentos fallidos → bloqueo 15 min, rate limiting 10 req/min
- RBAC: 5 roles, filtrado en backend (administrativo NO ve diagnósticos)
- Transferencia self-service: Paciente puede transferir a otro doctor
- Evidencia: Login fallido → bloqueo, Doctor B no ve paciente demo, transferencia en GUION_DEMO.md

**Notas del orador:**
> "Las contraseñas se hashean con bcrypt factor 12. JWT expira en 30 minutos y verifico que el usuario esté activo en cada request para permitir revocación inmediata. Bloqueo tras 5 intentos fallidos previene fuerza bruta. El RBAC filtra en el servidor: el administrativo no ve diagnósticos. El paciente puede transferir su historial a otro doctor self-service, cumpliendo con autonomía del titular."

**Captura/diagrama:** Captura de transferencia de doctor en frontend

---

## Diapositiva 7: Trazabilidad

**Título:** Logs inmutables con cadena SHA-256

**Viñetas:**
- Registro: login, lectura, edicion, borrado, transferencia, exportacion, acceso_emergencia
- Cadena SHA-256: hash_prev, hash_actual, seq autoincremental
- pg_advisory_xact_lock: serializa escrituras para evitar condiciones de carrera
- Triggers anti-UPDATE/DELETE: Rol de aplicación con solo INSERT/SELECT
- Verificación: scripts/verificar_cadena_logs.py detecta alteración
- Alertas: login_fallido, fuera de horario, volumen inusual
- Evidencia: Demo de alteración de log → verificación FALLA

**Notas del orador:**
> "Todos los accesos se registran en logs con cadena SHA-256. Cada registro tiene el hash del anterior, detectando cualquier alteración. Usé locks de PostgreSQL para serializar escrituras y triggers para impedir UPDATE/DELETE en logs. Si un atacante altera un registro manualmente, la cadena se rompe y el sistema lo detecta, como muestra la demo."

**Captura/diagrama:** Captura de verificación de cadena de logs (OK/FALLA)

---

## Diapositiva 8: Análisis con herramientas

**Título:** Verificación con herramientas de seguridad

**Viñetas:**
- Herramientas: Bandit (SAST), pip-audit (SCA), npm audit, Gitleaks, Hadolint, Trivy, testssl.sh, OWASP ZAP
- Resultados iniciales: 3,596 hallazgos
- Resultados finales: 1,396 hallazgos (reducción del 61.18%)
- Correcciones principales:
  - SEC-BANDIT-01/02: Inyección SQL en verificar_restauracion.py
  - SEC-PIP-03/04: python-multipart y python-dotenv actualizados
  - SEC-HADO-02/03/04: Buenas prácticas Docker
  - SEC-ZAP-01: Cabecera Cross-Origin-Resource-Policy agregada
- Evidencia: docs/hallazgos.md, docs/comparativa_antes_despues.md

**Notas del orador:**
> "Apliqué 8 herramientas de seguridad antes y después de las correcciones. Reduje los hallazgos en un 61%. Corregí inyecciones SQL, actualicé dependencias vulnerables, mejoré Dockerfiles y agregué cabeceras de seguridad. Esto demuestra mejora continua de la postura de seguridad, cumpliendo el requisito de aplicar herramientas y no solo describirlas."

**Captura/diagrama:** Tabla comparativa de docs/comparativa_antes_despues.md

---

## Diapositiva 9: DPIA

**Título:** Evaluación de Impacto en la Protección de Datos

**Viñetas:**
- DPIA completa conforme a GDPR Art. 35 e ISO/IEC 29134
- 5 riesgos principales para titulares:
  - Fuga masiva de base de datos (riesgo residual: 2, mitigado por AES-256-GCM)
  - Acceso indebido personal interno (riesgo residual: 2, mitigado por RBAC + logs)
  - Reidentificación por cuasi-identificadores (riesgo residual: 2, mitigado por cifrado de nombre)
  - Indisponibilidad en emergencia (riesgo residual: 2, mitigado por break-glass)
  - Retención excesiva (riesgo residual: 3, pendiente política de retención)
- Ciclo de vida: recolección → almacenamiento → uso → compartición → transmisión → retención → eliminación
- Evidencia: docs/DPIA.md, docs/inventario_datos.md

**Notas del orador:**
> "Completé una DPIA evaluando riesgos para los titulares de datos. Los riesgos principales son fuga de datos, acceso indebido, reidentificación, indisponibilidad y retención excesiva. Todos tienen riesgo residual bajo-medio tras implementar controles como AES-256-GCM, RBAC y logs inmutables. El punto más alto es retención excesiva, que requiere implementar una política de retención conforme a norma técnica MINSA."

**Captura/diagrama:** Tabla de riesgos de docs/DPIA.md

---

## Diapositiva 10: Objetivos vs. resultados

**Título:** Cumplimiento de objetivos

**Viñetas:**
- Total objetivos: 28
- Cumplidos: 26
- Parciales: 2 (expiración por inactividad, capacitación ejecutada)
- No cumplidos: 0
- KPIs alcanzados:
  - Tiempo de acceso: <30 seg (80% reducción)
  - Campos sensibles cifrados: 100%
  - Accesos registrados: 100%
  - Backups cifrados: Sí, RPO 24h, RTO <30 min
- Herramienta de análisis: Aplicada (61.18% reducción)
- DPIA: Completa con 12 riesgos
- Evidencia: docs/objetivos_vs_resultados.md

**Notas del orador:**
> "Cumplí 26 de 28 objetivos. Los parciales son expiración por inactividad en frontend (mejora futura con refresh token) y capacitación ejecutada (no aplicable en prototipo sin personal real). Todos los KPIs fueron alcanzados: reducción del tiempo de acceso, 100% de campos sensibles cifrados, 100% de accesos registrados, backups cifrados. La herramienta de análisis se aplicó con reducción del 61% en hallazgos."

**Captura/diagrama:** Tabla de docs/objetivos_vs_resultados.md

---

## Diapositiva 11: Lo que no se logró y trabajo futuro

**Título:** Limitaciones y trabajo futuro

**Viñetas:**
- No se logró:
  - Expiración por inactividad en backend (mejora futura: refresh token)
  - Capacitación ejecutada (no aplicable en prototipo)
  - Política de retención y anonimización (pendiente: verificar norma técnica MINSA)
  - Canal formal de ejercicio de derechos del titular
  - Dashboard para Oficial de Datos Personales
- Trabajo futuro:
  - MFA para todos los roles
  - Certificado de CA reconocida (Let's Encrypt)
  - Llaves en KMS/HSM con cifrado de sobre
  - WAF (Web Application Firewall)
  - Argon2id para hashing de contraseñas
  - Cookie HttpOnly + Secure + SameSite con protección CSRF
  - Anclaje externo del hash de logs
  - Monitoreo centralizado de logs

**Notas del orador:**
> "Las limitaciones principales son expiración por inactividad en backend y falta de política de retención. Para el futuro, recomiendo MFA, certificados de Let's Encrypt, llaves en HSM, WAF y migrar a Argon2id para contraseñas. También necesito implementar un canal formal para ejercer derechos del titular y un dashboard para el Oficial de Datos Personales."

**Captura/diagrama:** Tabla de recomendaciones de docs/FINAL_REPORT.md

---

## Diapositiva 12: Lecciones aprendidas y paso a la demo

**Título:** Lecciones aprendidas

**Viñetas:**
- **Empezar:** Verificar especificación antes de afirmar (Fernet vs. AES-256 enseñó esto)
- **Empezar:** Hacer DPIA y modelo de amenazas ANTES de programar
- **Empezar:** Definir roles sin contradicciones desde el inicio
- **Empezar:** Automatizar escaneos desde el día 1
- **Continuar:** Dividir trabajo en fases con un commit por paso
- **Continuar:** Documentar mientras se desarrolla
- **Parar:** Cifrar con librería no es lo mismo que justificar el algoritmo
- **Parar:** El código generado con IA necesita revisión humana
- **Parar:** Escanear secretos desde el día 1 (evité publicarlos)
- **Reflexión:** La transferencia de doctor salió de validar con el profesor a tiempo

**Notas del orador:**
> "Las lecciones clave son: verificar especificaciones antes de afirmar, hacer DPIA antes de programar, definir roles sin contradicciones, y automatizar escaneos. Dividir en fases con commits por paso funcionó bien. Debo parar de asumir que cifrar con una librería es suficiente sin justificar el algoritmo. El código generado con IA necesita revisión. Escanear secretos desde el día 1 evitó publicar información sensible. Ahora les mostraré la demo en vivo."

**Captura/diagrama:** Captura de GUION_DEMO.md o inicio de demo

---

## Notas para PowerPoint/Google Slides

**Instrucciones para el orador:**
- Menos texto, más tablas y capturas
- Usar las capturas indicadas en cada diapositiva
- La demo en vivo dura 10-12 minutos (ver GUION_DEMO.md)
- Preguntas probables:
  - ¿Por qué GCM y no Fernet? → GCM es estándar NIST, 256 bits
  - ¿Dónde guardas la llave? → Variables de entorno (KMS en producción)
  - ¿Qué pasa si se pierde la llave? → Datos irrecuperables (backups separados)
  - ¿Por qué certificado autofirmado? → Para demo, producción usa Let's Encrypt
