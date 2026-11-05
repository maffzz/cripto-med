# Ética y Privacidad - CriptoMed

**Proyecto:** CriptoMed — Plataforma de Gestión de Historias Clínicas para Clínicas Pequeñas en Perú  
**Asignatura:** DS3031 Ética y Seguridad de Datos (Entrega 2)  
**Fecha:** Noviembre 2026  
**Fase:** Fase 3 - DPIA y Consideraciones Éticas (Paso 3.4)

Este documento presenta las consideraciones éticas y de privacidad de CriptoMed, conectando cada decisión de diseño con implementaciones concretas en el código.

---

## 1. Autonomía y Consentimiento

### 1.1 Transferencia Self-Service del Paciente

**Decisión ética:** El paciente tiene autonomía para decidir qué médico accede a su historial clínico. El sistema no requiere aprobación administrativa para transferencias entre doctores.

**Implementación:**
- Endpoint: `PATCH /pacientes/{id}/transferir-doctor` en `backend/app/routers/pacientes.py` (líneas 500-520)
- Solo el paciente autenticado puede iniciar la transferencia (validación de rol `RolEnum.paciente`)
- Frontend muestra confirmación explícita con nombres del doctor actual y del nuevo doctor
- La transferencia se registra en audit_logs con acción `transferencia` y detalle de doctores anterior y nuevo

**Justificación ética:** Responde al principio de autonomía del paciente (bioética: principio de autonomía) y al derecho de control sobre sus datos personales (Ley 29733 Art. 14 - derecho de oposición/control).

### 1.2 Registro de Consentimiento

**Decisión ética:** El sistema registra el consentimiento del paciente al tratamiento de sus datos de salud.

**Implementación:**
- Campos en modelo Paciente: `consentimiento_fecha` (DateTime) y `consentimiento_version` (String) en `backend/app/models.py` (líneas 75-76)
- Valor por defecto: `"v1.0"`
- El consentimiento se asume obtenido en el proceso físico de admisión (papel o firma digital)

**Limitación actual:** No hay workflow digital de consentimiento explícito en la aplicación. El sistema asume que el consentimiento se obtiene fuera del sistema.

**Mejora futura:** Implementar pantalla de consentimiento digital con aceptación explícita antes de registrar datos.

### 1.3 Vista "Quién Accedió a Mi Historial"

**Decisión ética:** El paciente tiene derecho a saber quién ha accedido a sus datos y cuándo.

**Implementación:**
- Endpoint: `GET /pacientes/me/accesos` en `backend/app/routers/pacientes.py` (líneas 124-177)
- Solo el paciente autenticado puede acceder (validación de rol `RolEnum.paciente`)
- Retorna lista paginada de accesos desde audit_logs filtrados por `recurso == "paciente:{id}"`
- Cada acceso muestra: timestamp, acción, nombre del profesional, rol, IP origen, detalle

**Justificación ética:** Responde al principio de transparencia y al derecho de acceso del titular (Ley 29733 Art. 14, GDPR Art. 15). Permite al paciente detectar accesos indebidos.

---

## 2. Minimización y Finalidad

### 2.1 Por Qué Cada Campo Es Necesario

Basado en `docs/inventario_datos.md`, el sistema recolecta solo los campos necesarios para:

**Atención médica (finalidad primaria):**
- `diagnostico`, `medicacion`, `resultado_test`, `tipo_sangre`, `tipo_admision`, `codigo_cie10`: Necesarios para diagnóstico y tratamiento médico.
- `edad`, `genero`: Necesarios para contexto clínico (pueden ser cuasi-identificadores pero esenciales para medicina).

**Gestión administrativa (finalidad secundaria):**
- `monto_facturado`, `proveedor_seguro`: Necesarios para facturación y coberturas.
- `hospital`, `numero_habitacion`: Necesarios para logística hospitalaria.

**Cumplimiento legal:**
- `consentimiento_fecha`, `consentimiento_version`: Necesarios para cumplimiento de Ley 29733 (consentimiento informado).
- Logs de auditoría: Necesarios para trazabilidad y forense (NIST SP 800-92).

### 2.2 Qué Se Evitó Recolectar

El sistema deliberadamente NO recolecta:
- Datos biométricos (huellas, reconocimiento facial)
- Ubicación GPS
- Datos de redes sociales
- Preferencias personales no relacionadas con salud
- Historial de navegación dentro de la aplicación
- Datos de contacto adicionales (teléfono, dirección) - solo email para autenticación

**Justificación:** Minimización de datos conforme a GDPR Art. 5(1)(c) y Ley 29733 Art. 5 (principio de minimización). Cada campo tiene una finalidad clara y necesaria.

---

## 3. Tensión Ética 1: Derecho de Cancelación vs. Obligación de Conservar Historia Clínica

### 3.1 El Dilema

El paciente tiene derecho a solicitar la supresión de sus datos personales (Ley 29733 Art. 14, GDPR Art. 17). Sin embargo, las clínicas tienen la obligación legal de conservar las historias clínicas por un plazo específico conforme a la norma técnica del MINSA [VERIFICAR plazo exacto].

### 3.2 Solución en CriptoMed

**Implementación actual:**
- Endpoint `DELETE /pacientes/{id}` en `backend/app/routers/pacientes.py` (líneas 482-497)
- Solo disponible para rol `admin` (no para el paciente)
- Implementa soft delete (borrado lógico)
- No hay anonimización automática

**Decisión de diseño:** El paciente NO puede solicitar directamente la eliminación de sus datos. Solo el administrador puede eliminar registros, y esto debe ser coordinado con las obligaciones legales de retención.

**Justificación ética:** Prioriza el interés público en la continuidad de la atención médica y la obligación legal de conservación sobre el derecho individual a la supresión. En emergencias, el historial clínico puede ser vital para el paciente mismo.

**Mejora futura:** Implementar política de retención con anonimización después del plazo legal [VERIFICAR plazo según norma técnica MINSA]. El paciente podría solicitar:
- Eliminación de datos de contacto (email)
- Anonimización de datos personales (nombre → "PACIENTE ANONIMIZADO") después del plazo legal
- Conservación de datos clínicos anonimizados para investigación y estadística

---

## 4. Tensión Ética 2: Seguridad Estricta vs. Atención Oportuna en Emergencias

### 4.1 El Dilema

El principio de seguridad dicta que el acceso a datos sensibles debe ser estrictamente controlado (mínimo privilegio). Sin embargo, en emergencias médicas, un doctor que no está asignado a un paciente puede necesitar acceso inmediato para salvar una vida.

### 4.2 Solución en CriptoMed: Acceso de Emergencia (Break-Glass)

**Implementación:**
- Endpoint: `POST /pacientes/{id}/acceso-emergencia` en `backend/app/routers/pacientes.py` (líneas 332-394)
- Solo disponible para rol `doctor`
- Requiere justificación de al menos 20 caracteres
- Otorga acceso por 30 minutos
- Se registra en audit_logs con acción `acceso_emergencia` y la justificación
- El paciente puede ver accesos de emergencia en `GET /pacientes/me/accesos` (marcados como "acceso de emergencia")

**Justificación ética:** El acceso de emergencia es un mecanismo excepcional y auditado que balancea seguridad con el deber de asistencia médica. No deshabilita la seguridad, sino que añade una capa de accountability transparente.

**Referencia:** NIST SP 800-92 (logging de eventos de seguridad), principios de bioética (beneficencia vs. no maleficencia).

---

## 5. Reidentificación y Datos Sintéticos

### 5.1 Por Qué No Se Usan Datos Reales en Pruebas

**Decisión ética:** El dataset de pacientes proviene de Healthcare Dataset de Kaggle (55,500 registros sintéticos) y códigos CIE-10 de la OMS. No contiene pacientes reales.

**Justificación:**
- Evita exposición de datos personales reales en desarrollo y pruebas
- Permite probar funcionalidades sin riesgo de fuga de datos reales
- El sistema se diseña como si los datos fueran reales (mismos controles de seguridad, mismo cifrado)

**Limitación:** Los datos sintéticos pueden no reflejar patrones reales de reidentificación. Los tests de seguridad pueden subestimar el riesgo de reidentificación en producción.

### 5.2 Cuasi-Identificadores

El sistema identifica explícitamente cuasi-identificadores que combinados podrían reidentificar a una persona:
- `edad + género + fecha_admision + hospital`
- `edad + género + fecha_admision + tipo_admision`
- `numero_habitacion + fecha_admision`

**Mitigación:**
- Cifrado de `nombre` (identificador directo) con AES-256-GCM
- Control de acceso RBAC estricto
- Logs de auditoría encadenados
- Aislamiento de red Docker

**Referencia:** `docs/inventario_datos.md` - sección "Cuasi-Identificadores Críticos"

---

## 6. Transparencia Sobre el Uso de IA Generativa en el Desarrollo

### 6.1 Qué Se Generó con IA

En el desarrollo de CriptoMed para la Entrega 2, se utilizó IA generativa (Claude/Devin) para:

**Generación de código:**
- Implementación de cifrado AES-256-GCM (`backend/app/crypto.py`)
- Implementación de cadena de hashes SHA-256 en audit_logs (`backend/app/audit.py`)
- Implementación de rotación de llaves (`scripts/rotate_keys.py`)
- Configuración de Docker Compose y Dockerfiles
- Esqueletos de endpoints de FastAPI

**Generación de documentación:**
- `docs/inventario_datos.md` - Inventario de datos
- `docs/DPIA.md` - Evaluación de Impacto en la Protección de Datos
- `docs/flujo_datos.mmd` - Diagrama de flujo de datos
- `docs/etica_privacidad.md` - Este documento
- `docs/hallazgos.md` - Análisis de hallazgos de seguridad
- `docs/comparativa_antes_despues.md` - Comparativa de escaneos de seguridad

**Generación de scripts:**
- `scripts/security_scan.sh` - Script de escaneo multi-herramienta
- `scripts/verificar_despliegue.sh` - Script de verificación de despliegue Docker

### 6.2 Cómo Se Revisó

**Revisión humana:**
- Todo el código generado fue revisado línea por línea antes de commits
- Se verificó que no se generaran secretos hardcodeados
- Se verificó que las referencias a estándares fueran correctas
- Se ejecutaron pruebas unitarias (`pytest`) después de cambios
- Se ejecutaron escaneos de seguridad (Bandit, Trivy, ZAP) antes y después de cambios

**Verificación técnica:**
- 65 pruebas unitarias y de integración ejecutadas exitosamente
- Escaneos de seguridad antes/después mostraron reducción del 61.18% en hallazgos
- Funcionalidad verificada manualmente (login, lectura por rol, transferencia, exportación)

**Marcadores [VERIFICAR]:**
- Referencias legales (Reglamento D.S. 016-2024-JUS, norma técnica MINSA) marcadas para verificación manual en fuentes oficiales
- Probabilidades e impactos en matriz de riesgos marcados para ajuste según criterio humano

**Aceptación de riesgo:** El uso de IA no se oculta. Este documento declara explícitamente qué se generó con IA y cómo se revisó.

---

## 7. Consideraciones Éticas que NO Aplican

### 7.1 Decisiones Automatizadas con Impacto Significativo

**No aplica:** CriptoMed no implementa decisiones automatizadas sobre pacientes (ej: diagnóstico por IA, triaje automatizado, predicción de riesgo).

**Justificación:** El sistema es un repositorio de historias clínicas, no un sistema de soporte a decisiones clínicas. El diagnóstico lo pone el doctor humano, no el sistema.

**Referencia:** GDPR Art. 22 (decisiones automatizadas) - no aplicable.

### 7.2 Perfilado con IA

**No aplica:** CriptoMed no implementa perfilado de pacientes con IA (análisis de patrones, segmentación, marketing).

**Justificación:** La finalidad del sistema es la gestión de historias clínicas individuales, no el análisis de datos a nivel poblacional.

**Referencia:** GDPR Art. 22 (perfilado) - no aplicable.

### 7.3 Reconocimiento Facial o Biométrico

**No aplica:** CriptoMed no recolecta ni procesa datos biométricos (huellas, reconocimiento facial, voz).

**Justificación:** No es necesario para la finalidad del sistema. La autenticación usa JWT con email/contraseña, no biometría.

**Referencia:** Ley 29733 Art. 3 (datos sensibles) - biometría es dato sensible, no se recolecta.

### 7.4 Geolocalización

**No aplica:** CriptoMed no recolecta ubicación GPS de pacientes ni personal.

**Justificación:** No es necesario para la finalidad del sistema. La ubicación se infiere del hospital donde se atiende, no del GPS del dispositivo.

### 7.5 Monitoreo de Empleados

**No aplica:** CriptoMed no implementa monitoreo de productividad, keystroke logging o captura de pantalla de empleados.

**Justificación:** Los logs de auditoría registran accesos a datos de pacientes, no actividad de empleados. Esto es una medida de seguridad, no monitoreo laboral.

---

## Conclusión

CriptoMed incorpora consideraciones éticas y de privacidad en su diseño:

**Puntos fuertes:**
- Autonomía del paciente (transferencia self-service, vista de accesos)
- Minimización de datos (solo campos necesarios)
- Transparencia sobre uso de IA generativa
- Mecanismo de break-glass auditado para emergencias
- Uso de datos sintéticos en desarrollo

**Puntos a mejorar:**
- Workflow digital de consentimiento explícito
- Política de retención y anonimización
- Canal formal de ejercicio de derechos del titular
- Dashboard para Oficial de Datos Personales

**Decisión ética general:** El sistema balancea adecuadamente seguridad con accesibilidad, privacidad con obligaciones legales, y autonomía del paciente con continuidad de la atención médica.

---

## Referencias

- **Ley 29733 (Perú):** Ley de Protección de Datos Personales
- **Reglamento D.S. 016-2024-JUS:** Reglamento de la Ley 29733 [VERIFICAR]
- **Norma técnica MINSA:** [VERIFICAR] plazo de conservación de historias clínicas
- **GDPR Art. 15:** Right of access by the data subject
- **GDPR Art. 17:** Right to erasure ('right to be forgotten')
- **GDPR Art. 20:** Right to data portability
- **GDPR Art. 22:** Automated individual decision-making, including profiling
- **NIST SP 800-92:** Guide to Computer Security Log Management
- **Principios de bioética:** Autonomía, beneficencia, no maleficencia, justicia
