# Presentación — CriptoMed

**Proyecto:** CriptoMed — prototipo de gestión segura de historiales médicos
**Curso:** DS3031 — Ética y Seguridad de Datos, Tipo 2
**Equipo:** María Fernanda Lazón y Christopher Pérez
**Fecha:** Noviembre de 2026
**Formato sugerido:** 12 diapositivas, 12–15 minutos de exposición y 10–12 minutos de demostración. Ajustar si el curso asigna otro tiempo.

> **Mensaje central:** CriptoMed demuestra controles de seguridad y privacidad en un prototipo local con datos sintéticos. La exposición destaca resultados, evidencia y una hoja de ruta responsable para la siguiente etapa.

---

## Diapositiva 1 — Portada y propósito

**Título:** CriptoMed: seguridad y privacidad para historiales médicos

- **Problema:** clínicas pequeñas pueden carecer de acceso controlado, trazabilidad y protección adecuada de historiales.
- **Propuesta:** prototipo web para gestionar historiales sintéticos con controles técnicos y de privacidad.
- **Tipo de proyecto:** Tipo 2 — Ética y Seguridad de Datos.
- **Alcance:** demostración académica local con datos sintéticos.

**Notas del orador:**
> “Buenas tardes. Somos María Fernanda Lazón y Christopher Pérez. Presentamos CriptoMed, un prototipo académico para explorar cómo aplicar seguridad y privacidad a la gestión de historiales médicos. La demostración usa datos sintéticos. Mostraremos los controles, la evidencia y cómo la evaluación de riesgos guía la siguiente etapa.”

**Visual:** [captura de login](images/login.png).

---

## Diapositiva 2 — Problema, alcance y objetivos

- Un historial requiere confidencialidad, integridad, disponibilidad y acceso oportuno.
- La solución integra frontend, backend y base de datos; la demo contiene alrededor de 500 pacientes sintéticos y un catálogo CIE-10.
- **Funciones:** acceso por roles, consulta de historiales, consulta de accesos, exportación, transferencia de médico y acceso de emergencia.
- **Seguridad:** cifrado selectivo, TLS, hashing de contraseñas, controles de acceso, auditoría, análisis de riesgos y respuesta a incidentes.
- **Evolución:** Entrega 1 con despliegue web y Fernet; Entrega 2 incorpora Docker local, AES-256-GCM y controles adicionales.

**Notas del orador:**
> “El objetivo no es solo cifrar una base: las medidas deben permitir que cada usuario cumpla su función sin exponer más información de la necesaria. La demo consulta historiales en menos de 30 segundos. La comparación con unos 10 minutos es una referencia del caso de negocio para orientar una futura medición con usuarios.”

---

## Diapositiva 3 — Arquitectura y flujo de datos

- **Frontend:** React/Vite; **edge:** Nginx con TLS 1.3; **API:** FastAPI; **datos:** PostgreSQL 16.
- El navegador entra por el edge; el backend conecta con PostgreSQL en una red interna.
- Solo el edge publica el puerto 8443 al host; los puertos 8000 y 5432 no se publican.
- Backend y base de datos tienen controles de endurecimiento; como siguiente mejora se prioriza el mínimo privilegio también para `init` y edge.
- Los datos circulan entre roles, pantallas y servicios: se protege el transporte, se cifra un subconjunto de campos y se registran acciones instrumentadas.

**Notas del orador:**
> “El diagrama permite seguir el dato desde el navegador hasta PostgreSQL. TLS protege el tramo público y la red interna limita el acceso a la base. El backend corre sin root. En la hoja de ruta priorizamos extender el mínimo privilegio de `init` y edge para que todos los servicios tengan controles consistentes.”

**Visual sugerido:** diagrama de arquitectura del [README](../README.md).

---

## Diapositiva 4 — Funciones y acceso por roles

| Rol | Acceso principal |
|---|---|
| Admin | Administración y gestión del sistema |
| Doctor | Pacientes asignados; acceso de emergencia sujeto a justificación |
| Administrativo | Datos operativos; sin diagnóstico, medicación ni resultados |
| Auditor | Consulta de registros de auditoría |
| Paciente | Historial propio, accesos, exportación y transferencia de médico |

- Los permisos se verifican en el backend, no solo en la interfaz.
- El paciente puede ver accesos y transferir su historial con confirmación.
- El acceso *break-glass* habilita acceso temporal de emergencia y deja un evento de auditoría.
- La fecha y versión del consentimiento se registran; formalizar su captura y evidencia es una mejora de la siguiente iteración.

**Notas del orador:**
> “Mostramos un ejemplo de mínimo privilegio: el rol administrativo puede apoyar la operación, pero no ve los campos clínicos indicados. El paciente tiene funciones de transparencia y control. La siguiente iteración puede integrar estas funciones con un proceso completo para ejercer derechos y registrar consentimiento.”

**Visuales:** [dashboard administrativo](images/admin_clinica_dashboard.png), [dashboard doctor](images/doctor_dashboard.png) y [acceso de auditor](images/auditor_dashboard_denegado.png).

---

## Diapositiva 5 — Criptografía y autenticación

- **En reposo:** AES-256-GCM con nonce, etiqueta de autenticación y AAD asociado al paciente.
- **Cobertura actual:** cinco campos prioritarios cifrados: nombre, diagnóstico, medicación, resultado de prueba y monto facturado.
- Las llaves llevan versión; los scripts permiten verificar y rotar llaves.
- **Siguiente etapa:** clasificar los demás datos de salud y cuasi-identificadores para decidir controles adicionales.
- **En tránsito:** TLS 1.3 con certificado autofirmado para desarrollo local; contraseñas con bcrypt y control de acceso con JWT/RBAC.

**Notas del orador:**
> “Elegimos AES-256-GCM por el cifrado autenticado definido en NIST SP 800-38D. El AAD vincula el texto cifrado a su contexto y ayuda a detectar su copia entre registros. En esta versión protegemos cinco campos prioritarios y la hoja de ruta contempla revisar el resto según su clasificación. El certificado autofirmado corresponde a la demo local. Las contraseñas usan bcrypt factor 12; se aplican bloqueo tras cinco fallos y rate limiting. El JWT verifica el estado de la cuenta en cada request; como mejora de configuración, alinearemos sus tiempos de expiración.”

**Demostración:** mostrar el prefijo/versionado de un campo en PostgreSQL y el resultado del verificador, sin mostrar llaves ni contraseñas.

---

## Diapositiva 6 — Auditoría e integridad

- Los eventos instrumentados incluyen autenticación, transferencia, exportación y acceso de emergencia.
- Cada registro se enlaza con el hash anterior mediante SHA-256.
- `pg_advisory_xact_lock` serializa escrituras concurrentes; triggers y permisos limitan cambios desde el rol de aplicación.
- El verificador puede detectar una ruptura de la cadena.
- **Siguiente nivel:** añadir anclaje externo y ampliar la verificación de cobertura para fortalecer la evidencia frente a cambios privilegiados.

**Notas del orador:**
> “La cadena SHA-256, los triggers y los permisos restringidos del rol de aplicación permiten verificar integridad dentro del modelo de amenazas previsto. La siguiente mejora es un anclaje fuera de la base y pruebas de cobertura; así también se fortalece la evidencia ante cambios hechos por administradores privilegiados.”

**Demostración opcional:** ejecutar el verificador antes y después de alterar deliberadamente un registro en una base de demo con datos sintéticos; explicar que es una prueba controlada.

**Visual:** [registros de auditoría](images/auditor_logs.png).

---

## Diapositiva 7 — Análisis de seguridad: herramientas y estado

- Se documentó una evaluación con Bandit, pip-audit, npm audit, Gitleaks, Hadolint, Trivy, testssl.sh y OWASP ZAP.
- El reporte histórico indica 3,596 hallazgos antes y 1,396 después: reducción reportada de 61.18%.
- Los reportes registran hallazgos por herramienta; su clasificación y seguimiento están documentados para priorizar la siguiente revisión.
- Los resultados de herramientas no son necesariamente hallazgos únicos ni todos tienen la misma severidad; no equivalen a “cero vulnerabilidades”.
- La prueba focalizada de generación de secretos pasó; la demo evidencia los flujos funcionales principales.
- En la última reconstrucción de Docker Compose (16 de noviembre), pasaron los 8 checks de despliegue: HTTPS/TLS 1.3, servicios healthy, login y puertos internos.

**Notas del orador:**
> “Aplicamos herramientas de análisis y documentamos el antes/después. La reducción del 61.18% es una comparación histórica de resultados reportados, no una medida directa de riesgo ni una certificación. En la última reconstrucción del stack, los ocho checks de despliegue pasaron: TLS 1.3, salud de servicios, puertos y login. Los hallazgos por herramienta siguen en seguimiento.”

**Evidencia:** [hallazgos](hallazgos.md) y [comparativa antes/después](comparativa_antes_despues.md).

---

## Diapositiva 8 — Privacidad, uso responsable y ética

- **Finalidades documentadas:** gestión clínica, operación administrativa y seguridad/auditoría; la clínica debe validarlas antes de cualquier uso real.
- Se mantiene un inventario de datos y se debe justificar cada campo por necesidad y proporcionalidad.
- Se usan datos sintéticos; las exportaciones contienen datos descifrados y se deben proteger en el dispositivo del titular.
- El modelo registra fecha y versión de consentimiento; la siguiente fase formaliza la captura y la evidencia.
- La política de seguridad y concientización está documentada; la puesta en marcha incluye capacitación y simulacros.

**Notas del orador:**
> “La ética no se resuelve con el cifrado. También importan la finalidad, la minimización, la transparencia, los derechos, quién tiene acceso y cuánto tiempo se conserva cada dato. El inventario orienta la minimización; antes de un piloto, la clínica valida cada campo, su base jurídica y el flujo de consentimiento. La política de seguridad es la base para la capacitación y los simulacros del equipo.”

**Visual:** esquema simplificado del inventario y flujo de datos, sin datos personales ni secretos.

---

## Diapositiva 9 — DPIA/EIPD: método y aplicabilidad

**Seis pasos aplicados a CriptoMed:**
1. Describir datos, titulares, finalidades, flujos y conservación.
2. Evaluar necesidad y proporcionalidad; considerar alternativas con menos datos.
3. Identificar y puntuar riesgos.
4. Definir mitigaciones técnicas y organizativas.
5. Valorar el riesgo residual y decidir si requiere consulta previa.
6. Aprobar, registrar y mantener la evaluación; revisarla ante cambios relevantes.

- **LINDDUN** complementa la búsqueda de amenazas: vinculabilidad, identificabilidad, no repudio, detectabilidad, divulgación, falta de conocimiento e incumplimiento.
- **GDPR Art. 35:** DPIA cuando el tratamiento probablemente implique alto riesgo y GDPR sea aplicable; no por el solo hecho de tratar datos sensibles.
- **Ejemplos de alto riesgo:** perfilado sistemático con decisiones significativas, datos sensibles a gran escala, vigilancia sistemática de espacios públicos a gran escala y decisiones automatizadas con efectos jurídicos o similares.
- **GDPR Art. 36:** consulta previa si persiste alto riesgo y GDPR aplica. En Perú, la EIPD era una buena práctica antes de 2025; el Reglamento D.S. 016-2024-JUS la incorpora para tratamientos de alto riesgo y contempla su realización como atenuante cuando corresponda. Validar supuesto y alcance con normativa/guía vigente.
- CNIL PIA y herramientas de la AEPD son referencias prácticas; no reemplazan la valoración contextual ni la asesoría legal.

**Notas del orador:**
> “La DPIA concreta el enfoque de privacidad desde el diseño del Art. 25 del GDPR y la responsabilidad proactiva, cuando ese marco aplica. Es preventiva y viva, no una firma que convierte el sistema en conforme. LINDDUN ayuda a buscar amenazas de privacidad, pero no sustituye el análisis legal. Los supuestos del GDPR y de la norma peruana dependen del tratamiento concreto; no afirmamos que GDPR aplique automáticamente a una clínica peruana.”

**Referencia:** [DPIA/EIPD completa](DPIA.md), con riesgos, mitigaciones, decisión y plan de revisión.

---

## Diapositiva 10 — DPIA: riesgos, mitigación y decisión

| Riesgo | Inherente | Residual estimado | Estado |
|---|---:|---:|---|
| Fuga de base de datos (R-01) | 10/25 | 5/25 | Mitigado parcialmente |
| Acceso indebido interno (R-02) | 12/25 | 4/25 | Mitigado parcialmente |
| Reidentificación por cuasi-identificadores (R-03) | 9/25 | 6/25 | Mitigado parcialmente |
| Retención/eliminación incompleta (R-06) | 12/25 | **12/25** | **Alto; acción prioritaria para un piloto** |

- Las puntuaciones son estimaciones cualitativas P×I, no mediciones empíricas.
- **Siguiente hito para R-06:** aprobar el calendario de retención para datos, respaldos y logs, y probar la purga correspondiente.
- **Decisión de la DPIA:** la demo continúa con datos sintéticos; un piloto real se plantea tras completar la retención, asignar responsables y reevaluar el riesgo.
- Revisar DPIA ante cambios de datos, fines, tecnología, incidentes o normativa; como mínimo anual.

**Notas del orador:**
> “La DPIA convierte la retención —12 sobre 25 residual— en una puerta de decisión clara. El trabajo siguiente es acordar plazos por categoría, cubrir respaldos y logs, implementar eliminación o anonimización cuando corresponda y repetir la evaluación. Si después de mitigar el riesgo sigue alto, se consulta a la autoridad cuando el marco aplicable lo requiere. Esta priorización muestra cómo usamos la DPIA para ordenar el desarrollo.”

---

## Diapositiva 11 — Incidentes, continuidad y trabajo futuro

- **Plan documentado:** detección, contención, erradicación, recuperación, revisión posterior y notificaciones aplicables.
- El plan contempla la notificación a la ANPD en el plazo de 48 horas citado en el Reglamento; la organización debe designar responsables y confirmar su aplicación al caso.
- **Evidencia reciente:** se generó un backup cifrado y se restauró en una base aislada; la verificación confirmó conteos, integridad de auditoría y descifrado de muestra.
- **Resultado medido:** restauración local en 3 segundos en una prueba; no es un SLA ni una garantía de RTO. El backup sigue siendo manual y local, con rotación de los 7 archivos más recientes.
- **Siguiente etapa de continuidad:** programar copias, definir destino externo, evaluar WAL y repetir pruebas de recuperación para establecer objetivos RPO/RTO.
- Las credenciales de demo se generan para el entorno sintético local; la siguiente etapa de despliegue separa las credenciales de producción del frontend.
- **Prioridades:** retención y purga; validación y reescaneos reproducibles; custodia externa de llaves (KMS/HSM); MFA; anclaje de auditoría; consentimiento explícito; endurecimiento del edge y `init`.

**Notas del orador:**
> “El plan de incidentes documenta la respuesta y las notificaciones; su adopción operativa incluye responsables, contactos y simulacros. En esta revisión generamos un backup local cifrado y verificamos su restauración en una base aislada. Los 3 segundos son solo una medición de esta prueba; no constituyen una garantía. La hoja de ruta añade programación, destino externo y pruebas periódicas.”

**Referencias:** [plan de backups](BACKUPS.md), [plan de respuesta y concientización](SECURITY_AWARENESS.md), [recomendaciones del informe](FINAL_REPORT.md).

---

## Diapositiva 12 — Resultado, retrospectiva y demostración

**Qué evidencia el prototipo**
- Funciones web, roles y restricciones en backend.
- TLS en edge; AES-256-GCM en cinco campos; auditoría encadenada con verificación.
- Evaluación de seguridad aplicada, DPIA, análisis ético, plan de incidentes y recomendaciones.

**Siguiente etapa priorizada por la DPIA**
- Extender protección por clasificación de datos, fortalecer la evidencia de auditoría y formalizar consentimiento.
- Cerrar retención/purga y reevaluar R-06 antes de abrir un piloto con datos reales.
- Automatizar backups y repetir restauraciones en un destino externo; mantener escaneos y pruebas reproducibles.

**Cierre:** “La principal lección es diseñar y evaluar privacidad antes de construir, y comunicar con precisión qué controles están probados y cuáles siguen pendientes.”

**Demostración en vivo (10–12 minutos):**
1. Login y roles: mostrar una restricción de acceso en backend.
2. Consultar un campo cifrado en la base de datos.
3. Mostrar acceso del paciente o transferencia de médico.
4. Verificar la cadena de auditoría.
5. Si está ensayado, demostrar una alteración intencional en una base sintética separada y su detección.

**Notas del orador:**
> “En la retrospectiva, pasamos de elegir una librería de cifrado a justificar algoritmo y contexto; también aprendimos que la DPIA debe informar las decisiones desde el inicio. La demostración usa datos sintéticos y evidencia preparada. Cerramos mostrando cómo los resultados se convierten en una hoja de ruta priorizada.”

---

## Preparación de la exposición y lista de comprobación

### Antes de presentar

- Ensayar una exposición de 12–15 minutos y una demo de 10–12 minutos, o ajustar al tiempo asignado por el curso.
- Confirmar que la app responde, las cuentas demo se obtuvieron del `.env` local y no se pegaron credenciales en diapositivas ni repositorio.
- Usar datos sintéticos. No ejecutar reset ni manipular logs sobre una base persistente que no sea de demo.
- Probar cada paso de la demo con anticipación. Tener las capturas en `docs/images/` como respaldo e indicar cuándo son capturas previas.
- Presentar con claridad qué evidencias son de la demo y cuáles provienen de reportes históricos; explicar el siguiente hito de validación como parte de la hoja de ruta.
- Abrir el [guion detallado de demo](GUION_DEMO.md), el [informe final](FINAL_REPORT.md) y la [DPIA](DPIA.md) para preguntas.

### Cobertura de la rúbrica Tipo 2

| Criterio | Evidencia para exponer |
|---|---|
| Funcionalidad y problema real | Diapositivas 2–4 y demo |
| Protección en reposo/transporte, hashing, acceso y auditoría | Diapositivas 3, 5 y 6 |
| Uso seguro, políticas y concientización | Diapositiva 8; distinguir política documentada de capacitación realizada |
| Herramientas de análisis | Diapositiva 7; cifras históricas y pendientes |
| Riesgos, incidentes y recomendaciones | Diapositivas 10–11 |
| Privacidad y DPIA | Diapositivas 8–10 |
| Presentación, informe, lecciones y retrospectiva | Diapositiva 12 e [informe](FINAL_REPORT.md) |
| Demostración en vivo | Diapositiva 12 y [guion de demo](GUION_DEMO.md) |

### Preguntas probables

| Pregunta | Respuesta precisa |
|---|---|
| ¿Por qué AES-256-GCM y no Fernet? | GCM está especificado en NIST SP 800-38D y ofrece cifrado autenticado. En el modelo actual solo cinco campos usan este cifrado. |
| ¿Qué cobertura tiene el cifrado? | En esta versión están cifrados cinco campos de paciente; la hoja de ruta extiende controles según la clasificación y necesidad de cada dato. |
| ¿Dónde están las llaves? | Se configuran mediante variables de entorno para la demo local. La siguiente etapa productiva es integrarlas con KMS/HSM y probar segregación y recuperación. |
| ¿Qué pasa si se pierde una llave? | No se pueden descifrar los datos asociados a esa versión. La recuperación de llaves debe probarse y custodiarse separada de los dumps. |
| ¿Cómo se protege la integridad de auditoría? | La cadena, los triggers y permisos de `app_user` permiten verificar y limitar cambios desde la app; el siguiente nivel es anclaje externo frente a cambios privilegiados. |
| ¿Qué riesgo prioriza la DPIA? | R-06, retención/eliminación: 12/25 residual. Por eso la siguiente etapa define plazos y purga antes de valorar un piloto real. |
| ¿La DPIA siempre es obligatoria? | Depende del riesgo, tratamiento y marco aplicable. GDPR Art. 35 aplica a tratamientos probablemente de alto riesgo cuando GDPR alcance el caso; validar el supuesto localmente. |
| ¿Por qué difieren los tiempos de sesión? | El frontend tiene 15 minutos de inactividad; `.env.example` configura JWT a 30 minutos y el fallback del backend es 15. Hay que alinear y probar la configuración. |
| ¿Cómo registra el consentimiento? | El modelo conserva fecha y versión; una siguiente iteración integra captura explícita y evidencia verificable. |
| ¿Qué ofrece la continuidad hoy? | Se generó un backup cifrado y se restauró en una base aislada; conteos, cadena de auditoría y descifrado de muestra pasaron. La restauración tomó 3 segundos en esta prueba, no es un SLA. Sigue siendo manual y local; faltan programación, copia externa y RPO/RTO garantizados. |
| ¿Qué significa el resultado del escaneo? | El análisis comparativo documenta una mejora; los hallazgos por herramienta se clasifican y se vuelven a revisar antes de una publicación. |
| ¿Qué pruebas se ejecutaron? | Pasó la prueba focalizada de generación de secretos. En la exposición mostramos los flujos funcionales; la validación integrada completa es un siguiente hito. |
| ¿Por qué las credenciales se ven en el login? | Facilitan la demo local con datos sintéticos. Se generan para ese entorno; el despliegue productivo separa autenticación y credenciales del frontend. |
| ¿Cuál es el alcance de uso actual? | Demostración académica con datos sintéticos. La DPIA define las acciones de privacidad y operación que habilitarían una evaluación para piloto real. |
| ¿Cómo se usan IA generativa? | El informe declara los usos de IA y la revisión realizada; el equipo debe explicar qué herramientas usó y asumir la autoría y validación del resultado. |
