# CriptoMed
> Proyecto de Ética y Seguridad de los Datos – DS3031 (Entrega 2)

Prototipo web académico que permite demostrar la gestión de historiales médicos sintéticos con acceso controlado por roles, cifrado de campos seleccionados con AES-256-GCM, TLS 1.3 en el edge y logs de auditoría con cadena de hashes SHA-256.

**Despliegue:** Docker Compose local con PostgreSQL 16, FastAPI (Python 3.12.7), React (Vite + Node 20.19.0) y Nginx 1.27 con TLS 1.3.

**Estado de la entrega:** prototipo con frontend, backend, controles de seguridad, pruebas y documentación para demostración local.

> **Límite importante:** CriptoMed no está aprobado para producción ni para datos reales. La DPIA identifica riesgo residual alto por retención y eliminación incompletas; además, faltan aprobaciones operativas y validación legal. Usa únicamente datos sintéticos. Consulta [docs/DPIA.md](docs/DPIA.md) y [docs/FINAL_REPORT.md](docs/FINAL_REPORT.md).

---

## Cómo ejecutar el proyecto

**Requisitos:** Docker y Docker Compose.

1. **Generar .env:** `python3 scripts/generate_secrets.py --generate-env`
2. **Generar certificados:** `./scripts/gen_cert.sh`
3. **Levantar servicios:** `./scripts/dev.sh up`
4. **Sembrar datos de demo:** `./scripts/dev.sh seed`
5. **Abrir aplicación:** https://localhost:8443 (aceptar certificado autofirmado o importar `certs/cert.pem` como confiable). No uses `http://127.0.0.1:8000`: ese puerto no se publica al host.
6. **Usuarios demo:** admin (`admin@criptomed.com`), doctor (`doctor@criptomed.com`), administrativo (`admin@clinica.com`), auditor (`auditor@criptomed.com`) y paciente (`paciente@criptomed.com`). `./scripts/dev.sh deploy` genera credenciales aleatorias y las muestra en la terminal; el login local permite autorellenarlas.

   **Solo para la demo:** las contraseñas de prueba se inyectan al compilar el frontend y se muestran en la pantalla de login. Por diseño son públicas dentro de este prototipo y no deben reutilizarse ni usarse con datos reales o en un despliegue accesible desde Internet. No copies credenciales en README, capturas ni commits.

![Login](docs/images/login.png)

**Si el login falla con CSP / `AxiosError: Network Error`:** el front debe llamar a `/api` (mismo origen 8443), no a `127.0.0.1:8000`. Reconstruye el edge:

```bash
docker compose up -d --build edge
```

**Para reiniciar desde cero:** `./scripts/dev.sh reset`

**Para verificar despliegue:** `./scripts/verificar_despliegue.sh`

---

## Arquitectura Docker

```mermaid
graph TB
    subgraph "Host"
        A[Browser]
    end
    
    subgraph "app_net"
        B[Edge Nginx<br/>TLS 1.3]
        C[Backend FastAPI<br/>puerto 8000]
    end
    
    subgraph "db_net (internal)"
        D[PostgreSQL<br/>puerto 5432]
    end
    
    A -->|HTTPS 8443| B
    B -->|Proxy /api| C
    C --> D
```

**Servicios Docker:**
- **db**: PostgreSQL 16 Alpine - Base de datos con healthcheck, roles (owner y aplicación)
- **backend**: FastAPI con Python 3.12.7 - API REST con healthcheck, usuario no root (UID 10001), filesystem de solo lectura
- **edge**: Nginx 1.27 Alpine - Terminación TLS 1.3 exclusivo, frontend React compilado, proxy a backend
- **init**: Servicio de inicialización (perfil seed) - Crea tablas y carga datos demo
- **backup**: Servicio de backups (perfil tools) - pg_dump + GPG AES-256

**Redes:**
- `app_net`: Frontend y backend (no internal para exponer puerto 8443 al host)
- `db_net`: Base de datos (internal, solo accesible desde backend)

**Puertos:**
- Solo edge publica puerto `8443:8443` al host
- Puertos 5432 (Postgres) y 8000 (backend) son internos, no expuestos

---

## Modelo de datos

**`usuarios`**

| Campo | Tipo | Notas |
|---|---|---|
| id | UUID / PK | |
| nombre | string | |
| email | string, único | |
| password_hash | string | bcrypt (factor 12) |
| rol | enum | `admin`, `doctor`, `administrativo`, `auditor`, `paciente` |
| activo | boolean | para revocación inmediata de accesos |
| intentos_fallidos | integer | contador para bloqueo por fuerza bruta |
| bloqueado_hasta | datetime | timestamp de fin de bloqueo temporal |
| creado_en | timestamp | |

**`pacientes`**

| Campo | Tipo | Notas |
|---|---|---|
| id | UUID / PK | |
| nombre | string (cifrado AES-256-GCM) | AAD: pacientes.nombre.{id} |
| edad | integer | |
| genero | string | |
| tipo_sangre | string | |
| diagnostico | string (cifrado AES-256-GCM) | AAD: pacientes.diagnostico.{id} |
| codigo_cie10 | string, FK → diagnosticos_cie10 | |
| fecha_admision | datetime | |
| doctor_id | UUID, FK → usuarios | médico asignado |
| usuario_id | UUID, FK → usuarios (opcional) | cuenta de login del paciente |
| hospital | string | |
| proveedor_seguro | string | |
| monto_facturado | string (cifrado AES-256-GCM) | AAD: pacientes.monto_facturado.{id} |
| numero_habitacion | string | |
| tipo_admision | string | |
| fecha_alta | datetime | |
| medicacion | string (cifrado AES-256-GCM) | AAD: pacientes.medicacion.{id} |
| resultado_test | string (cifrado AES-256-GCM) | AAD: pacientes.resultado_test.{id} |
| consentimiento_fecha | datetime | fecha registrada; no demuestra aceptación válida por sí sola |
| consentimiento_version | string | versión registrada; no existe flujo digital de consentimiento |

**`diagnosticos_cie10`**

| Campo | Tipo |
|---|---|
| codigo | string / PK |
| descripcion | string |

**`audit_logs`** *(cadena SHA-256 con controles de integridad; no inmutable frente a un administrador privilegiado)*

| Campo | Tipo | Notas |
|---|---|---|
| id | UUID / PK | |
| seq | BigInteger (autoincremental, único) | para orden cronológico |
| hash_prev | string (64) | hash SHA-256 del registro anterior |
| hash_actual | string (64) | hash SHA-256 del registro actual |
| usuario_id | UUID, FK → usuarios (nullable) | |
| accion | enum | `login`, `login_fallido`, `bloqueo`, `lectura`, `edicion`, `borrado`, `transferencia`, `exportacion`, `acceso_emergencia` |
| recurso | string | ej. `paciente:UUID` |
| timestamp | datetime | UTC |
| ip_origen | string | |
| detalle | string (nullable) | detalle adicional |

**`accesos_emergencia`** *(break-glass)*

| Campo | Tipo | Notas |
|---|---|---|
| id | UUID / PK | |
| paciente_id | UUID, FK → pacientes | |
| doctor_id | UUID, FK → usuarios | |
| justificacion | string | mínimo 20 caracteres |
| otorgado_en | datetime | |
| expira_en | datetime | ventana de 30 minutos |

---

## Roles y permisos

| Rol | Login | Ver pacientes | Ver diagnóstico | Editar pacientes | Gestionar usuarios | Ver audit logs |
|---|---|---|---|---|---|---|
| **Administrador** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Doctor** | ✅ | ✅ (asignados) | ✅ (asignados) | ✅ (asignados) | ❌ | ❌ |
| **Administrativo** | ✅ | ✅ (datos básicos) | ❌ | ✅ (admisión/facturación) | ❌ | ❌ |
| **Auditor** | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ (solo lectura) |
| **Paciente** | ✅ | ✅ (propio) | ✅ (propio) | ❌ | ❌ | ❌ (solo accesos propios) |

**Nota:** El rol administrativo NO ve diagnóstico, medicación ni resultado_test (Paso 0.3). El rol paciente puede ver sus accesos y exportar sus datos (Paso 1.7).

---

## Seguridad

| Medida | Implementación | Estándar |
|---|---|---|
| Cifrado en reposo | AES-256-GCM con llaves versionadas (v1, v2) y AAD en cinco campos: nombre, diagnóstico, medicación, resultado_test y monto_facturado | FIPS 197, NIST SP 800-38D |
| Cifrado en tránsito | TLS 1.3 exclusivo en edge Nginx, certificado autofirmado (OpenSSL) | RFC 8446, NIST SP 800-52 Rev. 2 |
| Hashing de contraseñas | bcrypt factor 12, política NIST SP 800-63B (sin composición obligatoria, sin expiración periódica) | OWASP Password Storage Cheat Sheet, NIST SP 800-63B |
| Autenticación | JWT HS256; expiración configurable por `JWT_EXPIRE_MINUTES` (30 en `.env.example`, 15 como fallback del backend), verifica activo y bloqueado_hasta en cada request | RFC 7519, RFC 8725 |
| Autorización | RBAC (5 roles), principio de mínimo privilegio, filtrado en backend (no solo frontend) | NIST SP 800-63B, OWASP ASVS |
| Auditoría | Logs detectables ante alteraciones: cadena SHA-256, pg_advisory_xact_lock, triggers anti-UPDATE/DELETE y rol de aplicación con solo INSERT/SELECT | NIST SP 800-92, OWASP Logging Cheat Sheet |
| Bloqueo por fuerza bruta | Bloqueo tras 5 intentos fallidos (15 min), rate limiting 10 req/min por IP (slowapi) | NIST SP 800-63B |
| Usuario no root | El backend corre como UID 10001; el servicio `init` anula ese usuario y se ejecuta como root. El edge tampoco aplica todos los controles de usuario | CIS Docker Benchmark 4.1 |
| Capabilities mínimas | `cap_drop: ALL` + capacidades necesarias en db, backend e init; el edge no aplica este control | CIS Docker Benchmark 5.26 |
| Secretos de runtime | `.env` no se copia al backend y la llave privada TLS se monta en runtime. **Excepción de demo:** las credenciales de prueba se compilan en el frontend y quedan públicas en la imagen edge; no usar en producción. | CIS Docker Benchmark 4.1, OWASP ASVS V7.2.1 |
| Healthchecks | pg_isready (db), /health endpoint (backend) | CIS Docker Benchmark 6.1 |
| Límites de recursos | mem_limit y pids_limit configurados en docker-compose.yml | CIS Docker Benchmark 5.17 |
| Filesystem read-only | Backend e init con read_only: true, tmpfs para /tmp | CIS Docker Benchmark 5.15 |
| Redes internas | db_net: internal (solo backend accede a PostgreSQL) | CIS Docker Benchmark 5.8 |
| Cabeceras de seguridad | HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, CSP, Cross-Origin-Resource-Policy | OWASP ASVS V7 |

Para más detalles de hardening, ver `docs/HARDENING_DOCKER.md`.

**Límites conocidos:** otros datos personales/de salud (por ejemplo edad, tipo de sangre, CIE-10 y fechas) no están cifrados campo por campo en PostgreSQL. La cadena de hashes y los triggers dificultan/detectan cambios mediante el rol de aplicación, pero un administrador de base de datos con privilegios puede modificar los controles; no existe anclaje externo de logs.

---

## Endpoints principales

| Método | Ruta | Rol requerido | Descripción |
|---|---|---|---|
| POST | `/api/auth/login` | público | Login, retorna JWT |
| GET | `/api/pacientes` | doctor, admin, administrativo | Lista pacientes (campos según rol) |
| GET | `/api/pacientes/{id}` | doctor (asignado), admin | Detalle completo |
| POST | `/api/pacientes` | admin, administrativo | Crear paciente |
| PUT | `/api/pacientes/{id}` | doctor (asignado), admin | Editar historial |
| DELETE | `/api/pacientes/{id}` | admin | Borrado |
| GET | `/api/usuarios` | admin | Gestión de usuarios |
| POST | `/api/usuarios` | admin | Crear usuario |
| PATCH | `/api/usuarios/{id}/revocar` | admin | Revocar acceso |
| GET | `/api/audit-logs` | auditor, admin | Consultar logs (solo lectura) |
| GET | `/api/audit-logs/alertas` | auditor, admin | Alertas de accesos anómalos |
| GET | `/api/pacientes/me` | paciente | Ver propio historial |
| GET | `/api/pacientes/me/accesos` | paciente | Lista de accesos a su historial |
| GET | `/api/pacientes/me/export` | paciente | Exportar sus datos (JSON) |
| GET | `/api/pacientes/doctores` | paciente, admin | Lista doctores disponibles |
| PATCH | `/api/pacientes/{id}/transferir-doctor` | paciente (propio), admin | Transferir paciente a otro doctor |
| POST | `/api/pacientes/{id}/acceso-emergencia` | doctor | Acceso de emergencia (break-glass) |

---

## Documentación

- `docs/DOCKER.md` - Documentación de Docker (diagramas, puertos, volúmenes, debugging)
- `docs/HARDENING_DOCKER.md` - Resumen de hardening Docker con tabla de controles (CIS, OWASP)
- `docs/FINAL_REPORT.md` - Informe final completo (narrativa de diseño, verificación con herramientas, DPIA, consideraciones éticas, lecciones aprendidas)
- `docs/inventario_datos.md` - Inventario completo de datos (45 campos, categorías, cifrado, roles)
- `docs/DPIA.md` - Evaluación de Impacto en la Protección de Datos (DPIA) completa
- `docs/flujo_datos.mmd` - Diagrama de flujo de datos Mermaid
- `docs/etica_privacidad.md` - Consideraciones éticas y privacidad
- `docs/hallazgos.md` - Registro de hallazgos de seguridad (escaneo inicial)
- `docs/comparativa_antes_despues.md` - Comparativa de escaneos antes/después de remediación
- `docs/BACKUPS.md` - Procedimientos y evidencia de continuidad (revisar límites de automatización)
- `docs/objetivos_vs_resultados.md` - Estado de objetivos y evidencia
- `docs/matriz_trazabilidad.md` - Trazabilidad de requisitos

---

## Stack técnico

| Capa | Tecnología | Versión |
|---|---|---|
| Backend | Python + FastAPI | 3.12.7 |
| Base de datos | PostgreSQL | 16 Alpine |
| ORM | SQLAlchemy | - |
| Auth | JWT (`python-jose`) + `bcrypt` | HS256, factor 12 |
| Encriptación | `cryptography` (AES-256-GCM) | - |
| Frontend | React + Vite | Node 20.19.0 |
| Edge | Nginx | 1.27 Alpine |
| Orquestación | Docker Compose | - |
| Control de versiones | Git / GitHub | - |

---

## Scripts de operación

- `./scripts/dev.sh up` - Genera certificados si faltan, valida .env, build y levanta servicios
- `./scripts/dev.sh seed` - Ejecuta el perfil seed (carga datos demo)
- `./scripts/dev.sh down` - Detiene servicios
- `./scripts/dev.sh reset` - down -v + up + seed
- `./scripts/dev.sh logs` - Muestra logs de servicios
- `./scripts/dev.sh ps` - Muestra estado de servicios
- `./scripts/dev.sh test` - Ejecuta pytest en backend
- `./scripts/dev.sh shell-db` - Abre psql en contenedor db
- `./scripts/backup.sh` - Crea un backup cifrado local (ejecución manual)
- `./scripts/restore.sh <archivo>` - Restaura a `criptomed_restore_test`, nunca sobre la base principal
- `./scripts/verificar_despliegue.sh` - Comprueba TLS, puertos, salud de servicios, login, usuario no root, ausencia de `.env`/`.pem` en ubicaciones de imagen revisadas, placeholders en config e imágenes requeridas. No comprueba reset, retención ni cumplimiento legal.
- `./scripts/security_scan.sh` - Ejecuta suite multi-herramienta (Bandit, pip-audit, npm audit, Gitleaks, Hadolint, Trivy, testssl.sh, OWASP ZAP)
- `./scripts/rotate_keys.py` - Rotación de llaves de cifrado (con --dry-run)

**Continuidad:** el 2026-11-16 se generó un backup cifrado local y se restauró en la base aislada de prueba en 3 segundos; conteos, cadena de auditoría y descifrado de muestra se verificaron. Es una medición puntual, no un SLA. No hay scheduler, copia off-site, WAL archiving ni RPO garantizado; la retención conserva los últimos 7 archivos, no necesariamente 7 días.

---

## Estructura del repositorio

```
cripto-med/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── auth.py
│   │   ├── rbac.py
│   │   ├── crypto.py
│   │   ├── audit.py
│   │   └── routers/
│   │       ├── auth.py
│   │       ├── usuarios.py
│   │       ├── pacientes.py
│   │       └── audit_logs.py
│   ├── scripts/
│   │   ├── setup_db_docker.py
│   │   ├── seed_db.py
│   │   ├── rotate_keys.py
│   │   ├── verificar_cifrado.py
│   │   └── verificar_cadena_logs.py
│   ├── scripts/sql/
│   │   └── proteger_audit_logs.sql
│   ├── requirements.txt
│   └── .dockerignore
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── docker/
│   ├── backend/Dockerfile
│   ├── edge/Dockerfile
│   ├── edge/nginx.conf
│   ├── backup/Dockerfile
│   └── db/init/
│       ├── 02-create-tables.sql
│       └── 03-seed.sql
├── scripts/
│   ├── dev.sh
│   ├── dev.ps1
│   ├── gen_cert.sh
│   ├── generate_secrets.py
│   ├── generate_keys.py
│   ├── rotate_keys.py
│   ├── security_scan.sh
│   └── verificar_despliegue.sh
├── docs/
│   ├── DOCKER.md
│   ├── HARDENING_DOCKER.md
│   ├── FINAL_REPORT.md
│   ├── inventario_datos.md
│   ├── DPIA.md
│   ├── flujo_datos.mmd
│   ├── etica_privacidad.md
│   ├── hallazgos.md
│   └── comparativa_antes_despues.md
├── reports/
│   ├── before/
│   └── after/
├── certs/
│   ├── cert.pem
│   └── key.pem
├── docker-compose.yml
├── .env.example
├── .dockerignore
└── README.md
```

---

## Verificación de despliegue

El script `./scripts/verificar_despliegue.sh` verifica:

1. ✅ HTTPS://localhost:8443 responde con TLS 1.3 negociado
2. ✅ Puertos 5432 (Postgres) y 8000 (backend) NO son expuestos por Docker
3. ✅ Todos los servicios (db, backend, edge) están healthy/up
4. ✅ Login con usuario demo funciona a través de https://localhost:8443/api/auth/login
5. ✅ Backend corre con UID 10001 (usuario no root)
6. ✅ El script busca `.env` en backend y `.pem` en edge; no comprueba todos los secretos posibles ni que credenciales de demo estén fuera del frontend
7. ✅ docker compose config no contiene secretos literales
8. ✅ Las imágenes de backend e init requeridas existen

Estas verificaciones de despliegue no prueban cumplimiento legal, expiración/purga de datos ni recuperación de una copia de seguridad.

---

## Verificación de seguridad

El script `./scripts/security_scan.sh` ejecuta:

- **Bandit** (SAST Python) - Patrones inseguros en código
- **pip-audit** (SCA Backend) - Vulnerabilidades en dependencias Python
- **npm audit** (SCA Frontend) - Vulnerabilidades en dependencias JavaScript
- **Gitleaks** (Secretos) - Credenciales en repo e historial
- **Hadolint** (Dockerfile Linter) - Buenas prácticas Docker
- **Trivy** (Vulnerabilidades) - Escaneo de imágenes y filesystem
- **testssl.sh** (TLS DAST) - Configuración TLS del servidor
- **OWASP ZAP** (DAST) - Inyección, headers, CORS, configuración

Resultados históricos documentados tras remediación (no revalidados en esta revisión):
- Reducción reportada del 61.18% en hallazgos (3,596 → 1,396)
- El reporte previo no encontró vulnerabilidades altas/medias en código propio ni vulnerabilidades directas en frontend
- El reporte previo no encontró fugas de secretos

Estos resultados dependen del momento, alcance y configuración del escaneo; no son una garantía sobre el estado actual ni una certificación.

---

## Marco normativo y referencias técnicas

Las referencias siguientes orientan el diseño y las verificaciones técnicas; **no equivalen a certificación ni prueban por sí solas cumplimiento legal**:

- **Perú:** Ley N.° 29733 y Reglamento D.S. 016-2024-JUS, vigente desde 2025. Antes de tratar datos reales, la clínica debe validar obligaciones, base jurídica, retención, derechos y plazos de incidentes con la normativa y guía ANPD vigentes.
- **GDPR Arts. 25, 35 y 36:** privacidad desde el diseño, DPIA y consulta previa solo cuando el GDPR sea aplicable territorialmente y se cumplan sus criterios de riesgo.
- **ISO/IEC 29134:** metodología para evaluación de impacto de privacidad.
- **NIST SP 800-38D, SP 800-63B, SP 800-92; RFC 8446, RFC 7519 y RFC 8725; OWASP ASVS/Cheat Sheets y CIS Docker Benchmark:** referencias para controles técnicos concretos.

La app no tiene un proceso automatizado de retención/supresión ni una aprobación de tratamiento real. La DPIA queda limitada a una demo local con datos sintéticos.

---

## Evolución del proyecto

**Entrega 1:** Sistema desplegado en Render (backend) y GitHub Pages (frontend), cifrado con Fernet (AES-128-CBC + HMAC).

**Entrega 2:**
- Migración a despliegue local con Docker Compose para control de aislamiento de red, terminación TLS y gestión de llaves
- Migración de Fernet a AES-256-GCM con llaves versionadas (FIPS 197, NIST SP 800-38D)
- Implementación de cadena de hashes SHA-256 en logs de auditoría (NIST SP 800-92)
- Implementación de bloqueo por fuerza bruta y rate limiting (NIST SP 800-63B)
- Escaneos históricos de seguridad reportan una reducción del 61.18% en hallazgos; no se revalidó en esta revisión
- DPIA con 12 riesgos; uno residual alto (retención) pendiente de mitigación antes de producción
- Consideraciones éticas y privacidad (autonomía del paciente, break-glass, transparencia IA)
- Informe reescrito como narrativa de diseño (no checklist)

---

## Créditos

**Estudiantes:** María Fernanda Lazón y Christopher Pérez
**Curso:** DS3031 - Ética y Seguridad de Datos  
**Profesor:** José Carlos Pazos Ortiz
**Fecha:** Noviembre 2026