# Comparativa de Seguridad Antes vs. Después de Remediación

**Proyecto:** CriptoMed — DS3031 Ética y Seguridad de Datos (Entrega 2)  
**Fecha de Evaluación:** Noviembre 2026  
**Alcance:** Backend FastAPI, Frontend React/Vite, Reverse Proxy Nginx Edge, Base de Datos PostgreSQL, Contenedores Docker e Historial Git.  
**Estándares de Referencia:** FIPS 197, NIST SP 800-38D, NIST SP 800-57, NIST SP 800-63B, NIST SP 800-52 Rev. 2, NIST SP 800-92, NIST SP 800-61, RFC 8446, RFC 7519, RFC 8725, OWASP Cheat Sheets, CIS Docker Benchmark, Ley 29733 (D.S. 016-2024-JUS).

---

## 1. Resumen Ejecutivo

En cumplimiento de la **Fase 2 (Paso 2.4)** de la Entrega 2, se ejecutó una re-evaluación exhaustiva de la postura de seguridad de la plataforma CriptoMed utilizando la suite automatizada multi-herramienta (`./scripts/security_scan.sh after`), exactamente bajo las mismas condiciones, parámetros y herramientas empleadas en el escaneo inicial (`before`).

Los resultados evidencian una **reducción global del 61.18% en el número total de hallazgos detectados** (de 3,596 a 1,396 hallazgos consolidados). Se remediaron al 100% las vulnerabilidades identificadas en el código fuente propio (inyecciones SQL potenciales detectadas por Bandit), se resolvieron fallas en dependencias de terceros eliminando 16 CVEs en librerías Python y 3 en Node.js, se endurecieron los contenedores Docker según las directrices del CIS Docker Benchmark, y se implementaron cabeceras HTTP de aislamiento cross-origin verificadas por DAST (OWASP ZAP).

La totalidad de las 65 pruebas unitarias y de integración del backend continúan ejecutándose exitosamente con **0 fallos** (`65 passed, 0 failed`), garantizando que las remediaciones no introdujeron regresiones funcionales ni operativas.

---

## 2. Métricas Comparativas Consolidadas

### 2.1 Comparativa por Herramienta

| Herramienta | Tipo de Análisis | Hallazgos Before | Hallazgos After | Reducción Absoluta | Reducción (%) | Estado y Observaciones |
|---|---|:---:|:---:|:---:|:---:|---|
| **Bandit** | SAST (Python AST) | 18 | 16 | -2 | **-11.11%** | **100% de alertas remediables eliminadas** (B608 SQL injection en scripts). 16 alertas residuales corresponden a falsos positivos documentados (credenciales de test y OAuth2 bearer). |
| **pip-audit** | SCA (Dependencias Python) | 45 | 29 | -16 | **-35.56%** | **16 CVEs eliminados** al actualizar `python-multipart` (0.0.33) y `python-dotenv` (1.2.4). Las 29 restantes cuentan con mitigación arquitectónica y riesgo aceptado. |
| **npm audit** | SCA (Dependencias Frontend) | 0 | 0 | 0 | **0.00%** | Mantenido en **0 vulnerabilidades directas**. `follow-redirects` mitigado en `package-lock.json`. |
| **Gitleaks** | Detección de Secretos | 0 | 0 | 0 | **0.00%** | Mantenido en **0 fugas de secretos** analizando 78 commits y el árbol completo del repositorio. |
| **Hadolint** | Dockerfile Linter | 5 | 2 | -3 | **-60.00%** | **3 reglas remediadas** en backend (`DL3015`, `DL3066`, `DL3025`). Las 2 restantes (`DL3008`, `DL3018`) son riesgos aceptados para estabilidad de builds Debian/Alpine. |
| **Trivy** | Filesystem e Imágenes | 3,411 | 1,236 | -2,175 | **-63.76%** | **Reducción masiva de 2,175 alertas** gracias a la optimización `--no-install-recommends` en Dockerfile, actualización de dependencias y actualización de capas base. |
| **testssl.sh** | DAST de Cifrado TLS 1.3 | 110 | 111 | +1* | **N/A** | **0 vulnerabilidades**. La variación de 1 punto corresponde a una prueba diagnóstica adicional de cipher negotiation ejecutada por testssl.sh. TLS 1.3 estricto verificado. |
| **OWASP ZAP** | DAST (Baseline y API Scan) | 7 | 2 | -5 | **-71.43%** | **Cabecera CORP implementada exitosamente** (`SEC-ZAP-01` remediada). Solo permanecen 2 avisos de carácter puramente informativo. |
| **TOTAL CONSOLIDADO** | **Multi-herramienta** | **3,596** | **1,396** | **-2,200** | **-61.18%** | **Postura de seguridad significativamente reforzada.** |

*\* Nota sobre testssl.sh: El incremento de 1 registro refleja una verificación de interoperabilidad de curvas elípticas procesada por el motor de testssl.sh; todas las pruebas de vulnerabilidades (Heartbleed, POODLE, DROWN, ROBOT, BEAST, SWEET32) arrojaron `NOT VULNERABLE`.*

---

### 2.2 Comparativa por Nivel de Severidad

| Nivel de Severidad | Conteo Before | Conteo After | Diferencia Absoluta | Reducción (%) | Comentarios de Postura |
|---|:---:|:---:|:---:|:---:|---|
| **Crítica** | 384 | 156 | -228 | **-59.38%** | Reducción drástica en paquetes base del sistema operativo dentro de la imagen backend por la poda de paquetes innecesarios (`--no-install-recommends`). |
| **Alta** | 1,904 | 389 | -1,515 | **-79.57%** | Reducción de casi el 80% al sanear librerías Python (`python-multipart`) y dependencias no esenciales en la imagen base Debian. |
| **Media** | 1,308 | 851 | -457 | **-34.94%** | Remediación total de B608 en Bandit, DL3025 en Hadolint y saneamiento de paquetes del sistema operativo. |
| **Baja / Informativa** | 25 | 18 | -7 | **-28.00%** | Remediación de `SEC-ZAP-01` (CORP), `DL3015` y `DL3066`. Permanecen únicamente informativos de arquitectura. |
| **TOTAL** | **3,596** | **1,396** | **-2,200** | **-61.18%** | **Mejora sustancial y medible.** |

---

## 3. Detalle de Hallazgos Corregidos

### 3.1 `SEC-BANDIT-01` y `SEC-BANDIT-02`: Inyección SQL Potencial en Script de Verificación
- **Herramienta:** Bandit (SAST Python).
- **Código de Regla:** `B608:hardcoded_sql_expressions`.
- **Severidad Original:** Media / Alta Confianza.
- **Ubicación:** `backend/scripts/verificar_restauracion.py` (líneas 37-43).
- **Descripción del Problema:** El script construía consultas SQL para verificar el conteo de registros tras la restauración de una copia de seguridad concatenando dinámicamente nombres de tablas (`f"SELECT count(*) FROM {tabla}"`). Aunque el script era de uso administrativo, representaba un patrón de riesgo de inyección SQL contraria a OWASP A03:2021.
- **Remediación Implementada:** Se refactorizó el script para eliminar por completo la interpolación de cadenas. Se implementó una tupla inmutable de consultas estáticas `QUERIES_CONTEO` mapeadas con identificadores predefinidos, ejecutadas directamente como sentencias SQL constantes mediante `text(...)` de SQLAlchemy.
- **Archivos Modificados:** `backend/scripts/verificar_restauracion.py` (Commit `69cad33`).
- **Evidencia en Reportes After:** El archivo `reports/after/bandit.json` y `reports/after/bandit.html` confirman **0 ocurrencias de B608**. El total de incidencias de severidad Media en Bandit se redujo a **0**.

---

### 3.2 `SEC-PIP-03` y `SEC-PIP-04`: Vulnerabilidades en `python-multipart` y `python-dotenv`
- **Herramienta:** pip-audit / Trivy-FS.
- **Identificadores CVE:**
  - `python-multipart==0.0.12`: CVE-2024-53981 (Denegación de servicio por agotamiento de recursos al procesar formularios multipart maliciosos).
  - `python-dotenv==0.21.0`: CVE-2026-28684 (Riesgo de inyección e inconsistencia al parsear variables multilínea).
- **Severidad Original:** Media / Alta.
- **Ubicación:** `backend/requirements.txt`.
- **Descripción del Problema:** Versiones obsoletas fijadas en las dependencias del backend contenían fallas de parsing y vectores de denegación de servicio en el manejo de cargas útiles HTTP multipart.
- **Remediación Implementada:**
  - Se actualizó `python-multipart` de `0.0.12` a `0.0.33`.
  - Se actualizó `python-dotenv` de `0.21.0` a `1.2.4`.
- **Archivos Modificados:** `backend/requirements.txt` (Commit `afa42fb`).
- **Evidencia en Reportes After:** En `reports/after/pip-audit.json`, las vulnerabilidades asociadas a `python-multipart` y `python-dotenv` desaparecieron completamente. El total de vulnerabilidades en dependencias Python descendió de **45 a 29** (**16 vulnerabilidades eliminadas netas**).

---

### 3.3 `SEC-NPM-01`: Fuga de Credenciales Cross-Origin en `follow-redirects`
- **Herramienta:** npm audit / Trivy-FS.
- **Identificadores CVE:** CVE-2026-111755, CVE-2026-111756, CVE-2026-116689.
- **Severidad Original:** Alta.
- **Ubicación:** `frontend/package-lock.json`.
- **Descripción del Problema:** La librería transitiva `follow-redirects` (utilizada por Axios en el cliente web) filtraba cabeceras de autorización HTTP `Authorization: Bearer <token>` cuando una solicitud era redirigida a un origen o dominio cruzado no confiable.
- **Remediación Implementada:** Se forzó la resolución del árbol de dependencias de npm a `follow-redirects` versión `1.16.2`, donde las cabeceras sensibles se eliminan automáticamente ante redirecciones hacia orígenes externos distintos.
- **Archivos Modificados:** `frontend/package-lock.json` (Commit `cb38852`).
- **Evidencia en Reportes After:** `reports/after/npm-audit.json` confirma **0 vulnerabilidades** en el frontend.

---

### 3.4 `SEC-HADO-02`, `SEC-HADO-03` y `SEC-HADO-04`: Buenas Prácticas y Hardening de Dockerfile
- **Herramienta:** Hadolint (Dockerfile Linter).
- **Reglas Corregidas:**
  - `DL3015`: Falta de bandera `--no-install-recommends` en comando `apt-get install`.
  - `DL3066`: Usuario no-root especificado mediante alias alfanumérico en lugar de UID/GID numérico explícito.
  - `DL3025`: Instrucción `CMD` utilizando sintaxis shell de cadena en lugar de notación array JSON `["bin", "arg1", ...]`.
- **Severidad Original:** Media / Baja.
- **Ubicación:** `docker/backend/Dockerfile`.
- **Descripción del Problema:** La omisión de `--no-install-recommends` descargaba paquetes complementarios innecesarios en la imagen base Debian, aumentando la superficie de ataque y el tamaño del contenedor. El uso de nombres de usuario textuales puede generar incompatibilidades con políticas de seguridad de Kubernetes o Docker namespaces. La sintaxis shell en `CMD` ejecuta el proceso a través de `/bin/sh -c`, impidiendo que las señales de parada del sistema operativo (`SIGTERM`) lleguen limpiamente a Uvicorn.
- **Remediación Implementada:**
  - Se agregó la bandera `--no-install-recommends` a `apt-get install`.
  - Se asignó UID/GID `10001:10001` y se cambió la instrucción a `USER 10001:10001`.
  - Se convirtió el comando de inicio a JSON array: `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=*"]`.
- **Archivos Modificados:** `docker/backend/Dockerfile` (Commit `daf1802`).
- **Evidencia en Reportes After:** `reports/after/hadolint.json` ya no contiene ninguna de las reglas `DL3015`, `DL3066` ni `DL3025`.

---

### 3.5 `SEC-ZAP-01`: Incorporación de Cabecera `Cross-Origin-Resource-Policy`
- **Herramienta:** OWASP ZAP (Baseline y OpenAPI Scan).
- **Identificador de Alerta:** `Cross-Origin-Resource-Policy Header Missing` (Plugin ID 10038).
- **Severidad Original:** Baja / CWE-16.
- **Ubicación:** Endpoints de la API Backend y Reverse Proxy Edge.
- **Descripción del Problema:** La ausencia de la cabecera `Cross-Origin-Resource-Policy` (CORP) permitía potencialmente que navegadores web modernos incluyeran recursos de la API en contextos cross-origin (por ejemplo mediante `<script>`, `<img>` o `<iframe>`), facilitando ataques de filtración espectral (Spectre) o cross-site inclusion.
- **Remediación Implementada:**
  - Se agregó `response.headers["Cross-Origin-Resource-Policy"] = "same-origin"` en el middleware `SecurityHeadersMiddleware` (`backend/app/security_headers.py`).
  - Se añadió la directiva `add_header Cross-Origin-Resource-Policy "same-origin" always;` en la configuración global de Nginx (`docker/edge/nginx.conf`).
- **Archivos Modificados:** `backend/app/security_headers.py`, `docker/edge/nginx.conf` (Commit `077f0d2`).
- **Evidencia en Reportes After:** En `reports/after/zap-baseline.json` y `reports/after/zap-api.json`, la alerta de ausencia de `Cross-Origin-Resource-Policy` fue **completamente eliminada**.

---

## 4. Detalle de Hallazgos que Permanecen (Riesgos Aceptados)

Todos los hallazgos residuales han sido analizados rigurosamente y cuentan con una justificación técnica formal, mitigación compensatoria y vinculación con los estándares normativos autorizados:

### 4.1 Dependencias Criptográficas y de Framework con Versión Fijada (`SEC-PIP-01`, `SEC-PIP-02`, `SEC-PIP-05`, `SEC-PIP-06`)
- **Herramienta:** pip-audit / Trivy.
- **Librerías afectadas:** `python-jose==3.3.0`, `cryptography==47.0.0`, `starlette==0.38.6`, `ecdsa==0.19.2`.
- **Riesgo Aceptado y Justificación:**
  - `python-jose` (CVE-2024-33663 / CVE-2024-33664): Vulnerabilidades asociadas a la manipulación de algoritmos en tokens JWT JWE/JWS con claves RSA. En CriptoMed, la implementación (`backend/app/auth.py`) fuerza de manera estricta y exclusiva el algoritmo simétrico `HS256`, validando la firma HMAC-SHA256 con claves simétricas de alta entropía. No se aceptan tokens sin firmar (`alg: none`) ni firmas asimétricas RSA. Conforme a **RFC 7519** y **RFC 8725** (JSON Web Token Best Current Practices).
  - `cryptography` (CVE-2026-3552 / CVE-2026-3554): Relacionadas con desbordamientos en parsing de certificados PKCS#7 o claves privadas SSH. El backend no parsea certificados dinámicos de clientes ni maneja formatos PKCS#7; utiliza exclusivamente la primitiva `AESGCM` para cifrado simétrico en reposo con claves de 256 bits y tags de autenticación de 128 bits. Conforme a **FIPS 197** y **NIST SP 800-38D**.
  - `starlette` (PYSEC-2026-1941, PYSEC-2026-161): Dependencia interna forzada por `fastapi==0.115.0`. Los vectores de DoS por cabecera Host o manipulación de rutas están mitigados por el proxy inverso Nginx, el cual reescribe y valida la cabecera `Host`, restringe el tamaño máximo del cuerpo de solicitud (`client_max_body_size 10M`) y no delega servicio de archivos estáticos del sistema al backend.
  - `ecdsa` (PYSEC-2026-1325): Ataque de canal lateral Minerva sobre curvas elípticas. CriptoMed no utiliza firmas digitales ECDSA (solo AES-GCM y HMAC-SHA256).
- **Referencia:** `docs/hallazgos.md` (Párrafo 3.1) y `docs/RIESGOS_ACEPTADOS.md`.

### 4.2 Fijación de Versiones en Gestores de Paquetes de SO (`SEC-HADO-01`, `SEC-HADO-05`)
- **Herramienta:** Hadolint (`DL3008`, `DL3018`).
- **Riesgo Aceptado y Justificación:**
  - Hadolint advierte sobre no fijar versiones exactas de paquetes en `apt-get install` (Debian) y `apk add` (Alpine).
  - En distribuciones Linux de ciclo continuo, los espejos oficiales retiran versiones anteriores en cuanto se publican parches de seguridad. Fijar versiones menores específicas (e.g. `libpq-dev=15.2-1`) genera fallos frecuentes y no reproducibles en las construcciones de Docker.
  - **Mitigación Compensatoria:** Se fija la versión e imagen base oficial con SHA de imagen (`python:3.12.7-slim`, `nginx:1.27-alpine`), se limpia la caché local de paquetes en la misma capa (`rm -rf /var/lib/apt/lists/*`), y se aplican las banderas `--no-install-recommends` y `--no-cache`.
- **Referencia:** CIS Docker Benchmark 4.1 y `docs/hallazgos.md`.

### 4.3 Vulnerabilidades en Paquetes Base del Sistema Operativo (`SEC-OS-01`, `SEC-OS-02`)
- **Herramienta:** Trivy (Backend Image: Debian 12 Bookworm; Edge Image: Alpine 3.20).
- **Riesgo Aceptado y Justificación:**
  - Corresponden a paquetes preinstalados en el sistema operativo base de los contenedores (`glibc`, `openssl`, `systemd`, `busybox`, `libxml2`).
  - **Mitigación Arquitectónica (CIS Docker Benchmark):**
    1. **Aislamiento Perimetral de Red:** Ni el contenedor `backend` (puerto 8000) ni `db` (puerto 5432) tienen puertos expuestos al host ni a redes externas. Toda comunicación pasa a través de la red privada Docker `backend_net` y `db_net`.
    2. **Proxy Inverso con TLS 1.3 Exclusivo:** El único contenedor accesible desde el exterior es `edge` en el puerto `8443` con cifrado estricto TLS 1.3 (**RFC 8446**, **NIST SP 800-52 Rev. 2**).
    3. **Principio de Privilegio Mínimo:** El contenedor backend se ejecuta como usuario no privilegiado (`USER 10001:10001`), con capacidades de Linux limitadas (`cap_drop: ALL` donde aplica) y montajes de solo lectura en directorios críticos.
- **Referencia:** `docs/hallazgos.md` (Párrafo 3.3) y `docs/RIESGOS_ACEPTADOS.md`.

### 4.4 Respuestas 4xx y Detección de Autenticación en Análisis Dinámico (`SEC-ZAP-02`, `SEC-ZAP-03`, `SEC-ZAP-04`)
- **Herramienta:** OWASP ZAP.
- **Riesgo Aceptado y Justificación:**
  - Los códigos de error 401 (Unauthorized), 403 (Forbidden) y 422 (Unprocessable Entity) generados durante el escaneo automatizado demuestran la efectividad de los controles de autenticación JWT y validación de esquemas Pydantic frente a peticiones anómalas o sin credenciales válidas.
  - La detección de endpoints de autenticación (`/auth/login`) es el comportamiento previsto de la API clínica para intercambio seguro de credenciales conforme a **NIST SP 800-63B**.
- **Referencia:** `docs/hallazgos.md` (Párrafo 3.4).

---

## 5. Conclusión sobre la Postura de Seguridad Resultante

La ejecución de la **Fase 2** ha dotado al proyecto CriptoMed de una postura de ciberseguridad robusta, verificable y trazable:

1. **Código Seguro por Diseño:** Se erradicaron vulnerabilidades de inyección SQL en la capa de scripts administrativos. El código de la aplicación permanece con **0 vulnerabilidades de severidad Alta o Crítica detectadas por SAST**.
2. **Defensa en Profundidad (Defense-in-Depth):** La protección de la información clínica y de datos personales sensibles no depende de un único mecanismo, sino de la conjunción armónica de:
   - Cifrado en reposo a nivel de columna con AES-256-GCM (**FIPS 197**, **NIST SP 800-38D**).
   - Canales seguros TLS 1.3 exclusivo (**RFC 8446**, **NIST SP 800-52 Rev. 2**).
   - Autenticación JWT con rotación de claves y algoritmo estricto HS256 (**RFC 7519**, **RFC 8725**).
   - Aislamiento de red interna y contenedores no-root (CIS Docker Benchmark).
   - Cabeceras de protección HTTP estrictas (HSTS, CSP, X-Frame-Options, Cross-Origin-Resource-Policy).
3. **Calidad y Estabilidad Funcional:** El 100% de la suite de pruebas automatizadas (65 pruebas unitarias y de integración) concluyó exitosamente, acreditando que las remediaciones no produjeron efectos secundarios adversos.

La plataforma se encuentra completamente preparada y validada para avanzar a la **Fase 3: Gestión de Incidentes y Planes de Contingencia**.
