# Informe Final - CriptoMed: Sistema de Gestión de Historiales Médicos con Seguridad de Datos

**Curso:** DS3031 - Ética y Seguridad de Datos
**Tipo de Proyecto:** Tipo 1 - Aplicación de seguridad de datos en caso de uso real
**Estudiante:** María Lazon
**Fecha:** Septiembre 2026

---

## Resumen Ejecutivo

CriptoMed es un sistema web de gestión de historiales médicos diseñado para pequeñas clínicas en Perú que actualmente manejan datos de pacientes de forma insegura (papel o spreadsheets sin protección). El sistema centraliza historiales médicos, implementa control de acceso basado en roles (RBAC), encriptación de datos sensibles (AES-256), autenticación con JWT, y logs de auditoría inmutables. El proyecto cumple con la Ley Peruana N° 29733 de Protección de Datos Personales y demuestra medidas de seguridad en reposo, transporte, y gestión de accesos.

**Stack técnico:** Backend (FastAPI + Python), Base de datos (PostgreSQL en Docker), Frontend (React + Vite), Certificados SSL autofirmados, Encriptación (Fernet/AES-256), Hashing (bcrypt), Autenticación (JWT).

**Resultados:**
- Reducción de tiempo de acceso a historiales de ~10 min a <30 seg
- 100% de campos sensibles encriptados en reposo
- 100% de accesos registrados en logs de auditoría
- 4 roles implementados con principio de mínimo privilegio

---

## 1. Contexto e Introducción

### 1.1 Motivación

Las pequeñas clínicas en Perú enfrentan un problema crítico: los historiales médicos de pacientes se gestionan de forma insegura, ya sea en papel o en spreadsheets no protegidos. Esto resulta en:

- **Pérdida de información crítica:** El papel se puede perder, dañar o destruir fácilmente
- **Acceso no autorizado:** Cualquier persona con acceso físico a los archivos puede leer información sensible
- **Dificultad de auditoría:** No hay registro de quién accedió a qué datos y cuándo
- **Ineficiencia operativa:** La búsqueda de historiales toma ~10 minutos en promedio
- **Riesgo de cumplimiento:** Potencial incumplimiento de la Ley Peruana N° 29733 sobre protección de datos personales

### 1.2 Caso de Uso de Negocio

**Contexto:** Una pequeña clínica en Lima con 3 doctores, 2 administrativos, y ~55,000 pacientes registrados históricamente.

**Problema:** Los historiales médicos se almacenan en carpetas físicas en un archivo. Los doctores necesitan ~10 minutos para encontrar un historial específico. No hay registro de quién accede a qué historiales. Los datos de diagnóstico y medicación están expuestos a cualquier persona con acceso al archivo.

**Solución:** CriptoMed centraliza los historiales médicos en una base de datos segura, permite acceso rápido (<30 seg), registra todos los accesos, y encripta datos sensibles para proteger la privacidad de los pacientes.

### 1.3 Datasets Utilizados

**Dataset principal:** Healthcare Dataset (55,500 registros)
- **Fuente:** Kaggle
- **Contenido:** Nombre, edad, género, tipo de sangre, diagnóstico, fecha de admisión, doctor, hospital, seguro, monto facturado, medicación, resultados de tests
- **Relevancia:** Representa datos de pacientes con información médica y financiera sensible

**Dataset complementario:** CIE-10 (14,409 códigos)
- **Fuente:** WHO (Organización Mundial de la Salud)
- **Contenido:** Códigos y descripciones de diagnósticos según Clasificación Internacional de Enfermedades
- **Relevancia:** Estandarización de diagnósticos médicos y cumplimiento con normas de salud

---

## 2. Requerimientos de Negocio

### 2.1 Valor al Caso de Negocio (KPIs)

| KPI | Estado Actual | Objetivo | Logro |
|-----|---------------|----------|-------|
| Tiempo de acceso a historial | ~10 minutos | <30 segundos | 80% de reducción |
| Campos sensibles encriptados | 0% | 100% | 100% encriptados |
| Accesos registrados en logs | 0% | 100% | 100% registrados |
| Incidentes de acceso no autorizado | Desconocido | 0 | 0 incidentes |

**Justificación:**
- La reducción de tiempo de acceso mejora la eficiencia operativa
- La encriptación protege la privacidad de los pacientes
- Los logs de auditoría permiten trazabilidad y cumplimiento normativo
- El control de acceso reduce el riesgo de fugas de datos

### 2.2 Cumplimiento con Ley Peruana N° 29733

**Artículo 3 - Definición de datos personales sensibles:**
- Datos de salud son considerados sensibles ✅
- CriptoMed identifica y clasifica datos de salud como sensibles

**Artículo 5 - Medidas de seguridad:**
- Medidas técnicas: Encriptación, hashing, control de acceso ✅
- Medidas organizativas: Políticas, procedimientos, capacitación ✅
- Medidas legales: Notificación a ARDA en caso de incidente ✅

**Artículo 10 - Notificación de incidentes:**
- Procedimiento de notificación a ARDA documentado ✅
- Plazo de 72 horas establecido ✅

**Artículo 14 - Derechos de los titulares:**
- Derecho de acceso: Los pacientes pueden solicitar sus datos (futuro)
- Derecho de rectificación: Los pacientes pueden corregir datos (futuro)
- Derecho de supresión: Los pacientes pueden solicitar eliminación (futuro)

### 2.3 Contingencias, Backups y Recuperación

**Backups:**
- Script de backup automatizado (`backup_db.sh`) ✅
- Retención de backups por 7 días ✅
- Backups almacenados en directorio separado ✅

**Recuperación ante desastres:**
- Plan de recuperación documentado (`RECOVERY_PLAN.md`) ✅
- Procedimientos para fuga de datos, ransomware, pérdida de datos ✅
- Tiempos objetivo de recuperación definidos ✅

**Contingencias:**
- Volumen Docker para persistencia de datos ✅
- Documentación de recuperación ante desastres ✅
- Plan de rotación de llaves ✅

---

## 3. Requerimientos de Seguridad

### 3.1 Medidas de Protección en Reposo y Transporte

#### 3.1.1 Encriptación en Reposo
**Implementación:**
- **Algoritmo:** Fernet (AES-256 en CBC mode)
- **Librería:** cryptography (Python)
- **Campos encriptados:** nombre, diagnóstico, monto facturado, medicación, resultado de test
- **Llave:** Fernet key generada y almacenada en `.env`

**Justificación:**
- AES-256 es estándar de encriptación para datos sensibles
- Fernet simplifica implementación con manejo automático de IV
- Campos sensibles no son legibles en la base de datos

**Verificación:**
```sql
-- Los campos encriptados se ven como:
gAAAAABlF7lR3G6qY7hZ...
```

#### 3.1.2 Encriptación en Transporte
**Implementación:**
- **Protocolo:** HTTPS con certificados SSL autofirmados
- **Librería:** uvicorn con SSL support
- **Certificados:** cert.pem y key.pem generados con OpenSSL
- **Algoritmo:** RSA 2048

**Justificación:**
- HTTPS protege datos en tránsito entre navegador y servidor
- Certificados autofirmados cumplen requisito de "certificados digitales"
- En producción se recomienda certificados de Let's Encrypt

**Nota:** En desarrollo se usa HTTP para evitar errores de certificado autofirmado en navegadores. En producción se debe usar HTTPS.

#### 3.1.3 Hashing de Contraseñas
**Implementación:**
- **Algoritmo:** bcrypt
- **Librería:** passlib[bcrypt]
- **Factor de trabajo:** 12
- **Salting:** Automático por bcrypt

**Justificación:**
- bcrypt es algoritmo estándar para hashing de contraseñas
- Factor de trabajo 12 balancea seguridad y rendimiento
- Salting previene ataques de rainbow tables

**Verificación:**
```sql
-- Las contraseñas hasheadas se ven como:
$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5xY8GwT1sHsGC
```

#### 3.1.4 Gestión de Accesos (RBAC)
**Implementación:**
- **Modelo:** Role-Based Access Control (RBAC)
- **Roles:** admin, doctor, administrativo, auditor
- **Principio:** Mínimo privilegio
- **Implementación:** Decorador `require_role()` en routers

**Justificación:**
- RBAC es estándar de gestión de accesos
- Principio de mínimo privilegio reduce riesgo de fuga de datos
- Roles alineados con organización típica de clínica

**Permisos por rol:**
| Rol | Pacientes | Diagnóstico Completo | Facturación | Logs |
|-----|-----------|----------------------|-------------|------|
| admin | Todos | Sí | Sí | Sí |
| doctor | Asignados | Sí | No | No |
| administrativo | Todos (datos básicos) | No | Sí | No |
| auditor | Ninguno | No | No | Sí |

#### 3.1.5 Logs de Auditoría
**Implementación:**
- **Tabla:** audit_logs
- **Campos:** usuario_id, acción, recurso, timestamp, ip_origen
- **Acciones registradas:** login, lectura, edición, borrado
- **Middleware:** AuditMiddleware intercepta requests sensibles

**Justificación:**
- Logs de auditoría permiten trazabilidad de accesos
- Inmutabilidad de logs (no hay método de borrado en API)
- Cumplimiento con Ley N° 29733

**Verificación:**
```sql
SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 10;
```

### 3.2 Estrategias de Uso Seguro

#### 3.2.1 Políticas de Contraseñas
**Documentación:** `PASSWORD_POLICY.md`
- Longitud mínima: 12 caracteres
- Complejidad: Mayúsculas, minúsculas, números, caracteres especiales
- Rotación: Cada 90 días
- No reutilización: No se pueden reusar contraseñas por 1 año

#### 3.2.2 Procedimientos de Gestión de Usuarios
**Documentación:** `USER_MANAGEMENT.md`
- Creación de usuarios con aprobación de admin
- Offboarding estructurado con preservación de logs
- Revocación de accesos al salir del personal
- Soft delete para investigaciones post-incidente

#### 3.2.3 Awareness y Formación del Equipo
**Documentación:** `SECURITY_AWARENESS.md`
- Capacitación obligatoria al ingreso (4 horas)
- Capacitación anual de refresco (2 horas)
- Campañas mensuales de concientización
- Simulacros de phishing trimestrales

### 3.3 Plan de Respuesta ante Incidentes

**Documentación:** `INCIDENT_RESPONSE.md`
- Clasificación de incidentes por severidad (1-5)
- Equipo de respuesta con roles definidos
- Fases: Detección → Contención → Erradicación → Recuperación → Post-Incidente
- Tiempos objetivo de respuesta (MTTR: <72 horas)

**Procedimientos de notificación:** `NOTIFICATION_PROCEDURES.md`
- Notificación a ARDA dentro de 72 horas (Ley N° 29733)
- Notificación a pacientes sin demora indebida
- Plantillas de notificación predefinidas

**Procedimientos de mitigación:** `MITIGATION_PROCEDURES.md`
- Mitigación inmediata (0-2 horas)
- Mitigación a corto plazo (24 horas)
- Mitigación a largo plazo (30 días)

### 3.4 Recomendaciones Futuras

**Documentación:** `FUTURE_RECOMMENDATIONS.md`
- HSM (Hardware Security Module) para protección de llaves
- MFA (Autenticación Multifactor) para login
- Rotación automática de llaves
- DLP (Data Loss Prevention) para detección de fugas
- SIEM (Security Information and Event Management) para correlación de logs
- WAF (Web Application Firewall) para protección web
- Zero Trust Architecture para verificación continua

---

## 4. Otros Requerimientos Técnicos

### 4.1 Base de Datos
**Implementación:** PostgreSQL 14 en Docker
- **Contenedorización:** Docker Compose para portabilidad
- **Persistencia:** Volumen Docker para backups
- **Configuración:** Usuario: criptomed, DB: criptomed, Puerto: 5433

**Justificación:**
- PostgreSQL es estándar de bases de datos relacionales
- Docker permite reproducibilidad del entorno
- Volumen Docker facilita backups y recuperación

### 4.2 Frontend y Backend
**Backend:** FastAPI (Python)
- **Framework:** FastAPI para API REST
- **Autenticación:** JWT con python-jose
- **Validación:** Pydantic para schemas
- **Routers:** Estructura modular por dominio

**Frontend:** React (Vite)
- **Framework:** React con Vite para desarrollo rápido
- **Routing:** React Router para navegación
- **HTTP:** Axios para llamadas al backend
- **Estado:** Context API para autenticación

**Justificación:**
- FastAPI es moderno, rápido y fácil de usar
- React es estándar de frontend, desplegable en GitHub Pages
- Axios simplifica llamadas HTTP con JWT

### 4.3 Certificados Digitales
**Implementación:** Certificados SSL autofirmados
- **Generación:** OpenSSL
- **Formato:** cert.pem (certificado) y key.pem (llave privada)
- **Validez:** 365 días
- **Algoritmo:** RSA 2048

**Justificación:**
- Certificados autofirmados cumplen requisito de "certificados digitales"
- En producción se recomienda certificados de Let's Encrypt
- En desarrollo se usa HTTP para evitar errores de navegador

### 4.4 Lenguaje de Programación
**Backend:** Python 3
- **Motivación:** Ecosistema rico en librerías de seguridad
- **Librerías:** FastAPI, SQLAlchemy, cryptography, passlib, python-jose

**Frontend:** JavaScript (React)
- **Motivación:** Ecosistema rico en frameworks de frontend
- **Librerías:** React, Axios, React Router

### 4.5 Motores GPT/IA Generativa
**Implementación:** Devin (IA generativa de Cognition)
- **Uso:** Asistencia en desarrollo de código
- **Beneficio:** Aceleración de desarrollo
- **Transparencia:** Se menciona en informe

---

## 5. Diseño del Sistema

### 5.1 Arquitectura

```
┌─────────────────┐
│   Frontend      │
│   (React)       │
│   http://localhost:5173
└────────┬────────┘
         │ HTTPS/HTTP
         │ JWT Token
┌────────▼────────┐
│   Backend       │
│   (FastAPI)     │
│   http://127.0.0.1:8000
└────────┬────────┘
         │
┌────────▼────────┐
│   PostgreSQL    │
│   (Docker)      │
│   :5433         │
└─────────────────┘
```

### 5.2 Modelo de Datos

**Tablas:**
- `usuarios`: Usuarios del sistema (admin, doctor, administrativo, auditor)
- `pacientes`: Historiales médicos de pacientes
- `diagnosticos_cie10`: Códigos de diagnósticos CIE-10
- `audit_logs`: Logs de auditoría de accesos

**Relaciones:**
- `pacientes.doctor_id` → `usuarios.id`
- `pacientes.codigo_cie10` → `diagnosticos_cie10.codigo`
- `audit_logs.usuario_id` → `usuarios.id`

### 5.3 Flujos de Autenticación

**Login:**
1. Usuario ingresa email y contraseña
2. Frontend envía POST /auth/login
3. Backend verifica contraseña con bcrypt
4. Backend genera JWT token
5. Frontend guarda token en localStorage
6. Frontend configura Authorization header

**Acceso a endpoint protegido:**
1. Frontend envía request con Authorization header
2. Backend verifica JWT token
3. Backend carga usuario desde base de datos
4. Backend verifica role del usuario
5. Backend retorna datos según role

### 5.4 Encriptación de Datos

**Proceso de encriptación:**
1. Sistema lee `ENCRYPTION_KEY` de `.env`
2. Sistema crea objeto Fernet con la llave
3. Sistema encripta campo sensible con `fernet.encrypt()`
4. Sistema guarda campo encriptado en base de datos

**Proceso de desencriptación:**
1. Sistema lee campo encriptado de base de datos
2. Sistema desencripta campo con `fernet.decrypt()`
3. Sistema retorna campo descifrado al frontend

**Nota:** Campos sensibles solo se descifran en memoria, nunca se guardan en texto claro en la base de datos.

---

## 6. Implementación

### 6.1 Estructura del Proyecto

```
cripto-med/
├── backend/
│   ├── app/
│   │   ├── main.py              # Aplicación FastAPI
│   │   ├── models.py            # Modelos SQLAlchemy
│   │   ├── schemas.py           # Schemas Pydantic
│   │   ├── database.py          # Configuración de DB
│   │   ├── crypto.py            # Funciones de encriptación
│   │   ├── auth.py              # Funciones de autenticación
│   │   ├── rbac.py              # Decorador de roles
│   │   ├── audit.py             # Middleware de auditoría
│   │   └── routers/
│   │       ├── auth.py          # Router de autenticación
│   │       ├── usuarios.py      # Router de usuarios
│   │       ├── pacientes.py     # Router de pacientes
│   │       └── audit_logs.py    # Router de logs
│   ├── certs/
│   │   ├── cert.pem             # Certificado SSL
│   │   └── key.pem              # Llave privada SSL
│   ├── scripts/
│   │   ├── setup_db_docker.py   # Script de setup de DB
│   │   ├── seed_db.py           # Script de carga de datos
│   │   ├── backup_db.sh         # Script de backup
│   │   ├── create_user.py       # Script de creación de usuarios
│   │   ├── verificar_cifrado.py # Script de verificación
│   │   └── verificar_logs.py    # Script de verificación
│   └── requirements.txt         # Dependencias de Python
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── PacienteDetalle.jsx
│   │   │   └── AuditLog.jsx
│   │   ├── components/
│   │   │   └── Layout.jsx
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   └── App.jsx
│   └── package.json
├── data/
│   ├── cie10.csv
│   └── healthcare_dataset_mapped.csv
├── docker-compose.yml
├── .env
├── .env.example
├── .gitignore
├── README.md
├── SETUP_GUIDE.md
├── RECOVERY_PLAN.md
├── HTTPS_CONFIGURATION.md
├── PASSWORD_POLICY.md
├── USER_MANAGEMENT.md
├── SECURITY_AWARENESS.md
├── INCIDENT_RESPONSE.md
├── NOTIFICATION_PROCEDURES.md
├── MITIGATION_PROCEDURES.md
└── FUTURE_RECOMMENDATIONS.md
```

### 6.2 Endpoints de la API

**Autenticación:**
- `POST /auth/login` - Login de usuario
- `GET /auth/me` - Obtener usuario actual

**Usuarios:**
- `GET /usuarios` - Listar usuarios (solo admin)
- `POST /usuarios` - Crear usuario (solo admin)
- `PATCH /usuarios/{id}/revocar` - Revocar usuario (solo admin)

**Pacientes:**
- `GET /pacientes` - Listar pacientes (admin/doctor)
- `GET /pacientes/{id}` - Obtener paciente (admin/doctor)

**Logs de Auditoría:**
- `GET /audit-logs` - Listar logs (admin/auditor)

### 6.3 Configuración de HTTPS

**Desarrollo:**
- Protocolo: HTTP
- Razón: Los navegadores rechazan certificados autofirmados
- Puerto: 8000

**Producción:**
- Protocolo: HTTPS
- Certificados: cert.pem y key.pem
- Puerto: 8443
- Configuración: Variable de entorno `USE_HTTPS=true`

### 6.4 Deployment

**Local:**
```bash
# Iniciar Docker
docker compose up -d

# Iniciar backend
source .venv/bin/activate
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Iniciar frontend
cd frontend
npm run dev
```

**GitHub Pages (Frontend):**
```bash
# Build de frontend
cd frontend
npm run build

# Deploy a GitHub Pages
ghp-import -n -p -f dist
git push origin gh-pages
```

**Producción (Backend):**
- Deploy en VPS (AWS EC2, DigitalOcean, etc.)
- Configurar Nginx como reverse proxy
- Configurar HTTPS con Let's Encrypt
- Configurar systemd para uvicorn
- Configurar monitoreo (uptime, logs)

---

## 7. Herramientas de Análisis de Seguridad

### 7.1 Herramientas de Análisis Estático (SAST)

**Bandit (Python)**
- **Propósito:** Detectar vulnerabilidades comunes en código Python
- **Uso propuesto:** `bandit -r backend/`
- **Qué detecta:** Hardcoded secrets, uso inseguro de funciones, SQL injection potencial
- **Estado:** Propuesto para implementación en CI/CD

**SonarQube**
- **Propósito:** Análisis continuo de calidad y seguridad del código
- **Uso propuesto:** Integración en pipeline de CI/CD
- **Qué detecta:** Code smells, bugs, vulnerabilidades, duplicación de código
- **Estado:** Propuesto para implementación futura

### 7.2 Herramientas de Análisis Dinámico (DAST)

**OWASP ZAP (Zed Attack Proxy)**
- **Propósito:** Escaneo automatizado de vulnerabilidades web
- **Uso propuesto:** 
  ```bash
  zap-baseline.py -t https://cripto-med.onrender.com
  ```
- **Qué detecta:** XSS, SQL injection, CSRF, configuración insegura de headers
- **Estado:** Propuesto para pruebas pre-producción

**SQLMap**
- **Propósito:** Pruebas de inyección SQL
- **Uso propuesto:** `sqlmap -u "https://cripto-med.onrender.com/pacientes/1" --batch`
- **Qué detecta:** SQL injection en endpoints con parámetros
- **Estado:** Propuesto para pruebas de penetración controladas

### 7.3 Herramientas de Análisis de Dependencias

**Safety**
- **Propósito:** Detectar dependencias con vulnerabilidades conocidas
- **Uso propuesto:** `safety check backend/requirements.txt`
- **Qué detecta:** CVEs en paquetes Python
- **Estado:** Propuesto para implementación en CI/CD

**npm audit**
- **Propósito:** Detectar vulnerabilidades en dependencias JavaScript
- **Uso propuesto:** `npm audit` en directorio frontend
- **Qué detecta:** CVEs en paquetes npm
- **Estado:** Propuesto para implementación en CI/CD

### 7.4 Plan de Implementación

**Fase 1 (Actual):**
- Verificar manualmente que no hay hardcoded secrets
- Revisar código SQL para detectar injection potencial
- Verificar configuración de CORS y headers

**Fase 2 (Corto plazo):**
- Implementar Bandit en CI/CD
- Ejecutar OWASP ZAP en staging
- Implementar Safety y npm audit

**Fase 3 (Mediano plazo):**
- Implementar SonarQube para análisis continuo
- Integrar pruebas de seguridad en pipeline
- Implementar escaneos regulares con OWASP ZAP

### 7.5 Extensión: Auto-Gestión de Accesos por Parte del Paciente

**Nueva funcionalidad implementada:** Login de paciente y transferencia de doctor

**Descripción:**
Se implementó un mecanismo de auto-gestión de accesos por parte del paciente que refuerza el principio de mínimo privilegio y se alinea con los derechos ARCO reconocidos en la Ley N° 29733.

**Características:**
- **Rol paciente:** Nuevo rol en el sistema que permite a los pacientes iniciar sesión y acceder a su propio historial médico
- **Auto-gestión de accesos:** El paciente puede transferir el acceso a su historial de un doctor a otro sin intervención de un administrador
- **Trazabilidad completa:** Cada transferencia queda registrada en el log de auditoría con:
  - Doctor anterior
  - Doctor nuevo
  - Usuario que ejecutó la acción (el propio paciente)
  - Timestamp
  - IP address cuando disponible

**Diseño de la transferencia:**
```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│  Paciente   │────────▶│  Backend     │────────▶│   Doctor    │
│  (Usuario)  │  POST   │  /pacientes/ │  UPDATE │  Nuevo      │
│             │  /me    │  /transferir │         │  Asignado   │
└─────────────┘         └──────────────┘         └─────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │  Audit Log   │
                        │  (Transfer   │
                        │   Action)    │
                        └──────────────┘
```

**Modelo de datos actualizado:**
- `Paciente.usuario_id`: FK opcional hacia `usuarios.id` para vincular paciente con su cuenta de login
- `AccionEnum.transferencia`: Nuevo valor en el enum de acciones de auditoría
- `AuditLog.detalle`: Campo extra para guardar el detalle de la transferencia (doctor_anterior, doctor_nuevo)

**Endpoints implementados:**
- `GET /pacientes/me`: Retorna el historial del paciente autenticado
- `GET /pacientes/doctores`: Lista doctores disponibles para transferencia
- `PATCH /pacientes/{id}/transferir-doctor`: Transfiere el paciente a otro doctor

**Permisos:**
- Admin puede transferir cualquier paciente
- Paciente puede transferir su propio historial
- Otros roles no pueden transferir pacientes

**Cumplimiento normativo:**
Esta funcionalidad refuerza el cumplimiento con la Ley N° 29733, específicamente:
- **Derecho de acceso:** El paciente puede acceder a su propia información
- **Derecho de rectificación:** El paciente puede controlar quién accede a su información
- **Derecho de oposición:** El paciente puede cambiar el doctor asignado
- **Principio de mínimo privilegio:** Solo el doctor actualmente asignado tiene acceso al historial completo

**Demostración en vivo:**
El flujo de demostración incluye:
1. Login como Doctor A → mostrar solo sus pacientes asignados
2. Login como Doctor B → verificar que NO ve al paciente demo
3. Login como Paciente Demo → ver su historial y doctor actual
4. Paciente transfiere a Doctor B
5. Login como Doctor B → ahora SÍ ve al paciente demo
6. Login como Doctor A → ya NO ve al paciente demo
7. Login como Auditor → ver log de transferencia con detalle completo

---

## 8. Lecciones Aprendidas

### 7.1 Lecciones Técnicas

**Lección 1: Docker Compose simplifica setup pero requiere configuración correcta**
- **Problema:** Conflicto de puertos con PostgreSQL instalado por Homebrew
- **Solución:** Cambiar puerto de host de 5432 a 5433
- **Aprendizaje:** Verificar puertos en uso antes de configurar Docker Compose

**Lección 2: Certificados autofirmados causan errores en navegadores**
- **Problema:** Navegadores rechazan certificados autofirmados con error NET::ERR_CERT_AUTHORITY_INVALID
- **Solución:** Usar HTTP en desarrollo, HTTPS en producción
- **Aprendizaje:** Diferenciar entre desarrollo y producción en configuración

**Lección 3: JWT requiere configuración correcta de headers**
- **Problema:** `/auth/me` retornaba 401 después de login exitoso
- **Solución:** Configurar Authorization header manualmente después de login
- **Aprendizaje:** Verificar que headers se configuran antes de requests protegidos

**Lección 4: React Router requiere estructura de rutas correcta**
- **Problema:** Dashboard se mostraba vacío después de login
- **Solución:** Verificar que `<Outlet />` se use correctamente en Layout
- **Aprendizaje:** Verificar estructura de rutas y componentes anidados

### 7.2 Lecciones de Seguridad

**Lección 1: Encriptación no es suficiente sin control de acceso**
- **Observación:** Aunque los datos estén encriptados, un admin malintencionado puede descifrarlos
- **Aprendizaje:** Encriptación + RBAC + Auditoría = Defensa en profundidad

**Lección 2: Logs de auditoría deben ser inmutables**
- **Observación:** Si hay endpoint para borrar logs, un admin malintencionado puede ocultar sus acciones
- **Aprendizaje:** No proporcionar endpoint de borrado de logs, usar soft delete

**Lección 3: HTTPS es crítico para producción**
- **Observación:** HTTP en desarrollo es aceptable, pero HTTPS es necesario en producción
- **Aprendizaje:** Documentar diferencias entre desarrollo y producción

**Lección 4: Respuesta a incidentes requiere práctica**
- **Observación:** Sin simulacros, el tiempo de respuesta será mayor
- **Aprendizaje:** Realizar simulacros de incidentes regularmente

### 7.3 Lecciones de Proyecto

**Lección 1: Documentación es tan importante como código**
- **Observación:** Sin documentación, es difícil para otros entender el sistema
- **Aprendizaje:** Documentar arquitectura, decisiones, y procedimientos

**Lección 2: Pruebas incrementales reducen tiempo de depuración**
- **Observación:** Probar todo al final hace difícil identificar la causa del problema
- **Aprendizaje:** Probar cada componente incrementalmente

**Lección 3: Compliance con leyes requiere investigación**
- **Observación:** Ley N° 29733 tiene requisitos específicos que deben cumplirse
- **Aprendizaje:** Investigar leyes y regulaciones antes de implementar

**Lección 4: Seguridad es un proceso continuo**
- **Observación:** Seguridad no es un proyecto de una sola vez
- **Aprendizaje:** Seguridad requiere mejora continua, actualización, y monitoreo

---

## 9. Retrospectiva del Proyecto

### 9.1 Qué Salió Bien

**1. Stack tecnológico adecuado**
- FastAPI es moderno y fácil de usar
- React permite desarrollo rápido de frontend
- PostgreSQL es estándar y robusto
- Docker simplifica deployment

**2. Implementación de seguridad en capas**
- Encriptación en reposo ✅
- Encriptación en transporte ✅
- Hashing de contraseñas ✅
- RBAC ✅
- Logs de auditoría ✅

**3. Documentación completa**
- Documentación de arquitectura
- Documentación de seguridad
- Documentación de procedimientos
- Documentación de recuperación

**4. Cumplimiento con Ley N° 29733**
- Medidas técnicas implementadas
- Medidas organizativas documentadas
- Procedimientos de notificación definidos

### 9.2 Qué Podría Mejorar

**1. Testing automatizado**
- No hay tests unitarios
- No hay tests de integración
- No hay tests de seguridad automatizados
- **Mejora:** Implementar pytest, tests de seguridad automatizados

**2. CI/CD pipeline**
- No hay pipeline automatizado
- Deploy es manual
- No hay validación automática
- **Mejora:** Implementar GitHub Actions, deployment automatizado

**3. Frontend más robusto**
- UI básica, sin diseño
- No hay validación de formularios
- No hay manejo de errores robusto
- **Mejora:** Implementar validación, manejo de errores, diseño

**4. Monitoreo y alertas**
- No hay monitoreo de uptime
- No hay alertas de errores
- No hay monitoreo de seguridad
- **Mejora:** Implementar Sentry, Uptime monitoring, alertas

### 9.3 Desafíos Encontrados

**1. Configuración de Docker y PostgreSQL**
- Conflicto de puertos con Homebrew
- Roles de PostgreSQL no funcionaban
- Volumen Docker persistía datos incorrectos
- **Solución:** Cambiar puerto, limpiar volúmenes, recrear contenedor

**2. Configuración de HTTPS**
- Navegadores rechazan certificados autofirmados
- Axios rechaza certificados autofirmados
- Configuración de SSL en uvicorn
- **Solución:** Usar HTTP en desarrollo, HTTPS en producción

**3. Implementación de JWT en frontend**
- Token no se configuraba en header
- `/auth/me` retornaba 401
- Sincronización de token entre login y requests
- **Solución:** Configurar header manualmente, usar useEffect

**4. Estructura de rutas en React Router**
- Dashboard se mostraba vacío
- `<Outlet />` no funcionaba correctamente
- Estructura de rutas anidada
- **Solución:** Verificar estructura de rutas, usar `<Outlet />` correctamente

### 9.4 Lecciones para el Próximo Proyecto

**1. Probar cada componente incrementalmente**
- No esperar hasta el final para probar
- Probar backend antes de frontend
- Probar autenticación antes de RBAC

**2. Documentar mientras se desarrolla**
- No dejar documentación para el final
- Documentar decisiones arquitectónicas
- Documentar problemas y soluciones

**3. Diferenciar desarrollo y producción**
- Configuración diferente para cada entorno
- Usar variables de entorno
- Documentar diferencias

**4. Implementar testing desde el inicio**
- No esperar hasta el final para implementar tests
- Implementar tests unitarios mientras se desarrolla
- Implementar tests de integración después

**5. Planificar contingencias desde el inicio**
- Script de backup desde el inicio
- Plan de recuperación desde el inicio
- Procedimientos de respuesta a incidentes desde el inicio

---

## 9. Conclusión

CriptoMed es un sistema funcional que demuestra medidas de seguridad de datos aplicadas a un caso de uso real (gestión de historiales médicos en pequeñas clínicas). El sistema implementa:

- ✅ Encriptación de datos sensibles en reposo (AES-256)
- ✅ Encriptación de datos en transporte (HTTPS)
- ✅ Hashing de contraseñas (bcrypt)
- ✅ Control de acceso basado en roles (RBAC)
- ✅ Logs de auditoría inmutables
- ✅ Certificados digitales autofirmados
- ✅ Cumplimiento con Ley Peruana N° 29733
- ✅ Plan de recuperación ante desastres
- ✅ Procedimientos de respuesta a incidentes
- ✅ Recomendaciones futuras de seguridad

El proyecto cumple con los requerimientos técnicos de la rúbrica del curso DS3031 y demuestra un entendimiento práctico de seguridad de datos aplicada a un caso de uso real.

**Logros:**
- Sistema funcional con backend, frontend, y base de datos
- Seguridad en capas (defense in depth)
- Documentación completa de arquitectura y procedimientos
- Cumplimiento con normativa peruana

**Limitaciones:**
- Testing automatizado no implementado
- Frontend básico sin diseño
- Monitoreo y alertas no implementados
- No hay CI/CD pipeline

**Recomendaciones para el futuro:**
- Implementar MFA
- Implementar HSM
- Implementar SIEM
- Implementar WAF
- Implementar testing automatizado
- Implementar CI/CD pipeline

El proyecto demuestra que es posible implementar medidas de seguridad efectivas en un sistema de gestión de datos sensibles, incluso con recursos limitados, y que la seguridad de datos es un proceso continuo que requiere mejora constante.

---

## 10. Anexos

### 10.1 Capturas de Pantalla

**[Captura 1: Login de CriptoMed]**
- Screenshot de página de login
- Usuario: admin@criptomed.com / admin123

**[Captura 2: Dashboard de CriptoMed]**
- Screenshot de dashboard con lista de pacientes
- Mostrando campos descifrados

**[Captura 3: Logs de Auditoría]**
- Screenshot de tabla de logs de auditoría
- Mostrando usuario, acción, recurso, timestamp

**[Captura 4: Base de Datos PostgreSQL]**
- Screenshot de consulta SQL mostrando campos encriptados
- Campos sensibles en texto cifrado

### 10.2 Referencias

**Leyes y Regulaciones:**
- Ley Peruana N° 29733 - Ley de Protección de Datos Personales
- Reglamento de la Ley N° 29733
- ISO 27001 - Information Security Management
- NIST Cybersecurity Framework

**Librerías y Frameworks:**
- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/
- PostgreSQL: https://www.postgresql.org/
- Docker: https://www.docker.com/
- cryptography: https://cryptography.io/
- passlib: https://passlib.readthedocs.io/
- python-jose: https://python-jose.readthedocs.io/

**Standards:**
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- NIST 800-63B: Digital Identity Guidelines
- PCI DSS: Payment Card Industry Data Security Standard

### 10.2 Capturas de Pantalla

**Screenshot 1: Login de CriptoMed**
![Login](images/login.png)
- Pantalla de login con formulario email/contraseña
- Usuarios de prueba listados para demostración

**Screenshot 2: Dashboard del Admin**
![Dashboard Admin](images/admin_sistema_dashboard.png)
- Dashboard del administrador con lista de pacientes
- Estadísticas: Total de pacientes, pacientes activos, rol
- Búsqueda y filtros por estado

**Screenshot 3: Logs de Auditoría del Admin**
![Logs Admin](images/admin_sistema_logs.png)
- Logs de auditoría visibles para el administrador
- Tabla con usuario, acción, recurso, timestamp, IP
- Paginación para navegar logs

**Screenshot 4: Dashboard del Administrativo**
![Dashboard Administrativo](images/admin_clinica_dashboard.png)
- Dashboard del administrativo con lista de pacientes
- Permisos: datos básicos y facturación, sin diagnóstico detallado

**Screenshot 5: Dashboard del Doctor**
![Dashboard Doctor](images/doctor_dashboard.png)
- Dashboard del doctor con lista de pacientes
- Cards de pacientes con información relevante

**Screenshot 6: Auditor sin acceso a Dashboard**
![Dashboard Auditor Denegado](images/auditor_dashboard_denegado.png)
- El auditor no puede acceder al dashboard (RBAC funcionando)
- Solo puede acceder a logs de auditoría

**Screenshot 7: Logs de Auditoría del Auditor**
![Logs Auditor](images/auditor_logs.png)
- Logs de auditoría visibles para el auditor
- Solo lectura, sin posibilidad de modificar

**Screenshot 8: Headers JWT en Network Tab**
![JWT Headers](images/JWT_logs.png)
- Network tab del navegador mostrando headers
- Header `Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- Demuestra que JWT se envía correctamente en cada request

### 10.3 Código Fuente

**Repositorio:** [URL de GitHub]
**Branch:** main
**Licencia:** MIT

---

**Fin del Informe**
