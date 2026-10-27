# Hardening Docker - CriptoMed

Este documento describe las medidas de hardening implementadas en el despliegue Docker de CriptoMed, basadas en el CIS Docker Benchmark, OWASP Docker Security Cheat Sheet y OWASP ASVS.

## Tabla de Controles de Hardening

| Control | Cómo se implementa (archivo y línea) | Riesgo que reduce | Referencia |
|---------|--------------------------------------|-----------------|------------|
| **Usuario no root** | `docker/backend/Dockerfile` línea 23-30: Creación de usuario `app` (UID 10001) y cambio a ese usuario | Ejecución de código con privilegios elevados si el contenedor es comprometido | CIS Docker Benchmark 4.1, OWASP Docker Security Cheat Sheet |
| **no-new-privileges** | `docker-compose.yml` líneas 19-20, 71-72, 139-140: `security_opt: [no-new-privileges:true]` en db, backend e init | Escalación de privilegios vía setuid/setgid binaries | CIS Docker Benchmark 5.2 |
| **cap_drop ALL** | `docker-compose.yml` líneas 21-22, 73-74, 141-142: `cap_drop: [ALL]` en db, backend e init | Exposición innecesaria de capacidades del kernel Linux | CIS Docker Benchmark 5.26 |
| **Capacidades mínimas** | `docker-compose.yml` líneas 24-32 (db): CHOWN, DAC_OVERRIDE, FOWNER, FSETID, KILL, SETGID, SETUID, SYS_CHROOT; líneas 76-77 (backend): NET_BIND_SERVICE; líneas 144-145 (init): NET_BIND_SERVICE | Ejecución con capacidades innecesarias si se usa `cap_drop: ALL` sin añadir las necesarias | CIS Docker Benchmark 5.26 |
| **Sistema de archivos de solo lectura** | `docker-compose.yml` línea 78 (backend): `read_only: true`; línea 146 (init): `read_only: true` | Modificación de archivos binarios o configuración si el contenedor es comprometido | CIS Docker Benchmark 5.15, OWASP Docker Security Cheat Sheet |
| **Redes internas** | `docker-compose.yml` línea 160: `db_net: internal: true` para base de datos | Exposición no autorizada de base de datos a otros contenedores o al host | CIS Docker Benchmark 5.8, OWASP ASVS V6.2.1 |
| **Único puerto publicado** | `docker-compose.yml` línea 91: Solo edge publica puerto `8443:8443`; db y backend no tienen `ports` | Exposición de puertos internos (5432, 8000) al host | CIS Docker Benchmark 5.11, OWASP ASVS V6.2.1 |
| **Imágenes con versión fija** | `docker-compose.yml` línea 3: `postgres:16-alpine`; `docker/backend/Dockerfile` línea 2: `python:3.12.7-slim`; `docker/edge/Dockerfile` líneas 3, 20: `node:20.19.0-alpine`, `nginx:1.27-alpine` | Actualizaciones automáticas que introduzcan vulnerabilidades o cambios incompatibles | CIS Docker Benchmark 4.4, OWASP Docker Security Cheat Sheet |
| **Multi-stage build** | `docker/edge/Dockerfile` líneas 1-19: Etapa `builder` con Node.js, etapa final con Nginx (solo frontend compilado) | Inclusión de herramientas de build y dependencias innecesarias en la imagen final | CIS Docker Benchmark 4.5, OWASP Docker Security Cheat Sheet |
| **Sin secretos en imágenes** | `docker/backend/Dockerfile` y `docker/edge/Dockerfile`: No hay `COPY .env` ni secretos hardcodeados; variables de entorno vía `docker-compose.yml` líneas 46-58 | Exposición de secretos si la imagen es comprometida o compartida (ej: en Docker Hub) | CIS Docker Benchmark 4.1, OWASP ASVS V7.2.1 |
| **Healthchecks** | `docker-compose.yml` líneas 12-16 (db): `pg_isready`; líneas 62-67 (backend): health endpoint `/health` | Contenedores zombies que no responden pero consumen recursos | CIS Docker Benchmark 6.1, OWASP Docker Security Cheat Sheet |
| **Límites de recursos** | `docker-compose.yml` líneas 37-38 (db): `mem_limit: 512m`, `pids_limit: 100`; líneas 81-82 (backend): `mem_limit: 256m`, `pids_limit: 50`; líneas 115-116 (edge): `mem_limit: 128m`, `pids_limit: 30`; líneas 149-150 (init): `mem_limit: 256m`, `pids_limit: 50` | Consumo excesivo de recursos que afecta otros contenedores o el host (DoS) | CIS Docker Benchmark 5.17, OWASP Docker Security Cheat Sheet |
| **Certificados como volumen de solo lectura** | `docker-compose.yml` línea 93: `./certs:/etc/nginx/certs:ro` | Modificación de certificados TLS si el contenedor es comprometido | OWASP Docker Security Cheat Sheet |
| **Tmpfs para directorios temporales** | `docker-compose.yml` líneas 34-36 (db): tmpfs en `/tmp`, `/var/run/postgresql`; líneas 79-80 (backend): tmpfs en `/tmp`; líneas 147-148 (init): tmpfs en `/tmp` | Escritura de datos temporales en disco persistente (puede contener información sensible) | CIS Docker Benchmark 5.15 |

## Limitaciones

- **Secretos en variables de entorno:** Los secretos (JWT_SECRET, ENCRYPTION_KEY, POSTGRES_PASSWORD) se pasan como variables de entorno en `docker-compose.yml`. En producción, deberían usarse Docker Secrets o un gestor de secretos (ej: HashiCorp Vault, AWS Secrets Manager) para evitar exposición en `docker inspect` o logs. (OWASP ASVS V7.2.1)

- **Certificado autofirmado:** El certificado TLS en `certs/cert.pem` es autofirmado. Esto es aceptable para demos y desarrollo, pero en producción debería usarse un certificado emitido por una CA confiable (ej: Let's Encrypt) para evitar advertencias del navegador y asegurar la confianza del usuario. (OWASP ASVS V8.3.1)

- **Sin escaneo continuo de imágenes:** Las imágenes base (`python:3.12.7-slim`, `nginx:1.27-alpine`, `postgres:16-alpine`) no se escanean continuamente con herramientas como Trivy o Snyk. En producción, debería implementarse un pipeline CI/CD que escanee vulnerabilidades en las imágenes antes del despliegue. (CIS Docker Benchmark 4.6)

- **Volumen de base de datos no cifrado en disco:** El volumen `pgdata` no está cifrado a nivel de disco. Esto es mitigado parcialmente por el cifrado de campos sensibles a nivel de aplicación (AES-256 con Fernet), pero si un atacante obtiene acceso al disco físico, podría extraer datos sin cifrar (ej: nombres, emails, estructura de la base de datos). En producción, debería usarse cifrado a nivel de volumen (ej: LUKS en Linux, cifrado de EBS en AWS) o base de datos con cifrado nativo (ej: AWS RDS Encryption at Rest). (OWASP ASVS V6.2.3)

- **Endurecimiento desactivado en edge:** Los controles de hardening (`no-new-privileges`, `cap_drop`, `read_only`, tmpfs) están comentados en el servicio `edge` (líneas 99-114) debido a problemas de permisos con la imagen estándar de nginx. Esto deja el edge menos endurecido que backend y db. En producción, debería usarse la imagen `nginxinc/nginx-unprivileged` o ajustar la configuración para aplicar el endurecimiento completo. (CIS Docker Benchmark 5.15, 5.26)

- **Capacidades innecesarias en PostgreSQL:** PostgreSQL requiere capacidades específicas (CHOWN, DAC_OVERRIDE, FOWNER, FSETID, KILL, SETGID, SETUID, SYS_CHROOT) que podrían ser excesivas para algunas operaciones. En un entorno de producción de alto riesgo, debería evaluarse si es posible restringir aún más estas capacidades. (CIS Docker Benchmark 5.26)
