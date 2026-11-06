# Política de Seguridad y Concientización — CriptoMed

**Proyecto:** CriptoMed – Plataforma de Gestión de Historiales Médicos  
**Curso:** DS3031 - Ética y Seguridad de Datos  
**Versión:** 1.0  
**Fecha:** Noviembre 2026  
**Responsable:** Oficial de Datos Personales (por designar en producción)

---

## 1. Propósito

Este documento establece la política de seguridad y concientización para todo el personal que opera o administra CriptoMed. Su objetivo es reducir el riesgo de incidentes causados por error humano — la causa más frecuente de brechas de seguridad en sistemas de salud — y garantizar el cumplimiento de la Ley N° 29733 y su Reglamento D.S. 016-2024-JUS.

---

## 2. Alcance

Aplica a:
- Personal administrativo que accede al sistema para gestión de pacientes y facturación.
- Médicos y doctores que consultan o modifican historiales clínicos.
- Administradores del sistema.
- Auditores internos y externos.
- Cualquier persona con credenciales de acceso a CriptoMed.

---

## 3. Roles y Responsabilidades

| Rol | Responsabilidades de seguridad |
|---|---|
| **Admin** | Crear y revocar cuentas, revisar alertas de seguridad, ejecutar backups, monitorear el Dashboard Oficial |
| **Doctor** | Acceder solo a pacientes asignados, reportar accesos inusuales, no compartir credenciales |
| **Administrativo** | No intentar acceder a campos clínicos (diagnóstico, medicación), reportar errores de acceso |
| **Auditor** | Verificar la cadena de logs mensualmente con `scripts/verificar_cadena_logs.py`, reportar anomalías |
| **Paciente** | Mantener sus credenciales seguras, revisar periódicamente la sección "Quién accedió a mi historial" |

---

## 4. Política de Contraseñas

Alineada con **NIST SP 800-63B** y el **OWASP Password Storage Cheat Sheet**:

- **Longitud mínima:** 12 caracteres.
- **Longitud máxima:** 72 bytes en UTF-8 (límite de bcrypt).
- **Sin reglas de composición forzadas:** No se exigen mayúsculas, números ni símbolos específicos.
- **Sin rotación periódica obligatoria:** Solo se cambia ante sospecha de compromiso.
- **Prohibido:** Contraseñas que contengan el nombre de usuario, email, o que aparezcan en listas de contraseñas comunes (evaluadas con zxcvbn, puntuación mínima 3/4).
- **Almacenamiento:** bcrypt con factor de costo 12. Las contraseñas nunca se almacenan en texto plano ni se registran en logs.

### Qué hacer si sospechas que tu contraseña fue comprometida:
1. Notificar inmediatamente al administrador del sistema.
2. El administrador revoca la cuenta (`PATCH /usuarios/{id}/revocar`).
3. Se crea una nueva cuenta con nueva contraseña.
4. El administrador verifica en los logs de auditoría si hubo accesos no autorizados.

---

## 5. Uso Aceptable del Sistema

**Permitido:**
- Acceder a historiales clínicos únicamente en el contexto de atención al paciente asignado.
- Usar el acceso de emergencia (break-glass) ante situaciones clínicas urgentes, con justificación médica documentada de al menos 20 caracteres.
- Exportar datos propios (solo rol paciente) para ejercer el derecho de portabilidad.

**Prohibido:**
- Compartir credenciales con terceros.
- Intentar acceder a pacientes no asignados sin justificación de emergencia.
- Descargar o copiar masivamente historiales clínicos fuera del sistema.
- Intentar modificar o eliminar registros de auditoría.
- Acceder al sistema desde redes no confiables sin medidas adicionales (VPN, red segura).

---

## 6. Manejo de Incidentes

Ante cualquier sospecha de incidente de seguridad (acceso no autorizado, contraseña comprometida, comportamiento inusual del sistema):

1. **Detección:** El sistema genera alertas automáticas (`GET /audit-logs/alertas`) para fuerza bruta, accesos fuera de horario (07:00–21:00 hora Lima) y volumen anómalo de lecturas.
2. **Notificación inmediata:** Informar al administrador del sistema y al responsable del tratamiento de datos.
3. **Contención:** El administrador puede revocar accesos inmediatamente sin necesidad de cambiar contraseñas.
4. **Notificación a ANPD:** Si el incidente involucra datos personales, notificar a la Autoridad Nacional de Protección de Datos Personales (ANPD) dentro de las **48 horas** de tomar conocimiento, conforme al Reglamento D.S. 016-2024-JUS.
5. **Notificación a titulares:** Informar a los pacientes afectados según los artículos correspondientes del Reglamento.
6. **Reporte al CNSD:** Si el incidente es de naturaleza digital, reportar también al Centro Nacional de Seguridad Digital.

---

## 7. Acceso de Emergencia (Break-Glass)

El mecanismo de acceso de emergencia permite a un doctor acceder temporalmente a un historial no asignado en situaciones clínicas críticas:

- **Requiere:** Justificación médica escrita de al menos 20 caracteres.
- **Duración:** 30 minutos de acceso temporal.
- **Registro:** Queda registrado en la cadena de auditoría SHA-256 como `acceso_emergencia`.
- **Revisión obligatoria:** El auditor debe revisar cada acceso de emergencia dentro de las 24 horas.
- **Principio:** Es un mecanismo excepcional y auditado, no una vía para eludir el control de acceso regular.

---

## 8. Derechos de los Titulares (Pacientes)

Los pacientes tienen los siguientes derechos según la Ley N° 29733:

| Derecho | Cómo ejercerlo en CriptoMed |
|---|---|
| **Acceso** | `GET /pacientes/me` — ver su historial completo descifrado |
| **Portabilidad** | `GET /pacientes/me/export` — descargar sus datos en JSON |
| **Control de acceso** | `GET /pacientes/me/accesos` — ver quién consultó su historial |
| **Transferencia** | `PATCH /pacientes/{id}/transferir-doctor` — cambiar de médico tratante |
| **Información** | El sistema registra la versión y fecha del consentimiento informado |

Para ejercer derechos de cancelación u oposición (no implementados en esta versión), el titular debe contactar directamente al responsable del tratamiento de la clínica.

---

## 9. Capacitación (Plan para Producción)

En este prototipo académico, la política está documentada en este archivo. En un entorno de producción con personal real, se implementaría:

| Actividad | Frecuencia | Responsable |
|---|---|---|
| Inducción de seguridad para personal nuevo | Al incorporarse | Oficial de Datos Personales |
| Capacitación anual en Ley 29733 y manejo de datos de salud | Anual | Oficial de Datos Personales |
| Simulacro de phishing | Semestral | Oficial de Datos Personales + TI |
| Revisión de accesos y roles activos | Trimestral | Administrador del sistema |
| Prueba de restauración de backups | Semestral | Administrador del sistema |
| Verificación de cadena de logs | Mensual | Auditor |

---

## 10. Vigencia y Revisión

Esta política entra en vigencia en noviembre de 2026 y debe revisarse:
- Anualmente como parte de la revisión de la DPIA (ver `docs/DPIA.md`).
- Ante cambios significativos en el sistema o en la normativa aplicable.
- Después de cualquier incidente de seguridad que afecte datos personales.

**Referencias:** Ley N° 29733; Reglamento D.S. 016-2024-JUS; NIST SP 800-63B; OWASP Password Storage Cheat Sheet; NIST SP 800-61; NIST SP 800-92.
