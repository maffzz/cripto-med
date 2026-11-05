# Evaluación de Impacto en la Protección de Datos (DPIA) - CriptoMed

**Proyecto:** CriptoMed — Plataforma de Gestión de Historias Clínicas para Clínicas Pequeñas en Perú  
**Asignatura:** DS3031 Ética y Seguridad de Datos (Entrega 2)  
**Fecha:** Noviembre 2026  
**Fase:** Fase 3 - DPIA y Consideraciones Éticas (Paso 3.2)  
**Responsable del tratamiento:** Clínica pequeña (cliente de CriptoMed)  
**Encargado del tratamiento:** CriptoMed Salud Digital (proveedor de software)  
**Normativa aplicable:** Ley 29733 (Perú), Reglamento D.S. 016-2024-JUS, GDPR Art. 35, ISO/IEC 29134

---

## 1. Descripción Sistemática del Tratamiento

### 1.1 ¿Qué datos se tratan?

CriptoMed procesa datos personales de pacientes y personal médico, incluyendo:

**Datos de pacientes (título de datos personales sensibles conforme a Ley 29733 Art. 3):**
- Identificadores directos: nombre, email (solo si tiene cuenta de paciente)
- Datos de salud sensibles: diagnóstico, medicación, resultado_test, tipo_sangre, tipo_admision, codigo_cie10
- Datos financieros: monto_facturado, proveedor_seguro
- Cuasi-identificadores: edad, género, fecha_admision, fecha_alta, hospital, numero_habitacion
- Datos técnicos: consentimiento_fecha, consentimiento_version

**Datos de personal médico/administrativo:**
- Identificadores: nombre, email
- Datos técnicos: rol, estado de cuenta (activo/bloqueado), intentos_fallidos, timestamps

**Datos de auditoría:**
- Logs de todas las acciones (login, lectura, edicion, transferencia, exportacion, acceso_emergencia)
- Cadenas de hashes SHA-256 para verificación de integridad
- IPs de origen, timestamps, detalles contextuales

Fuente detallada: `docs/inventario_datos.md`

### 1.2 ¿De quién son los datos?

**Titulares principales:**
- Pacientes de clínicas pequeñas en Perú (datos sintéticos para desarrollo, pero sistema diseñado como si fueran reales)
- Personal médico (doctores, administrativos, auditores)

**Base legal:**
- Ley 29733: Protección de Datos Personales en Perú
- Reglamento D.S. 016-2024-JUS: [VERIFICAR] especifica obligaciones de responsables y encargados
- Consentimiento informado del paciente (registrado en consentimiento_fecha y consentimiento_version)

### 1.3 ¿Para qué se tratan?

**Finalidades principales:**
1. **Gestión clínica:** Historias clínicas electrónicas, diagnósticos, medicación, resultados de pruebas
2. **Gestión administrativa:** Facturación, seguros, admisión, logística hospitalaria
3. **Control de acceso:** Autenticación, autorización por roles (RBAC), auditoría
4. **Cumplimiento legal:** Retención de historias clínicas [VERIFICAR] plazo según norma técnica MINSA
5. **Derechos del titular:** Acceso, portabilidad, control de quién accede (GET /pacientes/me/accesos, GET /pacientes/me/export)

**Base legal:** Ley 29733 Art. 5 (medidas de seguridad), Art. 14 (derechos ARCO)

### 1.4 ¿Quién accede a los datos?

**Control de acceso basado en roles (RBAC - mínimo privilegio):**
- **admin:** Acceso total a todos los datos del sistema
- **doctor:** Solo pacientes asignados (doctor_id), ve todos los campos clínicos
- **administrativo:** Datos básicos + facturación, **NO** ve diagnóstico ni medicación (Paso 0.3)
- **auditor:** Solo logs de auditoría, ningún dato de paciente
- **paciente:** Solo su propio historial, puede exportar datos y ver quién accedió

**Implementación:** `backend/app/rbac.py`, `backend/app/routers/pacientes.py`

### 1.5 ¿Dónde se almacenan?

**Almacenamiento:**
- Base de datos PostgreSQL 16 en contenedor Docker
- Volumen persistente `pgdata` en host (no cifrado a nivel de disco, mitigado por cifrado a nivel aplicación)
- Contenedores backend y db en red interna Docker (db_net: internal), sin acceso desde host
- Solo edge Nginx publica puerto 8443 al host

**Arquitectura:** `docker-compose.yml`, `docs/DOCKER.md`

### 1.6 ¿Por cuánto tiempo se retienen?

**Retención actual:**
- Sin política de eliminación automática implementada en código
- Datos se conservan indefinidamente mientras exista el volumen pgdata
- [VERIFICAR] Norma técnica MINSA probablemente exige conservación de historias clínicas por 15-25 años

**Mitigación pendiente:** Implementar política de retención y anonimización conforme a norma técnica MINSA

---

## 2. Ciclo de Vida de los Datos

| Etapa | Qué ocurre en CriptoMed | Riesgo principal | Control REAL implementado (referencia) |
|-------|------------------------|-----------------|----------------------------------------|
| **Recolección** | Datos ingresados por administrativo en admisión o por paciente (cuenta propia). Campos cifrados en capa aplicación antes de guardar. | Recolección excesiva de datos no necesarios (violación de minimización). | Campos limitados a lo necesario por historia clínica estándar. Cifrado AES-256-GCM en capa aplicación (`backend/app/crypto.py`). Validación Pydantic en schemas (`backend/app/schemas.py`). |
| **Almacenamiento** | Datos almacenados en PostgreSQL 16 en contenedor Docker. Campos sensibles cifrados en reposo. | Fuga masiva de base de datos por vulnerabilidad en contenedor o host. | Cifrado AES-256-GCM en campos sensibles (FIPS 197, NIST SP 800-38D). Red interna Docker db_net (CIS Docker Benchmark 5.8). Contenedores no-root, cap_drop, read_only (CIS Docker Benchmark). Backups cifrados con GPG AES-256 (`scripts/backup.sh`). |
| **Uso** | Personal médico accede vía API FastAPI con JWT. Filtrado por RBAC en backend. Logs de auditoría encadenados. | Acceso indebido por credenciales comprometidas o insider threat. | Autenticación JWT con HS256 (RFC 7519, RFC 8725). RBAC estricto en `backend/app/rbac.py`. Cadena de hashes SHA-256 en audit_logs (NIST SP 800-92). Rate limiting con slowapi (Paso 1.4). Bloqueo por 5 intentos fallidos (NIST SP 800-63B). |
| **Compartición** | Transferencia de paciente a otro doctor (PATCH /pacientes/{id}/transferir-doctor). No se comparte con terceros externos. | Transferencia a doctor equivocado (error humano). | Confirmación explícita en frontend. Registro en audit_logs con detalle. Solo paciente puede iniciar transferencia (autonomía del titular). |
| **Transmisión** | Tráfico entre cliente (navegador) y edge Nginx, y entre edge y backend. | Intercepción de datos en tránsito (MITM). | TLS 1.3 exclusivo en edge (RFC 8446, NIST SP 800-52 Rev. 2). Certificados en volumen de solo lectura. Red interna Docker para backend-db. |
| **Retención** | Datos persistentes en volumen pgdata. Sin política de eliminación. | Retención excesiva más allá del plazo legal. | [PENDIENTE] Implementar política de retención conforme a norma técnica MINSA. Actualmente, solo mitigación por cifrado en reposo. |
| **Eliminación/Anonimización** | Soft delete implementado (DELETE /pacientes/{id}). No hay anonimización automática. | Eliminación incompleta (datos persisten en backups). | Soft delete marcando registro como eliminado. Backups cifrados rotativos (últimos 7 días). [PENDIENTE] Implementar anonimización (borrado de datos personales con conservación de datos clínicos anonimizados para investigación). |

---

## 3. Necesidad y Proporcionalidad

### 3.1 Finalidad

**Finalidad principal:** Gestión de historias clínicas electrónicas para pequeñas clínicas en Perú, cumpliendo con la Ley 29733 de Protección de Datos Personales.

**Proporcionalidad:** El sistema recolecta solo los datos necesarios para:
- Atención médica (diagnóstico, medicación, resultados)
- Gestión administrativa (facturación, seguros)
- Cumplimiento legal (auditoría, trazabilidad)
- Derechos del titular (acceso, portabilidad)

No se recolectan datos irrelevantes (ej: preferencias personales, datos biométricos, ubicación GPS, redes sociales).

### 3.2 Minimización

**Estrategias de minimización implementadas:**
- Rol administrativo NO ve datos clínicos sensibles (diagnóstico, medicación, resultado_test) - Paso 0.3
- Solo el paciente puede ver su historial completo y exportar sus datos
- Auditor solo ve logs, ningún dato de paciente
- Datos sintéticos en desarrollo (no se usan datos reales en pruebas)

**Evidencia:** `backend/app/rbac.py`, `backend/app/routers/pacientes.py`

### 3.3 Consentimiento

**Implementación:**
- Campos `consentimiento_fecha` y `consentimiento_version` en modelo Paciente
- Versión actual: "v1.0"
- Consentimiento registrado al momento de admisión

**Limitación actual:** El sistema asume que el consentimiento se obtiene en el proceso físico de admisión (papel o firma digital). No hay workflow digital de consentimiento explícito en la aplicación.

**Mejora futura:** Implementar pantalla de consentimiento digital con aceptación explícita antes de registrar datos.

### 3.4 Derechos del Titular

**Derechos soportados:**
- ✅ **Derecho de acceso:** GET /pacientes/me (paciente ve su historial)
- ✅ **Derecho de portabilidad:** GET /pacientes/me/export (descarga JSON de sus datos)
- ✅ **Derecho de control de quién accede:** GET /pacientes/me/accesos (lista de accesos)
- ✅ **Derecho a transferir:** PATCH /pacientes/{id}/transferir-doctor (transferencia self-service)
- ✅ **Derecho de rectificación:** PUT /pacientes/{id} (edición por admin/doctor)
- ⚠️ **Derecho de supresión:** DELETE /pacientes/{id} implementado pero solo para admin (soft delete). Paciente no puede solicitar eliminación directamente.

**Derechos NO soportados:**
- ❌ **Derecho de supresión por el titular:** Paciente no tiene endpoint para solicitar eliminación de sus datos.
- ❌ **Derecho de oposición:** No hay mecanismo para oponerse a tratamiento automatizado (no hay decisiones automatizadas).
- ❌ **Derecho a limitación del tratamiento:** No hay endpoint para solicitar limitación de procesamiento.

**Justificación:** El sistema está diseñado para clínicas que tienen obligación legal de conservar historias clínicas por un plazo [VERIFICAR] según norma técnica MINSA. El derecho de supresión entraría en conflicto con esta obligación.

---

## 4. Identificación de Riesgos para los Titulares

### Matriz de Riesgos

| ID | Riesgo | Probabilidad (1-5) | Impacto (1-5) | Riesgo inherente (P×I) | Medidas de mitigación (referencia) | Riesgo residual |
|----|--------|-------------------|---------------|----------------------|----------------------------------|----------------|
| **R-01** | Fuga masiva de la base de datos (vulnerabilidad en contenedor o host) | 2 | 5 | 10 | Cifrado AES-256-GCM en campos sensibles (`backend/app/crypto.py`). Red interna Docker db_net (CIS Docker Benchmark 5.8). Contenedores no-root, cap_drop, read_only. Backups cifrados con GPG. | 2 (bajo-medio) |
| **R-02** | Acceso indebido de personal interno (insider threat) | 3 | 4 | 12 | RBAC estricto (admin, doctor, administrativo, auditor, paciente). Administrativo NO ve datos clínicos. Auditor solo ve logs. Logs de auditoría encadenados SHA-256 (`backend/app/audit.py`). | 2 (bajo) |
| **R-03** | Reidentificación de pacientes mediante combinación de cuasi-identificadores | 3 | 3 | 9 | Cifrado de nombre (identificador directo). Logs de auditoría. Restricción de acceso por rol. Combinación de cuasi-identificadores mitigada por cifrado de nombre. | 2 (bajo) |
| **R-04** | Transferencia de paciente a doctor equivocado (error humano) | 2 | 4 | 8 | Confirmación explícita en frontend con nombres de doctores. Registro en audit_logs con detalle. Solo paciente puede iniciar transferencia. | 1 (bajo) |
| **R-05** | Indisponibilidad en emergencia (sistema caído, bloqueo de cuenta) | 2 | 5 | 10 | Backups cifrados diarios. Acceso de emergencia break-glass (POST /pacientes/{id}/acceso-emergencia) con justificación obligatoria. Healthchecks en contenedores Docker. | 2 (bajo-medio) |
| **R-06** | Retención excesiva de datos más allá del plazo legal | 4 | 3 | 12 | [PENDIENTE] Política de retención no implementada. Mitigación actual: cifrado en reposo. Riesgo aceptado temporalmente. | 3 (medio) |
| **R-07** | Uso secundario no autorizado (minería de datos, venta de datos) | 2 | 5 | 10 | Logs de auditoría encadenados (inmutables). Prohibición contractual en términos de servicio. No hay funcionalidad de exportación masiva para analytics. | 1 (bajo) |
| **R-08** | Error de mapeo CIE-10 (dato clínico incorrecto) | 3 | 4 | 12 | Validación de FK a tabla diagnosticos_cie10. Código CIE-10 de fuente autorizada (OMS). Doctor puede corregir diagnóstico (PUT /pacientes/{id}). | 2 (bajo) |
| **R-09** | Pérdida de llaves de cifrado (incapacidad de descifrar datos) | 1 | 5 | 5 | Llaves en variables de entorno (no en código). Script de rotación de llaves (`scripts/rotate_keys.py`). Backups de llaves separados de backups de datos (requisito en `docs/BACKUPS.md`). | 1 (bajo) |
| **R-10** | Ataque de fuerza bruta a login (cuentas comprometidas) | 3 | 4 | 12 | Bloqueo después de 5 intentos fallidos (NIST SP 800-63B). Rate limiting 10 req/min por IP (slowapi). Contraseñas validadas con zxcvbn (puntuación mínima 3). | 2 (bajo) |
| **R-11** | Intercepción de datos en tránsito (MITM) | 2 | 5 | 10 | TLS 1.3 exclusivo (RFC 8446). Certificados en volumen de solo lectura. No se acepta TLS 1.2. Validación de certificados en navegador. | 1 (bajo) |
| **R-12** | Pérdida de integridad de logs de auditoría (alteración de evidencia) | 2 | 4 | 8 | Cadena de hashes SHA-256 encadenada (NIST SP 800-92). pg_advisory_xact_lock para serialización. Trigger anti-UPDATE/DELETE en audit_logs (`backend/scripts/sql/proteger_audit_logs.sql`). | 1 (bajo) |

**Escala de probabilidad:** 1 (muy baja) - 5 (muy alta)  
**Escala de impacto:** 1 (bajo) - 5 (muy alto)  
**Riesgo inherente:** P × I (máximo 25)  
**Riesgo residual:** Después de aplicar mitigaciones

**Conclusión:** El riesgo residual general es **bajo a medio**. La mayoría de riesgos están mitigados por múltiples controles (defensa en profundidad). El riesgo más alto es R-06 (retención excesiva) que requiere implementación de política de retención.

---

## 5. Consulta y Responsables

### 5.1 Oficial de Datos Personales

**Propuesta para clínica pequeña:**
- En clínicas pequeñas (<50 empleados), el rol de Oficial de Datos Personales puede ser asumido por:
  - El administrador general de la clínica, con capacitación en Ley 29733
  - O un abogado externo contratado específicamente para cumplimiento de datos personales

**Obligaciones del Oficial (conforme a Reglamento D.S. 016-2024-JUS):**
- [VERIFICAR] Artículo específico sobre funciones del Oficial
- Recibir consultas y reclamos de titulares
- Coordinar respuestas a incidentes de seguridad
- Supervisar el cumplimiento de medidas de seguridad
- Mantener registro de tratamientos de datos

**Implementación en CriptoMed:**
- El sistema no implementa funcionalidad específica para el Oficial
- Los endpoints de auditoría (/audit-logs, /audit-logs/alertas) permiten al Oficial monitorear accesos anómalos
- Recomendación: Agregar dashboard específico para Oficial de Datos Personales

### 5.2 Ejercicio de Derechos del Titular

**Mecanismos actuales:**
- **Derecho de acceso:** Paciente puede ver su historial en GET /pacientes/me
- **Derecho de portabilidad:** Paciente puede exportar datos en GET /pacientes/me/export
- **Derecho de rectificación:** Paciente puede solicitar cambios vía contacto con clínica (no hay endpoint directo para paciente)

**Mecanismos faltantes:**
- [VERIFICAR] Canal formal de solicitud de derechos (email, formulario web)
- Tiempos de respuesta estipulados por Reglamento D.S. 016-2024-JUS
- Registro de solicitudes de derechos

**Recomendación:** Implementar módulo de gestión de solicitudes de derechos del titular con tracking de tiempos de respuesta.

---

## 6. Conclusión y Plan de Revisión

### 6.1 Conclusión

CriptoMed implementa controles de seguridad robustos para proteger los datos personales sensibles de pacientes de clínicas pequeñas en Perú:

**Puntos fuertes:**
- Cifrado AES-256-GCM en reposo con llaves versionadas (FIPS 197, NIST SP 800-38D)
- TLS 1.3 exclusivo en tránsito (RFC 8446)
- RBAC estricto con mínimo privilegio (administrativo NO ve datos clínicos)
- Logs de auditoría inmutables con cadena de hashes SHA-256 (NIST SP 800-92)
- Aislamiento de red Docker (CIS Docker Benchmark)
- Backups cifrados con GPG
- Derechos del titular soportados (acceso, portabilidad, control de accesos)

**Puntos a mejorar:**
- Política de retención y anonimización no implementada (R-06)
- Canal formal de ejercicio de derechos del titular no implementado
- Dashboard para Oficial de Datos Personales no implementado
- Consentimiento digital explícito no implementado

**Decisión:** El tratamiento de datos es **proporcionado** y las medidas de seguridad son **adecuadas** para el nivel de riesgo identificado. Se recomienda implementar las mejoras pendientes antes del despliegue en producción real.

### 6.2 Plan de Revisión

**Frecuencia de revisión:** Cada 12 meses o ante cambios importantes en:
- Cambios en la normativa peruana (Ley 29733, Reglamento D.S. 016-2024-JUS)
- Cambios en la arquitectura del sistema (nuevos endpoints, cambios en cifrado)
- Incidentes de seguridad que afecten datos personales
- Nuevas funcionalidades que impliquen tratamiento de datos adicionales

**Responsable de revisión:** Oficial de Datos Personales de la clínica cliente + equipo técnico de CriptoMed

**Referencias:**
- GDPR Art. 35 (DPIA)
- ISO/IEC 29134 (Guía para evaluación de impacto en privacidad)
- Ley 29733 (Perú)
- Reglamento D.S. 016-2024-JUS [VERIFICAR]
- ANPD (Autoridad Nacional de Protección de Datos Personales)

---

## Referencias Normativas

- **GDPR Art. 35:** Evaluación de Impacto en la Protección de Datos
- **ISO/IEC 29134:** Information technology — Security techniques — Privacy impact assessment
- **Ley 29733 (Perú):** Ley de Protección de Datos Personales
- **Reglamento D.S. 016-2024-JUS:** Reglamento de la Ley 29733 [VERIFICAR artículos específicos]
- **ANPD:** Autoridad Nacional de Protección de Datos Personales
- **NIST SP 800-92:** Guide to Computer Security Log Management
- **NIST SP 800-38D:** Recommendation for Block Cipher Modes of Operation: GCM
- **FIPS 197:** Advanced Encryption Standard (AES)
- **RFC 8446:** The Transport Layer Security (TLS) Protocol Version 1.3
- **RFC 7519:** JSON Web Token (JWT)
- **RFC 8725:** JSON Web Token Best Current Practices
- **CIS Docker Benchmark:** Benchmarks for Container Security
- **OWASP Logging Cheat Sheet:** Logging Best Practices
- **OWASP Password Storage Cheat Sheet:** Password Storage Guidelines
