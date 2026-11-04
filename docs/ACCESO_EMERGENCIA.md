# Protocolo de Acceso de Emergencia (*Break-Glass*)

## 1. Contexto y Dilema Ético (Seguridad vs. Vida)

En entornos de salud digital, el principio de **mínimo privilegio (NIST SP 800-53 / OWASP ASVS)** establece que un médico solo debe acceder a los expedientes de sus pacientes asignados. Sin embargo, en una situación de **urgencia médica vital** (ej. paciente inconsciente en sala de trauma ingresado de imprevisto o con doctor titular ausente), denegar el acceso a antecedentes de alergias, medicación o grupo sanguíneo puede ocasionar la muerte del paciente.

El marco legal peruano contempla expresamente esta contingencia:
- **Ley N° 29733 (Art. 14 inc. 3 y Art. 17 inc. b)**: No se requiere el consentimiento previo del titular cuando el tratamiento de datos sensibles sea necesario por razones de salud pública o de urgencia médica en situaciones de emergencia.
- **HIPAA Security Rule (45 CFR § 164.312(a)(2)(ii))**: Exige a los sistemas clínicos contar con un *Emergency Access Procedure* (procedimiento documentado y técnico para obtener información crítica en caso de emergencia).

---

## 2. Implementación Técnica en CriptoMed

El protocolo **Break-Glass** de CriptoMed resuelve la tensión ética permitiendo la atención inmediata sin anular la seguridad, mediante un mecanismo **estrictamente auditado, justificado y con expiración automática**:

```
                       [ Doctor No Asignado ]
                                  │
                                  ▼
     POST /pacientes/{id}/acceso-emergencia
     Body: { "justificacion": "≥ 20 caracteres obligatorios" }
                                  │
         ┌────────────────────────┴────────────────────────┐
         │                                                 │
         ▼                                                 ▼
[ Ventana Temporal 30 Min ]                 [ Cadena SHA-256 NIST SP 800-92 ]
- Tabla: accesos_emergencia                 - Acción: acceso_emergencia
- Registro de expira_en                     - Recurso: paciente:{id}
- Permiso dinámico en /pacientes/{id}       - Detalle: justificación médica
         │                                                 │
         │                                                 ▼
         │                                    [ Alerta Auditor Forense ]
         │                                    - GET /audit-logs/alertas
         │                                    - Severidad: ALTA (revisión inmediata)
         │                                                 │
         └────────────────────────┬────────────────────────┘
                                  ▼
                   [ Transparencia al Paciente ]
                   - GET /pacientes/me/accesos
                   - Marcado como: 🚨 Acceso de Emergencia
```

---

## 3. Controles Técnicos Implementados

1. **Restricción RBAC de Mínimo Privilegio**: Exclusivo para usuarios con rol `doctor`. Administrativos, auditores o terceros reciben `HTTP 403 Forbidden`.
2. **Justificación Médica Obligatoria**: Se exige un texto explicativo con un mínimo de **20 caracteres** (ej. `"Paciente en paro cardiorrespiratorio en trauma shock sin contacto con médico de cabecera"`). Solicitudes vacías o superficiales son rechazadas (`HTTP 400 Bad Request`).
3. **Ventana Temporal Estricta (30 Minutos)**: El acceso no es permanente; expira automáticamente transcurridos 30 minutos desde la emisión. Al vencer el plazo, las consultas subsiguientes a `GET /pacientes/{id}` vuelven a retornar `HTTP 403 Forbidden`.
4. **Trazabilidad Inmutable**: Cada invocación escribe un bloque en la cadena criptográfica SHA-256 (`audit_logs`) con la justificación y la IP del cliente.
5. **Detección y Alerta Inmediata**: Aparece de forma prioritaria en `GET /audit-logs/alertas` como alerta `ACCESO_EMERGENCIA_BREAK_GLASS` (severidad ALTA) para que el comité de ética médica y el auditor institucional auditen el evento a posteriori.
6. **Derecho de Información del Titular**: El paciente visualiza el acceso de emergencia en su propio panel (`/pacientes/me/accesos`) con un distintivo visible y la justificación dada por el facultativo.
