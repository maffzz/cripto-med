# Evaluación de Impacto en la Protección de Datos (DPIA / EIPD) — CriptoMed

**Proyecto:** CriptoMed — plataforma de gestión de historias clínicas para clínicas pequeñas en Perú
**Versión:** 2.0 — noviembre de 2026
**Responsable de tratamiento previsto:** la clínica que decida operar la plataforma (por designar antes de producción)
**Encargado previsto:** proveedor/operador de CriptoMed, según el contrato y el modelo de alojamiento que se adopte
**Estado:** evaluación de diseño para un prototipo académico local; no es una aprobación para tratar datos reales
**Alcance normativo:** Ley peruana N.° 29733 y su Reglamento (D.S. N.° 016-2024-JUS); GDPR cuando su ámbito territorial resulte aplicable; ISO/IEC 29134 como guía metodológica

> **Decisión de uso:** el entorno evaluado usa datos sintéticos. Antes de incorporar pacientes reales, la clínica debe confirmar su rol, finalidad y base jurídica, definir retención, validar las obligaciones aplicables y aprobar los riesgos residuales. Esta evaluación no constituye asesoría jurídica ni acredita por sí sola el cumplimiento normativo.

## 1. Resumen ejecutivo y decisión

CriptoMed administra historias clínicas y datos de cuentas, facturación y auditoría. Los datos de salud son especialmente sensibles y una divulgación, alteración o indisponibilidad puede causar daño clínico, discriminación, fraude o pérdida de confianza. Por ese motivo se realiza esta evaluación antes de un eventual tratamiento real, aunque el prototipo actual solo use datos sintéticos.

La evaluación identifica 12 riesgos y aplica una matriz cualitativa de probabilidad e impacto de 1 a 5. Con los controles descritos, el riesgo residual más alto es **R-06: retención no definida (12/25, alto según la escala de este documento)**. No se considera aceptado para producción. Se requiere establecer y aprobar la retención, incluida la de respaldos y logs, y volver a puntuar el riesgo. Si, tras las medidas, permanece alto y GDPR es aplicable, no se debe iniciar el tratamiento sin consultar previamente a la autoridad de control conforme al artículo 36. La aplicabilidad de las obligaciones peruanas del Reglamento debe validarse para el tratamiento concreto.

La decisión para el estado actual es **apto solo para demostración con datos sintéticos**. **No aprobado para producción con datos reales** hasta cerrar las acciones de prioridad alta de la sección 7 y obtener aprobación del responsable de tratamiento.

## 2. Paso 1 — Describir el tratamiento

### 2.1 Alcance, titulares y datos

**Titulares previstos**
- Pacientes de la clínica.
- Doctores, personal administrativo, auditores y administradores con cuenta en el sistema.

**Categorías de datos tratadas**
- Identificación y cuenta: nombre, email, identificadores UUID, rol y estado de cuenta.
- Salud: diagnóstico, código CIE-10, medicación, resultados de pruebas, tipo de sangre, tipo de admisión y fechas de atención.
- Administrativos/financieros: proveedor de seguro y monto facturado.
- Cuasi-identificadores: edad, género, hospital, habitación y fechas de admisión/alta; combinados pueden facilitar la reidentificación.
- Seguridad y auditoría: hash de contraseña, intentos fallidos, IP de origen, timestamps, acciones, recurso y detalles de auditoría; justificación y periodo del acceso de emergencia.
- Evidencia de consentimiento: fecha y versión registradas. Estos campos no demuestran por sí solos que se haya obtenido un consentimiento válido.

El inventario detallado, finalidad por campo, acceso y cifrado está en [inventario_datos.md](./inventario_datos.md). En el modelo actual se cifran a nivel de aplicación el nombre, diagnóstico, monto facturado, medicación y resultado de pruebas con AES-256-GCM; otros campos de salud y cuasi-identificadores no están cifrados individualmente en la base de datos.

### 2.2 Finalidades y operaciones

1. Registrar y consultar historias clínicas para la atención.
2. Gestionar admisión, asignación de profesional, facturación y seguro.
3. Autenticar usuarios, aplicar permisos y detectar abuso de cuentas.
4. Registrar accesos y cambios para auditoría y respuesta a incidentes.
5. Permitir al paciente consultar accesos, exportar su información y solicitar transferencia a otro doctor.
6. Facilitar acceso excepcional de emergencia (break-glass), limitado en el tiempo y auditado.

No se identifican en el prototipo perfiles de pacientes, decisiones automatizadas con efectos legales, publicidad, geolocalización ni vigilancia de espacios públicos. No hay integración externa prevista en el despliegue Docker local descrito; cualquier hosting, analítica, correo, interoperabilidad o destinatario externo futuro exige actualizar esta evaluación y revisar transferencias internacionales.

### 2.3 Flujo, almacenamiento y acceso

El navegador se comunica por TLS con Nginx (edge); Nginx reenvía solicitudes al backend FastAPI; el backend cifra determinados campos y accede a PostgreSQL en una red interna Docker. Los respaldos se generan aparte y se cifran con GPG según la documentación del proyecto. El flujo detallado consta en [flujo_datos.mmd](./flujo_datos.mmd).

| Rol | Acceso previsto |
|---|---|
| Admin | Administración y acceso amplio al sistema |
| Doctor | Datos clínicos de pacientes asignados; acceso de emergencia excepcional con justificación |
| Administrativo | Datos básicos y administrativos; no debe ver diagnóstico, medicación ni resultados de pruebas |
| Auditor | Registros de auditoría; sin acceso funcional a historias clínicas |
| Paciente | Su propio historial, accesos, exportación y transferencia disponible en la aplicación |

El despliegue revisado es un prototipo local con Docker Compose. Las decisiones sobre alojamiento, ubicación de datos, subencargados, acceso de soporte y transferencias deberán documentarse para el entorno real. El despliegue previo en servicios externos no se considera dentro de esta evaluación.

### 2.4 Retención, eliminación y derechos

- **Base de datos:** el código no aplica una eliminación automática ni una política completa de retención; mientras exista el volumen, los registros pueden persistir. La aplicación dispone de borrado lógico, que no equivale a supresión física.
- **Backups:** la documentación describe rotación de respaldos cifrados, pero la expiración y purga de copias debe verificarse y alinearse con el calendario de retención aprobado.
- **Logs:** contienen identificadores de usuario/recurso, IP, hora y actividad; requieren plazo, acceso y purga definidos. La cadena de hashes protege la integridad, no la confidencialidad ni la eliminación.
- **Derechos:** existen funciones de consulta del historial, consulta de accesos y exportación. Rectificación, oposición, limitación y solicitudes de supresión requieren canal y procedimiento operativos. La conservación clínica puede limitar la supresión; debe resolverse caso por caso conforme a la norma aplicable y no asumirse una exención automática.
- **Plazo clínico:** el proyecto cita la norma técnica MINSA R.M. N.° 214-2018/MINSA y 20 años de conservación. La clínica debe confirmar que el plazo aplica a cada categoría y documento; no extenderlo automáticamente a cuentas, telemetría, respaldos o logs.

### 2.5 Base jurídica y contexto normativo

La clínica, como responsable previsto, debe documentar la base jurídica y las condiciones para tratar datos de salud antes de producción. Los campos `consentimiento_fecha` y `consentimiento_version` son evidencia técnica incompleta, no sustituyen el aviso, la prueba de consentimiento cuando corresponda ni la determinación de otra base legal.

- **GDPR:** si aplica por el ámbito territorial, el artículo 35 exige una DPIA antes de tratamientos probablemente de alto riesgo; entre los supuestos relevantes están la evaluación sistemática y exhaustiva con decisiones significativas, el tratamiento a gran escala de categorías especiales y la observación sistemática a gran escala de espacios públicos. El artículo 36 requiere consulta previa a la autoridad cuando el riesgo alto permanece pese a las medidas previstas.
- **Perú:** antes de la entrada en vigor del Reglamento en 2025, la DPIA/EIPD era una buena práctica; el Reglamento aprobado por D.S. N.° 016-2024-JUS la incorpora para tratamientos de alto riesgo y puede considerar su realización como atenuante. Evaluar la Ley N.° 29733 y validar el supuesto exacto, umbrales y consecuencias con asesoría competente y la normativa/guías vigentes de la ANPD.
- GDPR no se presenta como aplicable automáticamente a una clínica peruana. La aplicabilidad depende de las circunstancias del tratamiento.

## 3. Paso 2 — Necesidad y proporcionalidad

### 3.1 Evaluación

Los campos clínicos son necesarios para documentar y dar continuidad a la atención; la identidad enlaza el historial con su titular; los datos administrativos apoyan admisión y facturación; y los datos de acceso permiten proteger las cuentas e investigar incidentes. La necesidad de cada campo debe revisarse por la clínica según sus servicios reales, no solo por estar presente en el dataset.

El prototipo utiliza un dataset sintético y un catálogo CIE-10. No se deben importar datos reales de datasets de prueba. Se recomienda separar los entornos y prohibir la copia de producción a desarrollo.

### 3.2 Salvaguardas y proporcionalidad

- El control RBAC restringe vistas por rol; en particular, el rol administrativo no debe recibir diagnóstico, medicación ni resultados.
- Los doctores se limitan a pacientes asignados, con excepción break-glass que registra una justificación y tiene ventana temporal.
- Los campos seleccionados se cifran con AES-256-GCM y AAD. El cifrado en la capa de aplicación no protege frente a una aplicación/administrador autorizado comprometido, y no reemplaza el control de acceso.
- TLS protege el tránsito navegador-edge; segmentación de red limita la exposición de PostgreSQL.
- Las exportaciones son una salida de datos descifrados y deben protegerse en el dispositivo del titular y no permanecer en almacenamiento temporal.
- Las IP y los eventos de actividad ayudan a investigar abuso, pero también son datos personales: reducir detalle, accesos y plazo a lo necesario.

### 3.3 Alternativas menos intrusivas y brechas

- Recoger solo los campos requeridos para el servicio clínico contratado; eliminar campos no usados y reducir granularidad cuando sea posible.
- Usar identificadores seudónimos en vistas y reportes cuando el nombre no sea necesario; ello reduce exposición, pero no anonimiza por sí solo.
- Evaluar cifrado de disco/volumen y gestión de llaves fuera del host; actualmente las llaves se configuran mediante variables de entorno.
- Formalizar retención y eliminación de datos primarios, respaldos y logs; hoy es una brecha de diseño/operación.
- Habilitar un proceso para solicitudes de derechos, revisión de accesos anómalos y atención de incidentes.

**Resultado:** el tratamiento es proporcional solo para las finalidades clínicas/administrativas documentadas y bajo estas salvaguardas. La clínica debe confirmar cada campo y su base jurídica antes de incorporar datos reales.

## 4. Paso 3 — Identificar y valorar riesgos

### 4.1 Método de evaluación

Se valora el riesgo para las personas titulares, no únicamente el impacto operativo para la clínica. La probabilidad (P) y el impacto (I) se puntúan de 1 a 5; el nivel numérico es P × I. Impacto considera confidencialidad, integridad, disponibilidad, autonomía, discriminación y consecuencias clínicas. Los valores son estimaciones iniciales para el prototipo, no mediciones estadísticas.

**Bandas internas de decisión (no son umbrales legales):** 1–4 bajo; 5–9 moderado; 10–16 alto; 17–25 muy alto. El residual se calcula nuevamente como probabilidad × impacto después de controles. La asignación debe revisarse con evidencia operativa, incidentes, pruebas y contexto real de la clínica.

### 4.2 LINDDUN como apoyo de identificación

Se usa **LINDDUN** para ampliar el análisis de amenazas de privacidad; no sustituye la evaluación legal ni la matriz de riesgos:

| Amenaza LINDDUN | Aplicación a CriptoMed |
|---|---|
| **Linkability (vinculabilidad)** | Edad, género, fechas, hospital y habitación pueden combinarse para enlazar registros (R-03). |
| **Identifiability (identificabilidad)** | Nombre, email y datos clínicos pueden identificar directamente a la persona (R-01, R-03). |
| **Non-repudiation (no repudio)** | Los logs atribuyen acciones a cuentas y pueden revelar patrones de actividad del personal; proteger su uso y acceso (R-12). |
| **Detectability (detectabilidad)** | La presencia de una cuenta, evento o registro puede revelar que una persona recibió atención (R-01, R-10). |
| **Disclosure of information (divulgación)** | Acceso interno indebido, fuga, exportación o uso secundario exponen información clínica (R-01, R-02, R-07). |
| **Unawareness (falta de conocimiento)** | El paciente puede desconocer finalidades, acceso de emergencia, exportaciones o conservación si no hay avisos y canal claros (R-06 y acción de transparencia). |
| **Non-compliance (incumplimiento)** | Base jurídica, derechos, plazos o medidas no documentados pueden incumplir obligaciones (R-06 y acción de derechos). |

### 4.3 Matriz de riesgos y controles

| ID | Riesgo para las personas | P×I inherente | Controles existentes / brecha | P×I residual | Estado |
|---|---|---:|---|---:|---|
| R-01 | Fuga de la base de datos y exposición de salud/identidad | 2×5=10 | AES-256-GCM en campos seleccionados, TLS, red interna y contenedores endurecidos. No todos los campos están cifrados; compromiso del backend puede revelar datos. | 1×5=5 | Moderado |
| R-02 | Acceso indebido de personal o abuso de privilegios | 3×4=12 | RBAC, mínimo privilegio y logs encadenados; falta revisión formal y periódica de privilegios. | 1×4=4 | Bajo |
| R-03 | Reidentificación por combinación de cuasi-identificadores | 3×3=9 | Restricción por rol; el cifrado del nombre no elimina la reidentificación por fechas/edad/hospital. | 2×3=6 | Moderado |
| R-04 | Transferencia a doctor incorrecto | 2×4=8 | Confirmación explícita y evento de auditoría; validar identidad del doctor y recuperación ante error. | 1×4=4 | Bajo |
| R-05 | Historia clínica indisponible durante una emergencia | 2×5=10 | Backups, healthchecks y break-glass; continuidad y restauración deben probarse periódicamente. | 1×5=5 | Moderado |
| R-06 | Retención excesiva o eliminación incompleta en DB/backups/logs | 4×3=12 | Política de retención/purga y proceso de derechos no implementados de extremo a extremo. Cifrado no resuelve retención. | 4×3=12 | **Alto — no aceptado** |
| R-07 | Uso secundario, consulta masiva o exportación no autorizada | 2×5=10 | Accesos por rol y auditoría; faltan controles organizativos/contractuales verificados y monitoreo de exportaciones. | 1×5=5 | Moderado |
| R-08 | Error de código CIE-10 o dato clínico con efecto en la atención | 3×4=12 | Catálogo y validación de referencia; se requiere revisión clínica y proceso de corrección. | 2×4=8 | Moderado |
| R-09 | Pérdida o exposición de llaves y pérdida de acceso a historias | 1×5=5 | Llaves versionadas y rotación documentada; variables de entorno no equivalen a KMS/HSM. Validar restauración de llaves. | 1×5=5 | Moderado |
| R-10 | Fuerza bruta o toma de cuenta | 3×4=12 | Hash de contraseña, bloqueo y rate limit; MFA no implementado. | 2×4=8 | Moderado |
| R-11 | Intercepción de datos en tránsito | 2×5=10 | TLS 1.3 en el edge; certificado autofirmado del prototipo y segmento edge-backend requieren revisión para producción. | 1×5=5 | Moderado |
| R-12 | Alteración, exposición o uso desproporcionado de logs de actividad | 2×4=8 | Cadena SHA-256, restricciones de escritura y triggers; logs no están anclados externamente y su retención/acceso no están definidos. | 1×4=4 | Bajo |

Los controles están descritos en el código y documentos citados en [FINAL_REPORT.md](./FINAL_REPORT.md), [DOCKER.md](./DOCKER.md), [BACKUPS.md](./BACKUPS.md) y [RIESGOS_ACEPTADOS.md](./RIESGOS_ACEPTADOS.md). Un control técnico reduce probabilidad, pero no elimina impacto ni demuestra por sí solo cumplimiento.

## 5. Paso 4 — Mitigar y planificar el tratamiento del riesgo

| Prioridad | Acción requerida antes de producción | Responsable previsto | Evidencia para cierre |
|---|---|---|---|
| **P0** | Aprobar calendario por categoría de dato, incluidos historias clínicas, cuentas, logs, backups y purga; resolver solicitudes de supresión frente a deberes de conservación. | Clínica responsable + asesoría de privacidad | Política aprobada, configuración/procedimiento de purga y prueba de restauración/purga |
| **P0** | Definir responsable/encargado, base jurídica, información al titular, canal de derechos y procedimiento de incidentes. | Clínica responsable | Registro de tratamiento, avisos/contratos y procedimiento operativo |
| **P1** | Revisar accesos de mínimo privilegio, cuentas privilegiadas, exportación y logs; fijar responsables y periodicidad. | Clínica + operador | Matriz de acceso y registro de revisiones |
| **P1** | Validar seguridad para producción: TLS/certificados, llaves fuera de variables de entorno, MFA para roles privilegiados y pruebas de restauración. | Operador técnico | Configuración aprobada y resultados de pruebas |
| **P1** | Confirmar exactitud clínica y proceso de rectificación del CIE-10; entrenar al personal para break-glass y transferencias. | Responsable clínico | Procedimientos y evidencia de revisión/capacitación |
| **P2** | Revisar minimización, necesidad de cada campo y plazos de conservación al menos anualmente. | Clínica responsable | Inventario y DPIA actualizados |

## 6. Paso 5 — Determinar el riesgo residual y consulta previa

Con la información disponible, **R-06 permanece alto (12/25)** porque no existe calendario aprobado que cubra registros, logs y respaldos. El cifrado no reduce este riesgo de conservación excesiva ni de incumplimiento. El riesgo se **rechaza para producción** hasta completar la acción P0 y recalcular la matriz.

- **Si, después de las medidas, algún riesgo residual sigue alto y GDPR aplica:** consultar a la autoridad de control antes de iniciar el tratamiento, de acuerdo con GDPR Art. 36; conservar la evaluación y el expediente de consulta.
- **Si el riesgo residual baja a moderado o bajo:** documentar la evidencia, la decisión del responsable y las condiciones de aceptación; proceder únicamente tras completar las demás acciones previas.
- **En el ámbito peruano:** confirmar con el responsable/asesoría competente si el tratamiento de alto riesgo activa obligaciones específicas bajo el Reglamento de 2025 y qué documentación o consulta corresponde. No inferir que el tratamiento queda autorizado solo por preparar esta DPIA.
- **Para la demostración local actual:** usar datos sintéticos exclusivamente. No se requiere una consulta relativa a datos reales mientras no haya tratamiento real, sin perjuicio de otros requisitos aplicables al proyecto.

## 7. Paso 6 — Aprobar, registrar y mantener viva la DPIA

### 7.1 Registro y aprobación

Esta versión registra el alcance, flujo, necesidad, amenazas, puntuaciones, controles, brechas y decisión. Antes de producción deben completarse los campos siguientes; no se presume que la aprobación exista:

| Aprobación | Responsable | Estado |
|---|---|---|
| Responsable de tratamiento de la clínica | Por designar | Pendiente |
| Responsable de privacidad/Oficial de Datos Personales, si corresponde | Por designar | Pendiente |
| Responsable técnico del operador | Por designar | Pendiente |
| Revisión clínica de exactitud y continuidad | Por designar | Pendiente |
| Aceptación formal del riesgo residual y acciones | Responsable de tratamiento | No aprobada |

Mantener esta DPIA junto con el inventario de datos, el diagrama de flujo, las decisiones de seguridad, el registro de riesgos y la evidencia de pruebas. Registrar versión, fecha, cambios, aprobador y acciones abiertas. Las excepciones y riesgos aceptados deben incluir motivo, propietario y fecha de vencimiento.

### 7.2 Revisión y eventos de actualización

Revisar al menos anualmente y **antes** de cualquier cambio sustancial, incluyendo:
- nuevos datos, finalidades, perfiles, automatización, integraciones o categorías de titulares;
- nuevos proveedores, alojamiento, ubicación, transferencia internacional o acceso de soporte;
- cambios en roles, autenticación, cifrado, llaves, exportación, backups o retención;
- incidente, vulnerabilidad relevante, cambio normativo o evidencia de que una puntuación era incorrecta;
- inicio de tratamiento con datos reales o aumento sustancial de escala.

## Referencias y herramientas

- GDPR, artículos 25, 35 y 36: privacidad desde el diseño, evaluación y consulta previa.
- Ley peruana N.° 29733 y Reglamento aprobado por D.S. N.° 016-2024-JUS; validar texto consolidado y guías vigentes de la ANPD antes del despliegue.
- ISO/IEC 29134, guía para evaluaciones de impacto en privacidad.
- Inventario y evidencias del proyecto: [inventario_datos.md](./inventario_datos.md), [flujo_datos.mmd](./flujo_datos.mmd), [FINAL_REPORT.md](./FINAL_REPORT.md).
- Herramienta y metodología PIA de la CNIL: https://www.cnil.fr/en/privacy-impact-assessment-pia
- Guías de evaluación de impacto de la AEPD: https://www.aepd.es/ (sección de evaluación de impacto / gestión del riesgo).
