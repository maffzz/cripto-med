# Inventario de Datos - CriptoMed

**Proyecto:** CriptoMed — Plataforma de Gestión de Historias Clínicas  
**Asignatura:** DS3031 Ética y Seguridad de Datos (Entrega 2)  
**Fecha:** Noviembre 2026  
**Fase:** Fase 3 - DPIA y Consideraciones Éticas (Paso 3.1)

Este documento inventaría todos los campos de datos que el sistema CriptoMed almacena, clasificándolos según su sensibilidad, nivel de cifrado, acceso por rol y finalidad. Sirve como base para la Evaluación de Impacto en la Protección de Datos (DPIA) conforme a GDPR Art. 35 e ISO/IEC 29134.

---

## Tabla de Inventario de Datos

| Campo | Descripción | Categoría | ¿Cifrado en reposo? | Roles que pueden verlo | Finalidad | ¿Es necesario? (sí/no + razón) |
|-------|-------------|-----------|---------------------|------------------------|-----------|-------------------------------|
| **usuarios.id** | UUID único identificador del usuario | Identificador técnico | No | Todos los roles (interna) | Clave primaria para relaciones de base de datos | Sí - Requerido por diseño de base de datos |
| **usuarios.nombre** | Nombre completo del usuario (personal médico, administrativo, auditor) | Cuasi-identificador | No | admin, auditor, auditor (self) | Identificación del personal en logs y UI | Sí - Necesario para auditoría y trazabilidad |
| **usuarios.email** | Correo electrónico único del usuario | Identificador directo | No | admin, auditor, auditor (self) | Autenticación (login) y comunicación | Sí - Requerido para autenticación con JWT |
| **usuarios.password_hash** | Hash bcrypt (factor de costo 12) de la contraseña | Dato técnico | No | Ninguno (sistema interno) | Verificación de credenciales de autenticación | Sí - Requerido por seguridad (OWASP Password Storage Cheat Sheet) |
| **usuarios.rol** | Rol RBAC (admin, doctor, administrativo, auditor, paciente) | Dato técnico | No | admin, auditor, auditor (self) | Control de acceso basado en roles (mínimo privilegio) | Sí - Requerido por principio de mínimo privilegio |
| **usuarios.activo** | Estado booleano de cuenta activa/desactivada | Dato técnico | No | admin, auditor, auditor (self) | Revocación inmediata de accesos (RFC 8725) | Sí - Requerido para gestión de accesos |
| **usuarios.intentos_fallidos** | Contador de intentos de login fallidos | Dato técnico | No | Ninguno (sistema interno) | Bloqueo por fuerza bruta (NIST SP 800-63B) | Sí - Requerido por política de contraseñas |
| **usuarios.bloqueado_hasta** | Timestamp hasta el cual la cuenta está bloqueada | Dato técnico | No | Ninguno (sistema interno) | Bloqueo temporal por exceso de intentos fallidos | Sí - Requerido por política de contraseñas |
| **usuarios.creado_en** | Timestamp de creación de cuenta | Dato técnico | No | admin, auditor | Trazabilidad de creación de usuarios | Sí - Requerido para auditoría |
| **pacientes.id** | UUID único identificador del paciente | Identificador técnico | No | Todos los roles (interna) | Clave primaria para relaciones de base de datos | Sí - Requerido por diseño de base de datos |
| **pacientes.nombre** | Nombre completo del paciente | Identificador directo | **Sí (AES-256-GCM)** | admin, doctor, paciente (self), administrativo (self) | Identificación del paciente en historial clínico | Sí - Requerido por Ley 29733 (identificación del titular) |
| **pacientes.edad** | Edad del paciente en años | Cuasi-identificador | No | admin, doctor, paciente (self), administrativo | Evaluación clínica y estadística | Sí - Requerido para contexto clínico (puede ser cuasi-identificador combinado) |
| **pacientes.genero** | Género del paciente | Cuasi-identificador | No | admin, doctor, paciente (self), administrativo | Evaluación clínica y estadística | Sí - Requerido para contexto clínico (puede ser cuasi-identificador combinado) |
| **pacientes.tipo_sangre** | Tipo de sangre (A+, B-, O+, etc.) | Dato de salud | No | admin, doctor, paciente (self), administrativo | Transfusiones y procedimientos médicos | Sí - Requerido para atención médica |
| **pacientes.diagnostico** | Diagnóstico médico textual | Dato de salud sensible | **Sí (AES-256-GCM)** | admin, doctor, paciente (self) | **NO** visible para administrativo (Paso 0.3) | Sí - Requerido por historia clínica (dato sensible Ley 29733 Art. 3) |
| **pacientes.codigo_cie10** | Código CIE-10 de diagnóstico (FK a diagnosticos_cie10) | Dato de salud | No | admin, doctor, paciente (self) | **NO** visible para administrativo (Paso 0.3) | Sí - Requerido para estandarización clínica (OMS CIE-10) |
| **pacientes.fecha_admision** | Fecha de admisión al hospital | Cuasi-identificador | No | admin, doctor, paciente (self), administrativo | Cronología de atención y estadística | ⚠️ **Cuasi-identificador**: combinado con edad + género + hospital puede reidentificar a una persona. Necesario para timeline clínico. |
| **pacientes.doctor_id** | FK al usuario médico asignado | Identificador técnico | No | admin, doctor, paciente (self), administrativo | Asignación de responsabilidad médica | Sí - Requerido por RBAC (mínimo privilegio) |
| **pacientes.usuario_id** | FK opcional a cuenta de login del paciente | Identificador técnico | No | admin, auditor, paciente (self) | Autenticación self-service del paciente | Sí - Requerido para funcionalidad de paciente (Paso 1.7) |
| **pacientes.hospital** | Nombre del hospital | Cuasi-identificador | No | admin, doctor, paciente (self), administrativo | ⚠️ **Cuasi-identificador**: combinado con fecha_admision + edad + género puede reidentificar. Necesario para contexto de atención. |
| **pacientes.proveedor_seguro** | Nombre de seguro médico | Dato financiero | No | admin, doctor, paciente (self), administrativo | Facturación y coberturas | Sí - Requerido para gestión administrativa |
| **pacientes.monto_facturado** | Monto monetario facturado | Dato financiero | **Sí (AES-256-GCM)** | admin, doctor, paciente (self), administrativo | Registro financiero | Sí - Requerido para facturación (dato financiero Ley 29733) |
| **pacientes.numero_habitacion** | Número de habitación o cama | Cuasi-identificador | No | admin, doctor, paciente (self), administrativo | Logística hospitalaria | ⚠️ **Cuasi-identificador**: puede contribuir a reidentificación en combinación. Necesario para logística. |
| **pacientes.tipo_admision** | Tipo de admisión (urgencia, programada, etc.) | Dato de salud | No | admin, doctor, paciente (self), administrativo | Clasificación de atención | Sí - Requerido para contexto clínico |
| **pacientes.fecha_alta** | Fecha de alta/dada de alta | Cuasi-identificador | No | admin, doctor, paciente (self), administrativo | Duración de estancia y cronología | ⚠️ **Cuasi-identificador**: combinado con fecha_admision puede inferir estancia. Necesario para timeline. |
| **pacientes.medicacion** | Medicación prescrita | Dato de salud sensible | **Sí (AES-256-GCM)** | admin, doctor, paciente (self) | **NO** visible para administrativo (Paso 0.3) | Sí - Requerido por historia clínica (dato sensible Ley 29733 Art. 3) |
| **pacientes.resultado_test** | Resultados de pruebas de laboratorio | Dato de salud sensible | **Sí (AES-256-GCM)** | admin, doctor, paciente (self) | **NO** visible para administrativo (Paso 0.3) | Sí - Requerido por historia clínica (dato sensible Ley 29733 Art. 3) |
| **pacientes.consentimiento_fecha** | Fecha de consentimiento del paciente | Dato técnico | No | admin, doctor, paciente (self), administrativo | Cumplimiento de consentimiento informado (Ley 29733) | Sí - Requerido por cumplimiento legal (Paso 1.7) |
| **pacientes.consentimiento_version** | Versión del documento de consentimiento | Dato técnico | No | admin, doctor, paciente (self), administrativo | Trazabilidad de cambios en políticas de consentimiento | Sí - Requerido para gestión de consentimiento (Paso 1.7) |
| **diagnosticos_cie10.codigo** | Código CIE-10 (clave primaria) | Dato técnico | No | admin, doctor, paciente (self) | Estándar internacional de diagnósticos (OMS) | Sí - Requerido para estandarización clínica |
| **diagnosticos_cie10.descripcion** | Descripción textual del diagnóstico CIE-10 | Dato de salud | No | admin, doctor, paciente (self) | Interpretación de código CIE-10 | Sí - Requerido para comprensión de diagnóstico |
| **audit_logs.id** | UUID único del log de auditoría | Identificador técnico | No | Ninguno (sistema interno) | Clave primaria de tabla de auditoría | Sí - Requerido por diseño de base de datos |
| **audit_logs.seq** | Secuencia autoincremental única | Dato técnico | No | admin, auditor | Orden cronológico e integridad de cadena de hashes | Sí - Requerido para cadena de hashes SHA-256 (NIST SP 800-92) |
| **audit_logs.hash_prev** | Hash SHA-256 del registro anterior | Dato técnico | No | Ninguno (sistema interno) | Verificación de integridad de cadena de auditoría | Sí - Requerido para inmutabilidad (NIST SP 800-92) |
| **audit_logs.hash_actual** | Hash SHA-256 del registro actual | Dato técnico | No | Ninguno (sistema interno) | Verificación de integridad de cadena de auditoría | Sí - Requerido para inmutabilidad (NIST SP 800-92) |
| **audit_logs.usuario_id** | FK al usuario que realizó la acción | Identificador técnico | No | admin, auditor | Trazabilidad de quién realizó la acción | Sí - Requerido para auditoría (OWASP Logging Cheat Sheet) |
| **audit_logs.accion** | Acción realizada (login, lectura, edicion, etc.) | Dato técnico | No | admin, auditor | Clasificación de eventos de auditoría | Sí - Requerido para auditoría (OWASP Logging Cheat Sheet) |
| **audit_logs.recurso** | Recurso afectado (ej: "paciente:uuid") | Dato técnico | No | admin, auditor | Contexto del evento de auditoría | Sí - Requerido para auditoría (OWASP Logging Cheat Sheet) |
| **audit_logs.timestamp** | Timestamp UTC del evento | Dato técnico | No | admin, auditor | Cronología de eventos | Sí - Requerido para auditoría (NIST SP 800-92) |
| **audit_logs.ip_origen** | Dirección IP de origen del evento | Dato técnico | No | admin, auditor | Detección de accesos anómalos y forense | Sí - Requerido para seguridad (Paso 1.4) |
| **audit_logs.detalle** | Detalle adicional opcional (ej: justificación emergencia) | Dato técnico | No | admin, auditor | Contexto adicional para eventos complejos | Sí - Requerido para casos especiales (acceso emergencia, transferencia) |
| **accesos_emergencia.id** | UUID único del acceso de emergencia | Identificador técnico | No | Ninguno (sistema interno) | Clave primaria de accesos de emergencia | Sí - Requerido por diseño de base de datos |
| **accesos_emergencia.paciente_id** | FK al paciente afectado | Identificador técnico | No | admin, auditor | Trazabilidad de acceso de emergencia | Sí - Requerido para auditoría de break-glass |
| **accesos_emergencia.doctor_id** | FK al doctor que solicitó acceso | Identificador técnico | No | admin, auditor | Trazabilidad de quién solicitó acceso | Sí - Requerido para auditoría de break-glass |
| **accesos_emergencia.justificacion** | Justificación médica del acceso (mínimo 20 caracteres) | Dato técnico | No | admin, auditor | Contexto del acceso de emergencia | Sí - Requerido por política de break-glass (Paso 1.8) |
| **accesos_emergencia.otorgado_en** | Timestamp de otorgamiento del acceso | Dato técnico | No | admin, auditor | Cronología de ventana temporal | Sí - Requerido para gestión de ventana de 30 minutos |
| **accesos_emergencia.expira_en** | Timestamp de expiración del acceso | Dato técnico | No | admin, auditor | Control de ventana temporal de acceso | Sí - Requerido para expiración automática de break-glass |

---

## Cuasi-Identificadores Críticos

Los siguientes campos, aunque no identifican a una persona por sí solos, pueden **combinarse** para reidentificar a un paciente:

1. **edad + género + fecha_admision + hospital**: Esta combinación puede identificar a un paciente en clínicas pequeñas donde la cantidad de admisiones por día es limitada.
2. **edad + género + fecha_admision + tipo_admision**: En emergencias, esta combinación puede ser altamente identificativa.
3. **numero_habitacion + fecha_admision**: La asignación de habitaciones en un hospital suele ser secuencial y combinada con fechas puede inferir identidad.

**Mitigación:** Todos estos campos están protegidos por:
- Cifrado en tránsito (TLS 1.3, RFC 8446)
- Control de acceso RBAC estricto (Paso 0.3)
- Logs de auditoría encadenados (NIST SP 800-92)
- Aislamiento de red interna Docker (CIS Docker Benchmark)

---

## Campos Cifrados en Reposo

Los siguientes campos están cifrados con **AES-256-GCM** (FIPS 197, NIST SP 800-38D) con datos asociados autenticados (AAD) vinculados al ID del paciente:

| Campo | Razón de cifrado | AAD utilizado |
|-------|------------------|---------------|
| pacientes.nombre | Dato de identificación directa (Ley 29733) | `pacientes.nombre.{id}` |
| pacientes.diagnostico | Dato de salud sensible (Ley 29733 Art. 3) | `pacientes.diagnostico.{id}` |
| pacientes.monto_facturado | Dato financiero (Ley 29733) | `pacientes.monto_facturado.{id}` |
| pacientes.medicacion | Dato de salud sensible (Ley 29733 Art. 3) | `pacientes.medicacion.{id}` |
| pacientes.resultado_test | Dato de salud sensible (Ley 29733 Art. 3) | `pacientes.resultado_test.{id}` |

**Nota:** El uso de AAD (datos asociados autenticados) previene que un valor cifrado pueda copiarse a otro registro o campo sin fallar el descifrado (NIST SP 800-38D).

---

## Referencias Normativas

- **Ley 29733 (Perú):** Art. 3 (Datos sensibles), Art. 5 (Medidas de seguridad), Art. 10 (Notificación de incidentes), Art. 14 (Derechos ARCO)
- **GDPR Art. 35:** Evaluación de Impacto en la Protección de Datos (DPIA)
- **ISO/IEC 29134:** Guía para evaluación de impacto en privacidad
- **NIST SP 800-92:** Guide to Computer Security Log Management
- **NIST SP 800-38D:** Recommendation for Block Cipher Modes of Operation: GCM
- **FIPS 197:** Advanced Encryption Standard (AES)
- **OWASP Logging Cheat Sheet:** Buenas prácticas de logging
- **OWASP Password Storage Cheat Sheet:** Buenas prácticas de almacenamiento de contraseñas
