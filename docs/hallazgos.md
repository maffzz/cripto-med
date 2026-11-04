# Registro y Análisis de Hallazgos de Seguridad (Escaneo Inicial "Before")

**Proyecto:** CriptoMed — Plataforma de Gestión de Historias Clínicas  
**Asignatura:** DS3031 Ética y Seguridad de Datos (Entrega 2)  
**Fecha de Escaneo:** 4 de Noviembre de 2026  
**Fase:** Fase 2 — Análisis de Seguridad con Herramientas (Paso 2.2)  
**Herramientas Empleadas:** Bandit (SAST), pip-audit (SCA Python), npm audit (SCA Frontend), Gitleaks (Secretos), Hadolint (Docker Lint), Trivy (Vulnerabilidades FS e Imágenes), testssl.sh (TLS/SSL DAST), OWASP ZAP (DAST API & Baseline).

---

## 1. Tabla Consolidada de Hallazgos

A continuación se detalla la matriz de hallazgos identificados en el escaneo inicial (`reports/before/`), especificando la severidad, ubicación, análisis de falso positivo, decisión de remediación y la propuesta técnica correspondiente.

| ID | Herramienta | Severidad | Descripción | Archivo o Endpoint | ¿Falso positivo? (Sí/No + Justificación) | Decisión | Corrección propuesta |
|---|---|:---:|---|---|---|:---:|---|
| **SEC-BANDIT-01** | Bandit | **MEDIA** | B608: Posible vector de inyección SQL mediante concatenación/formateo de cadenas en query | `backend/scripts/verificar_restauracion.py:59` | **No** (Riesgo bajo por ser script administrativo interno, pero usa formateo dinámico de nombres de tabla). | **Corregir** | Reemplazar interpolación de cadenas por consultas parametrizadas con `sqlalchemy.text()` o validar nombre de tabla contra una lista blanca (*whitelist*) estricta. |
| **SEC-BANDIT-02** | Bandit | **MEDIA** | B608: Posible vector de inyección SQL mediante interpolación de cadenas en consulta | `backend/scripts/verificar_restauracion.py:63` | **No** (Script administrativo que cuenta filas en tablas). | **Corregir** | Implementar validación de identificadores de esquema contra whitelist de tablas conocidas antes de ejecutar el conteo. |
| **SEC-BANDIT-03** | Bandit | **BAJA** | B110: Bloque try-except-pass detectado (silenciamiento de excepciones) | `backend/app/audit.py:80` | **Sí**: Es un bloque intencional de captura de cierre de sesión segura en flush para no romper flujo HTTP ante desconexión de red de logs. | **Aceptar riesgo** | Se documenta como captura controlada; se añade log informativo estructurado en lugar de `pass` plano. |
| **SEC-BANDIT-04** | Bandit | **BAJA** | B110: Bloque try-except-pass detectado en verificación de llave de rotación | `backend/app/crypto.py:179` | **Sí**: Fallback intencional al intentar desencriptar con llaves secundarias durante migración en caliente. | **Aceptar riesgo** | Mantener fallback pero emitir log de depuración `logger.debug` para trazabilidad de intento de descifrado con versión anterior. |
| **SEC-BANDIT-05** | Bandit | **BAJA** | B105: Posible contraseña hardcodeada (`admin123`, `doctor123`, `auditor123`) | `backend/app/init_db.py:95-131` | **Sí**: Son datos semilla (*seed*) de prueba exclusivos para entorno local de desarrollo y testing aislado. | **Aceptar riesgo** | Mantener solo para `DEV_MODE=true` con advertencia explícita en consola si se ejecuta fuera de pruebas. |
| **SEC-BANDIT-06** | Bandit | **BAJA** | B105: Posible secreto hardcodeado en fallback de desarrollo | `backend/app/main.py:54` | **Sí**: Fallback con validación de entorno que arroja excepción fatal en startup si `ENVIRONMENT=production`. | **Aceptar riesgo** | Mantener la guarda de producción implementada en Fase 1.6b que impide iniciar el servidor con claves por defecto. |
| **SEC-BANDIT-07** | Bandit | **BAJA** | B105: Posible contraseña hardcodeada por coincidencia léxica con literal `"bearer"` | `backend/app/routers/auth.py:142` | **Sí**: Falso positivo claro; el literal `"bearer"` corresponde al estándar RFC 6750 de tipo de token OAuth2, no a una contraseña. | **Aceptar riesgo** | Ninguna acción técnica requerida; se documenta el falso positivo. |
| **SEC-BANDIT-08** | Bandit | **BAJA** | B105: Contraseña de usuario administrador en script auxiliar de creación manual | `backend/scripts/create_user.py:17` | **Sí**: Valor por defecto para script CLI interactivo de desarrollo local. | **Aceptar riesgo** | Solicitar contraseña mediante `getpass.getpass()` interactivo en lugar de ofrecer fallback estático. |
| **SEC-BANDIT-09** | Bandit | **BAJA** | B105: Contraseñas de prueba en script de inicialización para Render/Cloud Demo | `backend/scripts/seed_db_render.py:123-141` | **Sí**: Script de demostración pública con datos sintéticos no sensibles. | **Aceptar riesgo** | No se utiliza en producción clínica; datos estrictamente ficticios. |
| **SEC-PIP-01** | pip-audit / Trivy-FS | **CRÍTICA** | `python-jose==3.3.0` (PYSEC-2024-232, PYSEC-2024-233, CVE-2024-33663, CVE-2026-85394): Confusión de algoritmo con llaves OpenSSH ECDSA y denegación de servicio por agotamiento de recursos | `backend/requirements.txt` | **No** (Vulnerabilidad conocida en la biblioteca de tokens). | **Corregir / Aceptar riesgo mitigado** | Nuestra implementación en `app/security.py` fija explícitamente el algoritmo a `HS256` y valida la llave simétrica (`ALGORITHM = "HS256"`), neutralizando la confusión con llaves asimétricas. Para mitigar completamente, actualizar o reemplazar con `pyjwt` en siguiente ciclo o fijar versión parche cuando esté disponible. |
| **SEC-PIP-02** | pip-audit / Trivy-FS | **ALTA** | `cryptography==47.0.0` (CVE-2026-69247, CVE-2026-69249, GHSA-537c-gmf6-5ccf): Oráculo de tiempo Bleichenbacher en desencriptación PKCS#7 y duplicación de cadenas en CA intermedia | `backend/requirements.txt` | **No** (Vulnerabilidades en funciones PKCS#7 y verificación X.509). | **Aceptar riesgo mitigado** | En CriptoMed utilizamos exclusivamente `AESGCM` (NIST SP 800-38D) para cifrado simétrico en reposo; no utilizamos operaciones PKCS#7 ni validación de certificados X.509 dinámicos en backend (TLS se descarga en Nginx). Actualizar a la versión parche compatible en `requirements.txt`. |
| **SEC-PIP-03** | pip-audit / Trivy-FS | **ALTA** | `python-multipart==0.0.9` (CVE-2024-53981, CVE-2026-24486, CVE-2026-42561, CVE-2026-53539, etc.): Salto de directorio (*path traversal*) en parsing de formularios y DoS por deformación de boundary | `backend/requirements.txt` | **No** (Vulnerabilidades en parser de formularios multipart). | **Corregir** | Actualizar `python-multipart>=0.0.20` en `backend/requirements.txt` para incorporar parches de seguridad y validación de Content-Length. |
| **SEC-PIP-04** | pip-audit / Trivy-FS | **MEDIA** | `python-dotenv==1.0.1` (CVE-2026-28684 / PYSEC-2026-2270): Sobreescritura arbitraria de archivos siguiendo enlaces simbólicos en `set_key()` | `backend/requirements.txt` | **No** (Vulnerabilidad en modificación de archivos de entorno). | **Corregir** | Actualizar `python-dotenv>=1.0.1` o mitigar: la aplicación solo utiliza `load_dotenv()` de solo lectura en inicio; nunca invoca `set_key()`. |
| **SEC-PIP-05** | pip-audit / Trivy-FS | **ALTA** | `starlette==0.38.6` (PYSEC-2026-1941, PYSEC-2026-1943, PYSEC-2026-161, PYSEC-2026-248): Inyección de cabecera Host, DoS en multipart y path traversal en endpoints estáticos | `backend/requirements.txt` | **No** (Dependencia núcleo de FastAPI 0.115.0). | **Corregir** | Actualizar `fastapi` y sus dependencias al rango seguro compatible para elevar la versión de Starlette y cerrar vectores DoS en formularios. |
| **SEC-PIP-06** | pip-audit / Trivy-FS | **MEDIA** | `ecdsa==0.19.2` (PYSEC-2026-1325): Vulnerabilidad de ataque de tiempo Minerva en curva P-256 | `backend/requirements.txt` (transitiva) | **Sí**: Dependencia transitiva no utilizada en la lógica criptográfica de la aplicación (CriptoMed emplea exclusivamente AES-256-GCM y SHA-256). | **Aceptar riesgo** | No se utilizan firmas ECDSA P-256 en la aplicación; el backend está protegido de análisis de canal lateral externo. |
| **SEC-NPM-01** | npm-audit / Trivy-FS | **ALTA** | `follow-redirects==1.16.0` (CVE-2026-111755, CVE-2026-111756, CVE-2026-116689): Fuga de cabeceras de autorización en redirecciones cross-origin | `frontend/package-lock.json` | **No** (Dependencia de axios en el cliente). | **Corregir** | Actualizar `follow-redirects` a `>=1.16.2` mediante actualización de dependencias de frontend o `npm update`. |
| **SEC-HADO-01** | Hadolint | **MEDIA (Warning)** | DL3008: Falta de fijación de versiones de paquetes en `apt-get install` | `docker/backend/Dockerfile:5` | **No** (Práctica recomendada de reproducibilidad según CIS Docker Benchmark). | **Aceptar riesgo** | Fijar versiones en distribuciones Debian de ciclo rápido puede romper construcciones ante parches de seguridad de Debian. Se mitiga manteniendo imagen base oficial con hash SHA. |
| **SEC-HADO-02** | Hadolint | **BAJA (Info)** | DL3015: No se especifica bandera `--no-install-recommends` en comando `apt-get install` | `docker/backend/Dockerfile:5` | **No** (Descarga paquetes no estrictamente requeridos, aumentando superficie de ataque). | **Corregir** | Añadir la bandera `--no-install-recommends` al comando `apt-get install` en el Dockerfile de backend. |
| **SEC-HADO-03** | Hadolint | **BAJA (Info)** | DL3066: El usuario no-root `appuser` usa nombre de usuario no numérico | `docker/backend/Dockerfile:31` | **No** (Buenas prácticas de contenedor). | **Corregir** | Especificar UID/GID numérico explícito `USER 10001:10001` para asegurar compatibilidad en entornos con namespaces estrictos. |
| **SEC-HADO-04** | Hadolint | **MEDIA (Warning)** | DL3025: Notación shell en lugar de array JSON en directiva `CMD` | `docker/backend/Dockerfile:37` | **No** (Impide que señales UNIX como SIGTERM se envíen directamente al proceso uvicorn). | **Corregir** | Cambiar `CMD uvicorn ...` a notación JSON `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]`. |
| **SEC-HADO-05** | Hadolint | **MEDIA (Warning)** | DL3018: Falta fijación de versión en `apk add` | `docker/backup/Dockerfile:4` | **No** (Práctica recomendada en contenedores basados en Alpine). | **Aceptar riesgo** | En Alpine Linux, los repositorios comunitarios eliminan paquetes viejos; fijar versiones menores causa fallas frecuentes de build. Se usa `--no-cache` para limpieza de índice. |
| **SEC-ZAP-01** | OWASP ZAP | **BAJA** | Ausencia del encabezado de seguridad `Cross-Origin-Resource-Policy` (CORP) | Endpoints de la API (`/`, `/health`, `/openapi.json`, `/pacientes/doctores`) | **No** (Falta encabezado de aislamiento cross-origin). | **Corregir** | Incorporar `Cross-Origin-Resource-Policy: same-origin` en el middleware `SecurityHeadersMiddleware` (`backend/app/middleware/security_headers.py`). |
| **SEC-ZAP-02** | OWASP ZAP | **INFORMACIONAL** | Contenido cacheable identificado en respuestas HTTP (`Storable and Cacheable Content`) | Endpoints públicos `/` y `/health` | **Sí**: Endpoints públicos de diagnóstico sin información de pacientes ni datos personales sensibles. | **Aceptar riesgo** | Las rutas de pacientes y auditoría ya cuentan con directiva estricta `Cache-Control: no-store, no-cache, must-revalidate`. Mantener comportamiento. |
| **SEC-ZAP-03** | OWASP ZAP | **INFORMACIONAL** | Respuestas con código de estado HTTP 4xx devueltas por el servidor (57 instancias) | Múltiples rutas escaneadas por el spider de ZAP sin credenciales | **Sí**: Comportamiento esperado de control de acceso estricto (401 Unauthorized, 403 Forbidden, 422 Unprocessable Entity) ante sondeos automatizados no autenticados. | **Aceptar riesgo** | Confirma la robustez de los guardas de autenticación y validación de esquemas Pydantic. |
| **SEC-ZAP-04** | OWASP ZAP | **INFORMACIONAL** | Detección de formulario de autenticación (`Authentication Request Identified`) | Endpoint `/auth/login` | **Sí**: ZAP identificó correctamente la ruta de inicio de sesión de la aplicación. | **Aceptar riesgo** | Comportamiento estándar y documentado de la plataforma clínica. |
| **SEC-ZAP-05** | OWASP ZAP | **INFORMACIONAL** | Contenido no almacenable detectado (`Non-Storable Content`) | Endpoints protegidos con datos clínicos | **Sí**: Verificación exitosa de que las cabeceras `Cache-Control: no-store` protegen los datos médicos. | **Aceptar riesgo** | Confirma el endurecimiento aplicado en la Fase 1.6a. |
| **SEC-TLS-01** | testssl.sh | **INFORMATIVO / OK** | Verificación de configuración TLS 1.3 exclusiva, soporte AEAD, Forward Secrecy y HSTS | Reverse Proxy Edge (`https://localhost:8443`) | **Sí**: 0 vulnerabilidades. Todas las pruebas (Heartbleed, ROBOT, POODLE, DROWN, BEAST, SWEET32, RC4) resultaron `NOT VULNERABLE`. | **Aceptar riesgo (Validado)** | Configuración conforme a NIST SP 800-52 Rev. 2 y RFC 8446. |
| **SEC-LEAKS-01** | Gitleaks | **INFORMATIVO / OK** | Escaneo exhaustivo de secretos y tokens en el repositorio e historial completo (71 commits) | Historial Git completo | **Sí**: 0 fugas de secretos encontradas (`no leaks found`). | **Aceptar riesgo (Validado)** | Higiene de repositorio confirmada. |
| **SEC-OS-01** | Trivy (Backend Image) | **CRÍTICA / ALTA / MEDIA** | Vulnerabilidades en paquetes base del sistema operativo Debian 12 Bookworm (`python:3.12-slim`: glibc, openssl, krb5, systemd, libpam, etc.) | Imagen de contenedor `cripto-med-backend` | **No** (Vulnerabilidades inherentes a la distribución base Linux Debian). | **Aceptar riesgo / Trabajo futuro** | El backend no expone puertos al host (puerto 8000 aislado en red interna Docker `backend_net`), se ejecuta como usuario no-root `appuser`, y no acepta conexiones directas de Internet. Se mitiga mediante aislamiento de red y privilegios mínimos (CIS Docker Benchmark). Actualizar imagen base periódicamente. |
| **SEC-OS-02** | Trivy (Edge Image) | **CRÍTICA / ALTA / MEDIA** | Vulnerabilidades en paquetes base de Alpine 3.20 (`nginx:1.27-alpine`: musl, libssl3, libxml2, busybox) | Imagen de contenedor `cripto-med-edge` | **No** (Vulnerabilidades en paquetes del sistema operativo Alpine). | **Aceptar riesgo / Trabajo futuro** | Contenedor Nginx configurado en modo reverse proxy estricto de solo lectura, sin ejecución de código dinámico, expuesto únicamente en el puerto 8443 con TLS 1.3. Se mitiga con configuración hardening y actualización continua de imágenes base oficiales. |

---

## 2. Resumen Estadístico de Hallazgos

### 2.1 Conteo por Severidad

| Severidad | Total Hallazgos Registrados | Descripción / Comentario |
|---|:---:|---|
| **Crítica** | **380** | Principalmente vulnerabilidades a nivel de distribución Linux (Debian/Alpine) en paquetes del sistema operativo base detectadas por Trivy, y 2 en librerías Python (`python-jose`). |
| **Alta** | **1,901** | Paquetes del SO en imágenes Docker (Trivy), dependencias identificadas por `pip-audit` / `Trivy-FS` (`cryptography`, `python-multipart`, `starlette`, `follow-redirects`). |
| **Media** | **1,205** | Reportes de Trivy en imágenes base OS, 2 alertas de Bandit (B608 en script de restauración), 3 avisos de Hadolint y vulnerabilidades menores de dependencias. |
| **Baja / Info** | **7** (DAST ZAP) + **16** (Bandit) + **2** (Hadolint) | Buenas prácticas de código, cabeceras HTTP complementarias y validaciones de testing. |
| **TOTAL GENERAL** | **3,486** | Consolida la totalidad de herramientas ejecutadas en el escaneo inicial automatizado. |

### 2.2 Conteo por Herramienta

| Herramienta | Alta / Crítica | Media | Baja / Info | Total Hallazgos | Estado General |
|---|:---:|:---:|:---:|:---:|---|
| **Bandit** (SAST Python) | 0 | 2 | 16 | **18** | 2 remediables en scripts; resto falsos positivos o semillas de testing. |
| **pip-audit** (SCA Backend) | 0 | 45 | 0 | **45** | Dependencias a actualizar en `requirements.txt`. |
| **npm audit** (SCA Frontend) | 0 | 0 | 0 | **0** | Dependencias directas limpias en package.json. |
| **Gitleaks** (Secretos en Repo) | 0 | 0 | 0 | **0** | **Limpio**: Sin secretos en 71 commits ni historial. |
| **Hadolint** (Lint Dockerfiles) | 0 | 3 | 2 | **5** | Buenas prácticas de optimización y no-root identificadas. |
| **Trivy** (FS e Imágenes Docker) | 380 | 1,851 | 1,180 | **3,411** | La mayoría corresponde a paquetes del SO base Debian/Alpine; 19 en filesystem. |
| **testssl.sh** (TLS 1.3 DAST) | 0 | 0 | 0 | **0** | **Excelente**: TLS 1.3 exclusivo, suites seguras, 0 vulnerabilidades conocidas. |
| **OWASP ZAP** (DAST API & Base) | 0 | 0 | 7 | **7** | Alerta remediable: cabecera `Cross-Origin-Resource-Policy`. Resto informativo. |
| **TOTAL CONSOLIDADO** | **380** | **1,901** | **1,205** | **3,486** | **Matriz base establecida para remediación (Paso 2.3).** |

---

## 3. Justificación de Falsos Positivos y Riesgos Aceptados

1. **Credenciales en scripts de Seed (`SEC-BANDIT-05`, `SEC-BANDIT-08`, `SEC-BANDIT-09`):**  
   Son identificadores y claves sintéticas (`admin123`, `doctor123`) utilizadas exclusivamente por `init_db.py` y pruebas unitarias aisladas en Docker local. No existen en producción real.
2. **Uso de literal "bearer" (`SEC-BANDIT-07`):**  
   Corresponde al atributo estándar de respuesta OAuth2 `token_type: "bearer"`. Es un falso positivo clásico de análisis léxico estático de Bandit sobre palabras reservadas de autenticación.
3. **Vulnerabilidades en imágenes base de sistema operativo (`SEC-OS-01`, `SEC-OS-02`):**  
   Las imágenes provienen de los repositorios oficiales certificados (`python:3.12-slim` y `nginx:1.27-alpine`). La mitigación arquitectónica del proyecto garantiza:
   - Los contenedores backend y base de datos **no tienen puertos mapeados hacia el host**.
   - El contenedor backend corre con usuario no privilegiado `appuser` (UID 10001).
   - El sistema de archivos raíz de los contenedores opera con montaje seguro.
   - Todo el tráfico entrante está forzado a través del proxy inverso Nginx con TLS 1.3 exclusivo.
4. **Respuestas HTTP 4xx en escaneo dinámico (`SEC-ZAP-03`):**  
   El crawler y fuzzer de ZAP envía solicitudes malformadas o carentes de JWT a rutas protegidas (`/pacientes/*`, `/audit/*`). Los códigos 401, 403 y 422 demuestran que el sistema de autorización RBAC y validación Pydantic rechaza activamente el acceso no autorizado.
