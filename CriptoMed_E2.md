**CriptoMed**  
Entrega 2 \- Guía paso a paso con prompts para tu IDE con IA

Proyecto de Ética y Seguridad de los Datos \- DS3031

Cada tarea de la Entrega 2 está escrita como un mini prompt que copias y pegas en la IA de tu IDE. Los pasos que solo puedes hacer tú (Notion, rotar contraseñas, grabar el video) están en cuadros amarillos.

## **Cómo usar este documento**

- **Primero** pega el PROMPT 0 (contexto) al abrir una sesión nueva en tu IDE. Si la IA pierde el hilo, vuelve a pegarlo.

- **Después** ve en orden: cada paso tiene un cuadro **gris** (prompt para copiar), a veces uno **amarillo** (lo haces tú) y uno **verde** (qué verificar antes de seguir).

- **Revisa el diff** antes de aceptar cambios de la IA y haz un commit por paso (por ejemplo: git commit \-m "paso 1.1 AES-GCM").

- Si la IA responde con algo que suena a estándar o artículo de ley que no está en la lista del PROMPT 0, **desconfía**: pídele la fuente o márcalo como \[VERIFICAR\]. El profesor ya mostró que revisa las justificaciones.

- Para Google Docs: sube este archivo a Drive y ábrelo con Documentos de Google, o copia y pega cada cuadro directamente.

- Si te falta tiempo, mira el Anexo C (qué recortar y qué nunca recortar).

- **Todo corre en Docker.** El profesor aceptó despliegue local, así que el sistema que se evalúa es el que levanta con docker compose up. Haz la Fase D (Docker) justo después de la Fase 0, antes de tocar la criptografía: así todos los scripts, escaneos y la demo corren dentro de contenedores y no dependen de lo que tengas instalado en tu equipo.

## **Qué te pidió el profesor y dónde se resuelve**

| Comentario del profesor (E1: 17/20) | Qué se hace | Paso |
| :---- | :---- | :---- |
| Fernet es AES-128-CBC \+ HMAC, no AES-256 | Migrar a AES-256-GCM (NIST SP 800-38D) | 1.1 |
| ¿Cómo se rota la llave? | Llaves versionadas \+ script de re-cifrado \+ demo en vivo | 1.2 y 5.4 |
| "ARDA": ¿quisieron decir ANPD? | Sí: Autoridad Nacional de Protección de Datos Personales | 0.3 |
| Estándares sin fuente; descripciones que mandan a un markdown | Tabla decisión → estándar; todo explicado dentro del informe | 4.1 a 4.9 y Anexo A |
| Parecía que Fernet no tenía integridad | Con GCM la integridad es explícita (tag de autenticación) | 1.1 y 4.2 |
| Informe largo, parece lista de requisitos | Reescribir como narrativa de diseño; requisitos al anexo | Fase 4 |

## **Qué es nuevo en la Entrega 2**

| Requisito E2 | Paso(s) |
| :---- | :---- |
| Aplicar una herramienta de análisis de seguridad (en E1 solo se describía) | Fase 2 |
| DPIA (Evaluación de Impacto en la Protección de Datos) | Fase 3 |
| Sección de consideraciones éticas y de privacidad en el informe | 3.4 y 4.7 |
| Informe: todo lo de E1 \+ lo nuevo \+ lecciones aprendidas \+ retrospectiva | Fase 4 |
| Demostración en vivo | Fase 5 |
| Presentación (resumen de E1, objetivos vs. resultados, justificar lo no logrado) | Fase 6 |
| Despliegue local reproducible con Docker (el profesor aceptó despliegue local) | Fase D |

# ✅ **PROMPT 0 \- Contexto (pégalo primero en tu IDE)**

*Le explica a la IA qué es CriptoMed, cómo trabajar y qué no inventar. Pégalo al inicio de cada sesión nueva.*

| PROMPT PARA TU IA  (copia todo el cuadro) Eres mi asistente de desarrollo en el proyecto CriptoMed (curso DS3031 Ética y Seguridad de Datos, Entrega 2). CONTEXTO \- CriptoMed es una plataforma web para clínicas pequeñas de Perú que centraliza historiales médicos con acceso por roles, cifrado en reposo y en tránsito, y logs de auditoría. Los datos son sintéticos (Healthcare Dataset de Kaggle \+ códigos CIE-10), pero el sistema se diseña como si fueran reales. \- Stack: backend Python \+ FastAPI \+ SQLAlchemy \+ PostgreSQL; front React (Vite); JWT (python-jose); bcrypt; librería cryptography. Despliegue: LOCAL con Docker Compose (servicios: db PostgreSQL, backend FastAPI, edge Nginx con TLS que sirve el front compilado y reenvía /api al backend). Solo el edge publica un puerto (https\://localhost:8443). \- Roles: admin, doctor, administrativo, auditor, paciente. Mínimo privilegio: el administrativo NO ve diagnósticos; el doctor solo ve a sus pacientes asignados; el auditor solo ve logs; el paciente solo ve lo suyo y puede transferir su historial a otro doctor. \- Archivos principales: backend/app/{main,database,models,schemas,auth,rbac,crypto,audit}.py, backend/app/routers/{auth,usuarios,pacientes,audit\_logs}.py, backend/scripts/{setup\_db,seed\_db,verificar\_cifrado,verificar\_logs}.py, frontend/src/... REGLAS DE TRABAJO 1\. Antes de modificar, lee los archivos relevantes y dime en pocas líneas qué vas a cambiar. 2\. Haz cambios mínimos y enfocados en el paso pedido. No refactorices lo que no te pida. 3\. Nunca escribas secretos reales en código, docs ni ejemplos. Usa .env (ignorado por git) y .env.example con valores falsos. 4\. Si cambias el modelo de datos, actualiza setup\_db.py y seed\_db.py y dime cómo recrear la base (en desarrollo puedo borrarla y volver a sembrar). 5\. Escribe o actualiza pruebas (pytest) para lo que cambies y ejecútalas. Si no puedes ejecutar algo, dímelo en lugar de asumir que funciona. 6\. No inventes estándares, RFC, artículos de ley ni cifras. Solo puedes citar de esta lista: FIPS 197; NIST SP 800-38D; NIST SP 800-57 Part 1; NIST SP 800-63B; NIST SP 800-52 Rev. 2; NIST SP 800-92; NIST SP 800-61; RFC 8446 (TLS 1.3); RFC 7519 y RFC 8725 (JWT); OWASP Password Storage Cheat Sheet; OWASP Logging Cheat Sheet; OWASP ASVS; CIS Docker Benchmark; OWASP Docker Security Cheat Sheet; GDPR art. 35; ISO/IEC 29134; HIPAA Security Rule 45 CFR 164.312; Ley 29733 y su Reglamento (D.S. 016-2024-JUS); ANPD. Si algo no está en la lista, escribe \[VERIFICAR\] en vez de afirmarlo. 7\. Al terminar cada paso entrégame: (a) archivos modificados, (b) comandos exactos para probarlo, (c) riesgos o limitaciones que quedaron. 8\. Todo corre en Docker: ejecuta los scripts de Python con docker compose run \--rm backend ..., usa docker compose exec db psql ... para la base de datos y no asumas Python, Node, Postgres ni herramientas de escaneo instalados en mi equipo. Nunca expongas puertos de db ni backend al host. Responde solo "listo" y espera mi primer paso. |
| :---- |

# ✅ **FASE 0 \- Triage (1 a 2 horas)**

*Antes de agregar nada nuevo: sacar secretos expuestos y arreglar inconsistencias que el profesor puede notar.*

### **Paso 0.1 \- Auditar y sacar los secretos del repo**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 0.1 \- Secretos Audita el repositorio buscando secretos: contraseñas de base de datos, JWT\_SECRET, claves de cifrado, llaves privadas (\*.pem), tokens. Revisa también el historial de git (git log \-p) y los archivos de documentación (\*.md). Haz lo siguiente: 1\. Lista cada hallazgo (archivo, línea, tipo) SIN imprimir el valor completo del secreto. 2\. Asegura que .gitignore incluya: .env, .env.\*, \!.env.example, certs/, \*.pem, \*.key, \*.db, backups/, \*.gpg, reports/ (si contienen datos sensibles). 3\. Crea backend/.env.example con TODAS las variables que usa la app, con valores falsos (ej. JWT\_SECRET=cambia-esto). 4\. En README, SETUP\_GUIDE.md y cualquier otro documento, reemplaza credenciales reales por referencias a .env.example. 5\. Crea scripts/generate\_secrets.py que imprima un JWT\_SECRET nuevo (secrets.token\_hex(32)) y una contraseña aleatoria para Postgres, SIN escribirlos a disco. 6\. Si hay secretos en el historial de git, dime los pasos exactos (git filter-repo o recrear el repo limpio), pero NO ejecutes nada destructivo sin mi confirmación. |
| :---- |

| TÚ (MANUAL, sin prompt) 1\. Genera secretos nuevos con scripts/generate\_secrets.py y actualiza tu .env local. 2\. Cambia la contraseña del usuario de Postgres (ALTER USER ... PASSWORD ...) y actualiza DATABASE\_URL. 3\. Pon los valores nuevos solo en tu .env local (el despliegue será local con Docker; ver Fase D). 4\. Borra los valores viejos (JWT\_SECRET, ENCRYPTION\_KEY, contraseña de Postgres) de tu Notion y de cualquier documento compartido con el profesor. Esos valores quedan quemados: no los reutilices. |
| :---- |

### **Paso 0.2 \- Escanear secretos con gitleaks (evidencia para la Fase 2\)**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 0.2 \- gitleaks Instala o ejecuta gitleaks (usa Docker si es lo más simple en mi sistema) sobre todo el repositorio, incluido el historial. Guarda el reporte JSON en reports/before/gitleaks.json y dime cuántos hallazgos hay y de qué tipo. No muestres los valores de los secretos. Si hay hallazgos, propón cómo resolverlos (rotar, limpiar historial) y espera mi confirmación. |
| :---- |

### **Paso 0.3 \- Alinear el rol Administrativo (el servidor decide, no el front)**

*En tu informe E1 la tabla decía que Administrativo ve diagnósticos y la sección de seguridad decía que no. Decisión recomendada: NO los ve.*

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 0.3 \- Rol administrativo Decisión de diseño: el rol administrativo NO puede ver diagnostico, codigo\_cie10, medicacion ni resultado\_test (sí puede ver datos básicos y facturación). 1\. Revisa rbac.py, schemas.py (las respuestas de paciente por rol), routers/pacientes.py y el front. 2\. Asegura que el filtrado ocurra EN EL BACKEND: para el rol administrativo esos campos no deben salir en la respuesta JSON (no basta con ocultarlos en el front). 3\. El doctor solo accede a pacientes con doctor\_id igual a su usuario; el paciente solo a su propio registro; el auditor a ningún paciente. 4\. Agrega pruebas parametrizadas por rol que llamen a GET /pacientes y GET /pacientes/{id} y verifiquen qué campos aparecen y qué códigos HTTP se devuelven (200/403/404). |
| :---- |

| VERIFICA ANTES DE SEGUIR Entra con cada rol y confirma con la pestaña Network del navegador que, para Administrativo, el JSON realmente no contiene el diagnóstico. |
| :---- |

### **Paso 0.4 \- Correcciones del informe en Notion**

| TÚ (MANUAL, sin prompt) Haz estas correcciones en  1\. Busca "ARDA" y reemplázalo por "ANPD (Autoridad Nacional de Protección de Datos Personales)". 2\. Tabla de roles: Administrativo "no ve diagnósticos médicos detallados". 3\. Frase del ransomware: cambia "el 67% de los ataques al sector salud en 2024 involucraron ransomware" por "el 67% de las organizaciones de salud sufrió ataques de ransomware en 2024". Antes de usar la cifra, ábrela en la fuente original (IBM u otra) y confirma el número y el año. 4\. Tabla de riesgos: borra la fila duplicada de "Fuga de historiales médicos \- Pacientes". 5\. Borra notas sueltas del tipo "necesito verificar si tiene properties computadas". 6\. Plan de incidentes: agrega el paso "Notificar a la ANPD dentro de las 48 horas de tomar conocimiento del incidente e informar a los titulares afectados (Reglamento de la Ley 29733, D.S. 016-2024-JUS). Si el incidente es en un entorno digital, reportar también al Centro Nacional de Seguridad Digital." Antes de citar números de artículo, ábrelos en el texto oficial publicado en El Peruano. 7\. Política de contraseñas: reemplázala por el texto del Anexo B (alineado a NIST SP 800-63B). |
| :---- |

# ✅ **FASE D \- Despliegue local con Docker (4 a 5 horas)**

*El profesor indicó que el despliegue puede ser local. Entonces el sistema que se evalúa es el que levanta con un solo comando: docker compose up. Además de cumplir la consigna, Docker te da reproducibilidad (cualquiera lo corre igual), aislamiento (la base de datos no queda expuesta) y buenos argumentos de seguridad para el informe. Haz esta fase ANTES de la Fase 1: así todo lo demás (migraciones, scripts, escaneos, demo) corre dentro de contenedores.*

## **Arquitectura objetivo**

| Servicio | Imagen base | ¿Expuesto al host? | Redes | Función |
| :---- | :---- | :---- | :---- | :---- |
| edge | nginx-unprivileged | Sí: https\://localhost:8443 | app\_net | Termina TLS 1.3, sirve el front compilado y reenvía /api al backend |
| backend | python:3.12-slim | No | app\_net y db\_net | FastAPI con uvicorn (HTTP solo dentro de la red interna) |
| db | postgres:16 | No | db\_net (interna) | PostgreSQL; sin acceso desde el host ni salida a internet |
| init (perfil seed) | la del backend | No | db\_net | Crea tablas, roles de BD y siembra datos sintéticos |
| herramientas (perfil tools) | varias | No | app\_net | ZAP, Bandit, gitleaks, Trivy, testssl, backups |

Decisiones de diseño que luego vas a justificar en el informe: (1) solo el edge publica un puerto; (2) db\_net es una red interna sin salida a internet; (3) los contenedores corren sin root y con capacidades mínimas; (4) las llaves, certificados y contraseñas nunca están dentro de las imágenes: llegan por .env y volúmenes de solo lectura; (5) el backend confía en el encabezado X-Forwarded-For solo porque únicamente el edge puede alcanzarlo (así los logs y el rate limiting ven la IP real del cliente).

### **Paso D.1 \- Estructura, certificados y variables**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO D.1 \- Base de Docker Todo el proyecto va a correr con Docker Compose. Detecta mi sistema operativo (o pregúntamelo una vez) y no asumas Python, Node ni Postgres instalados en mi equipo. 1\. Crea esta estructura (sin sobrescribir lo existente): docker/backend/Dockerfile, docker/edge/Dockerfile, docker/edge/nginx.conf, docker/db/init/ (scripts SQL de inicialización), docker-compose.yml, .dockerignore (en la raíz y en frontend/), y scripts/. 2\. Crea scripts/gen\_cert.sh (y gen\_cert.ps1 si uso Windows) que genere con OpenSSL un certificado autofirmado para localhost en certs/: clave RSA de 2048 bits o EC P-256, validez de 365 días, con subjectAltName DNS:localhost, IP:127.0.0.1 (los navegadores modernos ignoran el CN y exigen SAN). Salida: certs/cert.pem y certs/key.pem. certs/ debe estar en .gitignore. Si OpenSSL no está en mi equipo, ejecútalo con un contenedor (por ejemplo la imagen alpine/openssl). 3\. Crea .env.example en la raíz con TODAS las variables que consume docker-compose.yml, con valores falsos: POSTGRES\_DB, POSTGRES\_USER, POSTGRES\_PASSWORD, APP\_DB\_USER, APP\_DB\_PASSWORD, DATABASE\_URL (usando el host "db"), JWT\_SECRET, JWT\_ALGORITHM, JWT\_EXPIRE\_MINUTES, ENC\_KEYS, ENC\_KEY\_CURRENT, ALLOWED\_ORIGINS=https\://localhost:8443, ENV, BACKUP\_PASSPHRASE y DEMO\_PASSWORD\_\*. 4\. Extiende scripts/generate\_secrets.py (del paso 0.1) para que genere un .env completo a partir de .env.example con secretos aleatorios, sin imprimirlos en consola, y se niegue a sobrescribir un .env existente salvo con \--force. 5\. El frontend debe llamar a la API con la ruta relativa /api (variable VITE\_API\_URL=/api), no a una URL absoluta. Ajusta el código del front que construye las URLs. No levantes nada todavía; muéstrame el resumen de archivos creados. |
| :---- |

### **Paso D.2 \- Dockerfile del backend**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO D.2 \- Imagen del backend Escribe docker/backend/Dockerfile para el backend FastAPI con buenas prácticas de seguridad: \- Base python:3.12-slim fijada a una versión menor concreta (no "latest"). \- Compilación en una etapa (multi-stage) para que la imagen final no lleve compiladores ni caches de pip; instala dependencias con pip \--no-cache-dir desde backend/requirements.txt. \- Usuario no root (crea el usuario "app" con UID 10001\) y WORKDIR /app. Copia solo backend/app y backend/scripts (usa .dockerignore para excluir .env, certs, tests, .git, \_\_pycache\_\_, reports). \- Sin secretos en la imagen: no uses COPY de .env ni ARG/ENV con valores secretos. \- HEALTHCHECK que llame a un endpoint /health (créalo en main.py si no existe, sin datos sensibles y sin requerir autenticación; no debe quedar registrado en audit\_logs). \- Comando: uvicorn app.main:app \--host 0.0.0.0 \--port 8000 \--proxy-headers \--forwarded-allow-ips="\*" (comenta por qué "\*" es aceptable: el puerto 8000 NO se publica al host, solo el edge puede alcanzarlo). Quita del código la lógica antigua que arrancaba uvicorn con ssl\_keyfile: ahora el TLS lo termina el edge. \- Verifica que la IP registrada en audit\_logs.ip\_origen y la que usa slowapi sea la del cliente real (X-Forwarded-For) y no la del contenedor del edge; agrega una prueba que lo compruebe simulando el encabezado. Muéstrame el Dockerfile y los cambios en el código. |
| :---- |

### **Paso D.3 \- Edge: Nginx con TLS 1.3 y frontend compilado**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO D.3 \- Edge Nginx \+ frontend Escribe docker/edge/Dockerfile (multi-stage) y docker/edge/nginx.conf: \- Etapa 1: node (versión LTS fija) que ejecuta npm ci y npm run build en frontend/. \- Etapa 2: nginxinc/nginx-unprivileged (versión fija) con el build copiado a /usr/share/nginx/html. Corre sin root; escucha en 8443 con TLS. \- nginx.conf: ssl\_protocols TLSv1.3 únicamente; certificado y llave leídos desde /etc/nginx/certs (se montan como volumen de solo lectura, nunca dentro de la imagen); redirección de HTTP a HTTPS si abres el puerto 8080 interno; encabezados Strict-Transport-Security, X-Content-Type-Options nosniff, X-Frame-Options DENY, Referrer-Policy no-referrer y una Content-Security-Policy para el front (default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'); server\_tokens off. \- location /api/ { proxy\_pass http\://backend:8000/; } con proxy\_set\_header X-Forwarded-For \$remote\_addr (sobrescribir, no anexar, para que el cliente no pueda falsificarlo), X-Forwarded-Proto y Host; limita el tamaño del body (client\_max\_body\_size 1m) y agrega timeouts razonables. \- Configuración de SPA: try\_files \$uri /index.html para las rutas de React Router. \- Para el backend, los encabezados de seguridad ya los pone el middleware del paso 1.6a; evita duplicarlos (decide cuáles pone cada capa y déjalo documentado en un comentario). Explícame en 5 líneas qué hace cada bloque del nginx.conf. |
| :---- |

### **Paso D.4 \- docker-compose.yml**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO D.4 \- Compose Escribe docker-compose.yml con: 1\. Servicios db, backend, edge y init (este último con profiles: \["seed"\]); y los de herramientas en profiles: \["tools"\] se agregan después (Fase 2 y backups). 2\. Redes: app\_net y db\_net con internal: true. db solo en db\_net; backend en ambas; edge solo en app\_net. SOLO edge publica puertos: "8443:8443". Ni db ni backend usan "ports". 3\. db: postgres:16 (versión fija), variables desde .env, volumen con nombre pgdata, montaje de docker/db/init en /docker-entrypoint-initdb.d (solo lectura), healthcheck con pg\_isready. 4\. backend: build con docker/backend/Dockerfile, env\_file: .env, depends\_on con condition: service\_healthy para db, healthcheck del paso D.2, restart: unless-stopped. 5\. edge: build con docker/edge/Dockerfile, volumen ./certs:/etc/nginx/certs:ro, depends\_on backend (healthy). 6\. init: reutiliza la imagen del backend con command que ejecute scripts/setup\_db.py y scripts/seed\_db.py; debe ser idempotente y terminar (restart: "no"). 7\. Endurecimiento de CADA servicio propio (no root, ya viene del Dockerfile): security\_opt: \["no-new-privileges:true"\], cap\_drop: \["ALL"\] (agrega solo las capacidades imprescindibles y justifícalas en un comentario; Postgres necesita algunas), read\_only: true con tmpfs para /tmp y los directorios que necesiten escritura, límites de memoria y de procesos (mem\_limit, pids\_limit). 8\. Sin "version:" obsoleta, sin latest, sin privileged, sin montar el socket de Docker. Después de escribirlo, ejecuta docker compose config (sin pegarme los valores de los secretos) y corrige errores. Si algún endurecimiento rompe un servicio, aflójalo solo lo necesario y deja un comentario con la razón. |
| :---- |

### **Paso D.5 \- Base de datos: roles e inicialización**

*Aquí se conecta con el paso 1.3 (rol criptomed\_app con solo INSERT y SELECT sobre audit\_logs). Si ya tienes ese SQL, se monta en docker/db/init para que se aplique solo al crear la base.*

| PROMPT PARA TU IA  (copia todo el cuadro) PASO D.5 \- Inicialización de la base 1\. Crea docker/db/init/01-roles.sh (los scripts .sh de /docker-entrypoint-initdb.d pueden leer variables de entorno) que cree el rol de aplicación APP\_DB\_USER con la contraseña APP\_DB\_PASSWORD, sin superusuario, sin CREATEDB y sin CREATEROLE, y le conceda solo CONNECT sobre la base. Los privilegios sobre tablas se otorgan al final de setup\_db.py (después de crear las tablas): SELECT, INSERT, UPDATE, DELETE sobre las tablas de negocio según el caso, y solo SELECT e INSERT sobre audit\_logs (más el trigger anti-UPDATE/DELETE del paso 1.3, cuando exista). 2\. setup\_db.py debe conectarse con el rol dueño (POSTGRES\_USER) para crear tablas y privilegios, mientras que el backend en ejecución usa APP\_DB\_USER. Ajusta DATABASE\_URL (backend) y OWNER\_DATABASE\_URL (init) en .env.example. 3\. seed\_db.py debe leer las contraseñas de DEMO\_PASSWORD\_\* y las llaves de ENC\_KEYS / ENC\_KEY\_CURRENT, ser idempotente y no imprimir secretos. 4\. Documenta en docs/DOCKER.md cómo reiniciar desde cero: docker compose down \-v (borra el volumen pgdata) seguido de docker compose \--profile seed up init. |
| :---- |

### **Paso D.6 \- Comandos de operación y README**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO D.6 \- Operación Crea scripts/dev.sh (y dev.ps1 si uso Windows) con subcomandos: up (genera certs si faltan, valida que exista .env, build y levanta en segundo plano), seed (ejecuta el perfil seed), down, reset (down \-v \+ up \+ seed), logs, ps, test (ejecuta pytest dentro del contenedor del backend con docker compose run \--rm) y shell-db (abre psql en el contenedor db). Ningún subcomando debe imprimir secretos. Actualiza el README.md con una sección "Cómo ejecutar el proyecto" de máximo 12 líneas: requisitos (Docker y Docker Compose), copiar .env.example a .env y generar secretos, generar el certificado, levantar, sembrar, abrir https\://localhost:8443, usuarios de demo (sin contraseñas, indicando de qué variable salen) y cómo aceptar el certificado autofirmado en el navegador. Quita del README cualquier mención a Render o GitHub Pages como despliegue oficial. Crea docs/DOCKER.md con: diagrama Mermaid de servicios y redes, tabla de puertos, qué volúmenes existen, qué está dentro y fuera de las imágenes, y cómo depurar (logs, healthchecks). |
| :---- |

| TÚ (MANUAL, sin prompt) \- Instala Docker Desktop (o Docker Engine \+ plugin compose) y comprueba: docker \--version y docker compose version. \- Genera el certificado y el .env, levanta con scripts/dev.sh up y luego seed. \- Abre https\://localhost:8443. El navegador mostrará una advertencia porque el certificado es autofirmado: acéptala, o para la demo importa certs/cert.pem como certificado de confianza (así no aparece la advertencia delante del profesor). \- Si usas Windows con WSL2, guarda el proyecto dentro del sistema de archivos de WSL (no en /mnt/c): los contenedores van mucho más rápido. |
| :---- |

### **Paso D.7 \- Verificación desde cero**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO D.7 \- Verificar el despliegue Crea scripts/verificar\_despliegue.sh que, con los contenedores arriba, compruebe y reporte OK o FALLA en cada punto: 1\. https\://localhost:8443 responde y el TLS negociado es 1.3 (usa openssl s\_client \-tls1\_3 y comprueba que \-tls1\_2 es rechazado). 2\. Los puertos 5432 (Postgres) y 8000 (backend) NO son accesibles desde el host. 3\. docker compose ps muestra todos los servicios en estado healthy. 4\. El login con un usuario de demo funciona a través de https\://localhost:8443/api/auth/login. 5\. Los contenedores propios corren con un usuario distinto de root (docker compose exec \<servicio\> id \-u). 6\. No existen archivos .env ni \*.pem dentro de las imágenes (docker run \--rm \--entrypoint sh \<imagen\> \-c "ls \-a /app /etc/nginx" y búsqueda de patrones). 7\. docker compose config no contiene valores literales de los secretos en los archivos versionados. 8\. Un reinicio completo (reset) deja el sistema funcionando sin pasos manuales extra. Ejecútalo y muéstrame el resultado. |
| :---- |

| VERIFICA ANTES DE SEGUIR \- Puedes borrar todo (docker compose down \-v), clonar el repo en una carpeta nueva, copiar .env.example a .env, generar secretos y levantar el sistema siguiendo SOLO el README. \- Desde el host no puedes conectarte a Postgres ni al puerto 8000\. \- Todo el flujo de la app (login por rol, pacientes, transferencia) funciona por https\://localhost:8443. |
| :---- |

### **Paso D.8 \- Qué hacer con el despliegue anterior (Render y GitHub Pages)**

| TÚ (MANUAL, sin prompt) Suspende o elimina el servicio de Render y desactiva GitHub Pages para el front. Razones: (1) usa la versión vieja del código (Fernet) y las llaves que ya quedaron expuestas en E1; (2) un despliegue desactualizado contradice lo que dice el informe; (3) como el profesor aceptó despliegue local, el sistema evaluado es el de Docker. Si quieres conservar una vista pública, publica solo capturas o un video, no un servicio con datos. En el informe escribe, con honestidad: "En la Entrega 1 el sistema se desplegó en Render y GitHub Pages; para la Entrega 2 se migró a un despliegue local con Docker Compose para controlar el aislamiento de red, la terminación TLS y la gestión de llaves." |
| :---- |

### **Paso D.9 \- Hardening de contenedores (resultado para el informe)**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO D.9 \- Resumen de hardening Lee docker-compose.yml y los Dockerfile y crea docs/HARDENING\_DOCKER.md con una tabla: control \| cómo se implementa (archivo y línea) \| riesgo que reduce \| referencia (solo CIS Docker Benchmark, OWASP Docker Security Cheat Sheet u OWASP ASVS; si dudas del número de control escribe \[VERIFICAR\]). Cubre: usuario no root, no-new-privileges, cap\_drop ALL, sistema de archivos de solo lectura, redes internas y un único puerto publicado, imágenes con versión fija, multi-stage, sin secretos en imágenes, healthchecks, límites de recursos, certificados como volumen de solo lectura. Al final incluye una sección "Limitaciones": secretos en variables de entorno (en producción: Docker secrets o un gestor de secretos), certificado autofirmado, sin escaneo continuo de imágenes, el volumen de la base de datos no está cifrado en disco (mitigado por el cifrado de campos a nivel aplicación). |
| :---- |

| VERIFICA ANTES DE SEGUIR Checkpoint de la Fase D: docker compose up funciona desde un clon limpio, scripts/verificar\_despliegue.sh no tiene FALLAS, y existen docs/DOCKER.md y docs/HARDENING\_DOCKER.md. Haz un commit por paso (por ejemplo: "feat(docker): compose con redes internas"). |
| :---- |

# ✅ **FASE 1 \- Criptografía y endurecimiento del sistema (5 a 7 horas)**

*Corrige lo que observó el profesor (AES-256, rotación de llaves, integridad) y convierte en reales algunas afirmaciones de E1 que hoy no tienen mecanismo (logs inmutables, detección en menos de 24 horas).*

### **Paso 1.1 \- Migrar de Fernet a AES-256-GCM con llaves versionadas (1.5 h)**

*Fernet usa AES-128-CBC \+ HMAC-SHA256 y no es un estándar NIST. AES-256-GCM sí lo es (SP 800-38D) y da cifrado autenticado con llave de 256 bits. Plan B si no hay tiempo: dejar Fernet y corregir el informe (ver Anexo C).*

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 1.1 \- AES-256-GCM Migra backend/app/crypto.py de Fernet a AES-256-GCM usando cryptography.hazmat.primitives.ciphers.aead.AESGCM. Requisitos: 1\. Variables de entorno: ENC\_KEYS con formato "v1:\<base64url de 32 bytes\>,v2:\<base64url de 32 bytes\>" y ENC\_KEY\_CURRENT (ej. "v2"). Al arrancar, valida que cada llave decodifique a EXACTAMENTE 32 bytes; si no, lanza un error claro. 2\. encrypt(plaintext: str, aad: str \= "") \-\> str: genera nonce \= os.urandom(12), cifra con la llave actual y devuelve "\<kid\>:\<base64url(nonce \+ ciphertext\_con\_tag)\>". 3\. decrypt(token: str, aad: str \= "") \-\> str: separa el kid, busca la llave en el anillo, descifra y devuelve el texto. Si la autenticación falla (InvalidTag), lanza una excepción y NO devuelve datos parciales. 4\. AAD (datos asociados autenticados) \= "pacientes.\<campo\>.\<id\_del\_paciente\>", para que un valor cifrado no pueda copiarse a otro registro o campo sin que falle el descifrado. 5\. Actualiza TODOS los lugares donde se cifra o descifra (seed\_db.py, routers/pacientes.py, schemas/models). Genera el UUID del paciente en Python ANTES de cifrar, porque el AAD lo necesita. 6\. Elimina cualquier uso de Fernet y de ENCRYPTION\_KEY. 7\. Actualiza backend/.env.example con valores falsos y crea scripts/generate\_keys.py que imprima una llave AES-256 nueva en base64url (os.urandom(32)). 8\. Actualiza scripts/verificar\_cifrado.py: debe comprobar que los campos sensibles en la BD empiezan con el prefijo de versión (ej. "v2:"), que no contienen texto legible, y que un valor alterado (cambia un carácter) hace fallar el descifrado. 9\. Recrea la base y vuelve a sembrar con scripts/dev.sh reset: los datos viejos cifrados con Fernet no se pueden leer con GCM (son datos sintéticos). |
| :---- |

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 1.1b \- Pruebas de crypto Crea tests/test\_crypto.py con pytest que verifique: (a) ida y vuelta: decrypt(encrypt(x, aad), aad) \== x, incluyendo texto vacío, tildes y emojis; (b) dos cifrados del mismo texto producen salidas distintas (nonce aleatorio); (c) alterar un solo carácter del token provoca error al descifrar; (d) usar un AAD distinto provoca error al descifrar; (e) una llave de longitud distinta de 32 bytes hace fallar el arranque; (f) un token con kid desconocido falla con un error claro. Ejecuta las pruebas y muéstrame el resultado. |
| :---- |

| VERIFICA ANTES DE SEGUIR \- psql: SELECT nombre, diagnostico FROM pacientes LIMIT 3;  \-\> deben verse cadenas como "v2:..." sin texto legible. \- Un doctor sigue viendo los datos descifrados en la app. \- No queda ninguna referencia a "Fernet" en el código (busca con grep \-ri fernet backend/). |
| :---- |

### **Paso 1.2 \- Rotación de llaves demostrable (1 h)**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 1.2 \- Rotación de llaves Crea scripts/rotate\_keys.py que: 1\. Recorra la tabla pacientes en lotes (por ejemplo 500\) y, para cada campo cifrado (nombre, diagnostico, monto\_facturado, medicacion, resultado\_test), si el prefijo de versión NO es ENC\_KEY\_CURRENT, lo descifre con su llave y su AAD y lo vuelva a cifrar con la llave actual. Un commit por lote. 2\. Soporte \--dry-run (solo cuenta, no escribe) y sea idempotente (correrlo dos veces no cambia nada la segunda vez). 3\. Imprima al final un resumen: registros revisados, campos migrados, campos que ya estaban en la versión actual, errores. 4\. Ante cualquier error de descifrado, aborte ese lote y reporte el id; no sobrescribas datos que no pudiste descifrar. Crea también docs/ROTACION\_LLAVES.md con el procedimiento en tres pasos: (1) agregar la nueva versión a ENC\_KEYS y poner ENC\_KEY\_CURRENT a la nueva; (2) ejecutar rotate\_keys.py; (3) verificar con una consulta que ya no queden valores con la versión vieja (campo NOT LIKE 'v3:%') y recién entonces retirar la llave vieja del entorno. Incluye: la rotación es periódica (propón 12 meses, según el concepto de periodo criptográfico de NIST SP 800-57 Part 1\) o inmediata ante sospecha de compromiso; y una advertencia de que las llaves viejas deben conservarse hasta terminar la migración y respaldarse por separado. Agrega una prueba que: cifre registros con v1, cambie a v2, ejecute la rotación y verifique que todo se lee igual y ahora tiene prefijo v2. |
| :---- |

### **Paso 1.3 \- Logs de auditoría con cadena de hashes (1.5 h)**

*En E1 dijiste que los logs son inmutables, pero una tabla común de Postgres se puede editar sin dejar rastro. Este paso lo vuelve verdad: cadena de hashes (detecta alteración) \+ trigger y rol de solo inserción (impide alteración).*

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 1.3 \- Logs con cadena de hashes Objetivo: que audit\_logs sea verificable contra alteración. 1\. models.py, AuditLog: agrega seq (BigInteger, autoincremental, único), hash\_prev (String(64)), hash\_actual (String(64)) y detalle (String, nullable) si no existe. Haz usuario\_id NULLABLE (hay intentos de login con usuario inexistente). 2\. En audit.py centraliza TODA escritura de logs en una función log\_action(...). Dentro de UNA transacción debe: (a) tomar pg\_advisory\_xact\_lock con una constante, para serializar escrituras; (b) leer el hash\_actual del último registro por seq (si no hay ninguno usa "0"\*64); (c) generar el timestamp en Python en UTC, y usar ese mismo valor para el hash y para el INSERT; (d) calcular hash\_actual \= SHA-256 de la concatenación, separada por "\|", de: hash\_prev, usuario\_id (vacío si es None), accion, recurso, timestamp en ISO-8601 UTC, ip\_origen, detalle (vacío si es None); (e) insertar. 3\. Asegura que TODAS las rutas que registran eventos (login, login fallido, lectura, edición, borrado, transferencia, exportación) usen log\_action. 4\. Crea scripts/verificar\_cadena\_logs.py: recorre audit\_logs por seq, recalcula cada hash y reporta OK, o la primera fila donde la cadena se rompe (seq e id) y termina con código de salida distinto de 0\. 5\. Crea scripts/sql/proteger\_audit\_logs.sql con: (a) un trigger de FILA BEFORE UPDATE OR DELETE sobre audit\_logs que lance excepción, y un trigger de SENTENCIA BEFORE TRUNCATE que haga lo mismo; (b) los GRANT y REVOKE para que el rol de aplicación APP\_DB\_USER (creado en el paso D.5; no crees otro rol) tenga solo INSERT y SELECT sobre audit\_logs y los permisos mínimos sobre las demás tablas. setup\_db.py aplica este SQL con el rol dueño después de crear las tablas. Explica cómo se usa APP\_DB\_USER en la DATABASE\_URL del backend y el rol dueño solo en el servicio init. 6\. Pruebas: inserta 5 logs y verifica que la cadena da OK; luego, como superusuario en la prueba, desactiva el trigger, altera una fila y comprueba que la verificación falla señalando esa fila. 7\. Documenta en docs/LOGS\_INMUTABLES.md el diseño y sus límites: quien controle el servidor podría reescribir toda la cadena; mitigación futura: anclar periódicamente el último hash en un servicio externo. |
| :---- |

| VERIFICA ANTES DE SEGUIR \- Haz un login y una lectura; corre scripts/verificar\_cadena\_logs.py \-\> OK. \- Con la app conectada como APP\_DB\_USER (docker compose exec db psql \-U \<APP\_DB\_USER\> \-d \<base\>), intenta UPDATE audit\_logs ... \-\> debe fallar con error de permisos o de trigger. |
| :---- |

### **Paso 1.4 \- Bloqueo por intentos fallidos, rate limiting y alertas (1 h)**

*Esto hace real tu KPI de detectar accesos anómalos en menos de 24 horas.*

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 1.4 \- Bloqueo, rate limiting y alertas 1\. models.py: agrega a Usuario intentos\_fallidos (Integer, default 0\) y bloqueado\_hasta (DateTime, nullable). Agrega a AccionEnum los valores login\_fallido, bloqueo y exportacion (si uso un ENUM nativo de Postgres dime cómo migrarlo; en desarrollo puedo recrear las tablas). 2\. routers/auth.py, POST /auth/login:    \- Si el usuario está bloqueado (bloqueado\_hasta \> ahora), responde 429 con mensaje genérico y registra el evento.    \- Credenciales incorrectas: incrementa intentos\_fallidos y registra login\_fallido; al llegar a 5 bloquea 15 minutos y registra bloqueo.    \- La respuesta debe ser IDÉNTICA para usuario inexistente y para contraseña incorrecta (evita enumerar usuarios). Cuando el usuario no exista, verifica igualmente contra un hash falso para igualar tiempos de respuesta.    \- Login correcto: reinicia intentos\_fallidos.    \- Registra en audit\_logs todos los casos. Para usuario inexistente guarda el email intentado en detalle (nunca la contraseña) y usuario\_id nulo. 3\. Rate limiting con slowapi: 10 peticiones por minuto por IP en /auth/login. 4\. Crea GET /audit-logs/alertas (solo auditor y admin) que devuelva: (a) usuarios con 5 o más login\_fallido en los últimos 10 minutos; (b) lecturas de historiales fuera de 07:00-21:00 hora de Lima; (c) usuarios que leyeron más de N historiales distintos en una hora (N configurable, por defecto 30). 5\. Pruebas: bloqueo al 5.º intento, desbloqueo al vencer el plazo (simula el tiempo), respuesta idéntica para usuario inexistente, y cada regla de alertas. |
| :---- |

### **Paso 1.5 \- Backups cifrados y restauración cronometrada (1 h)**

*Cumple el requisito de contingencias y te da un RTO medido (evidencia) en lugar de un número supuesto.*

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 1.5 \- Backups Todo con Docker: no instales pg\_dump ni gpg en mi equipo. Agrega a docker-compose.yml un servicio backup (profiles: \["tools"\], red db\_net, imagen basada en postgres:16 con gnupg instalado mediante un Dockerfile mínimo en docker/backup/) y monta ./backups. Detecta mi sistema operativo y entrega, si hace falta, versiones .ps1 de los scripts que se ejecutan en el host. 1\. scripts/backup.sh: ejecuta pg\_dump en formato custom (-Fc) de la base criptomed y cifra el resultado con gpg \--symmetric \--cipher-algo AES256, tomando la passphrase de la variable de entorno BACKUP\_PASSPHRASE (nunca en el repo). Nombra el archivo backup\_AAAA-MM-DD\_HHMM.dump.gpg dentro de backups/ (ignorado por git). Conserva los últimos 7 y borra los más viejos. Imprime el tamaño y la duración. 2\. scripts/restore.sh \<archivo\>: descifra y restaura en una base SEPARADA llamada criptomed\_restore\_test (nunca sobre la base real por defecto). Mide e imprime el tiempo total. 3\. scripts/verificar\_restauracion.py: compara conteos de filas por tabla entre la base original y la restaurada, comprueba que la cadena de hashes de audit\_logs sigue siendo válida en la restaurada, y descifra una muestra de 5 pacientes con las llaves actuales. 4\. docs/BACKUPS.md: política (diario incremental / semanal completo, como en el informe E1), dónde se guardan, y la regla de que las llaves de cifrado (ENC\_KEYS y la passphrase) se respaldan POR SEPARADO de los dumps. Incluye una sección "Prueba de restauración" con fecha, tamaño y tiempo medido (RTO medido) para citar en el informe. |
| :---- |

### **Paso 1.6a \- Cabeceras de seguridad y CORS (30 min)**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 1.6a \- Headers y CORS 1\. CORS: reemplaza cualquier "\*" por una lista de orígenes permitidos leída de la variable ALLOWED\_ORIGINS (https\://localhost:8443, el origen del front servido por el edge de Docker; como front y API comparten origen, CORS casi no se usa, pero mantenlo restrictivo). Limita los métodos y cabeceras a los necesarios. 2\. Crea un middleware que agregue a toda respuesta: Strict-Transport-Security (max-age=31536000; includeSubDomains), X-Content-Type-Options: nosniff, X-Frame-Options: DENY, Referrer-Policy: no-referrer, Cache-Control: no-store para respuestas con datos de pacientes, y Content-Security-Policy "default-src 'none'; frame-ancestors 'none'" para la API. 3\. Deshabilita /docs, /redoc y /openapi.json cuando ENV=production, y mantenlos activos en desarrollo (los necesito para el escaneo de ZAP; para los escaneos usaré docker-compose.scan.yml que sobrescribe ENV=development solo en esa ejecución). 4\. En el front (index.html) agrega una Content-Security-Policy por meta tag restrictiva (script-src 'self'; connect-src solo hacia mi API) y confirma que no se usa dangerouslySetInnerHTML en ningún componente. 5\. Pruebas que verifiquen la presencia de los headers y que un origen no permitido no recibe cabeceras CORS. |
| :---- |

### **Paso 1.6b \- Política de contraseñas alineada a NIST SP 800-63B (30 min)**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 1.6b \- Contraseñas Implementa una función validate\_password\_policy(password, email, nombre) usada en POST /usuarios, en cualquier cambio de contraseña y en el seed: \- Longitud mínima de 12 caracteres y máxima de 72 bytes en UTF-8 (límite de bcrypt: rechaza explícitamente lo que exceda, no lo trunques en silencio). \- Sin reglas de composición obligatorias (no exijas mayúsculas/símbolos) y SIN expiración periódica obligatoria. \- Rechaza contraseñas comunes o filtradas: usa la librería zxcvbn (puntuación mínima 3\) y/o una lista local de las 10 000 contraseñas más comunes (inclúyela en el repo si la puedes obtener de una fuente de licencia abierta; si no, dime cuál usar). \- Rechaza contraseñas que contengan el email o el nombre del usuario. Confirma que bcrypt usa un factor de costo de 12 (rounds=12). Actualiza las contraseñas del seed para que cumplan la política (leyéndolas de variables de entorno DEMO\_PASSWORD\_\*, no escritas en el repo). Agrega pruebas con casos válidos e inválidos. |
| :---- |

### **Paso 1.6c \- JWT y sesión (30 min)**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 1.6c \- JWT 1\. En auth.py, decodifica el JWT con algorithms=\["HS256"\] explícito y exige las claims exp y sub; rechaza tokens sin ellas (RFC 8725). 2\. En cada request protegida, get\_current\_user debe volver a consultar la BD y rechazar al usuario si activo es False (así la revocación de acceso es inmediata) o si está bloqueado. 3\. Mantén JWT\_EXPIRE\_MINUTES corto (15 a 30). En el front, agrega un temporizador de inactividad de 15 minutos que cierre la sesión (borra el token) y redirija al login. 4\. El token está en localStorage, que es vulnerable a robo por XSS. NO migres a cookies en este paso: documenta en docs/RIESGOS\_ACEPTADOS.md que se acepta el riesgo mitigado con CSP estricta, sin dangerouslySetInnerHTML y con expiración corta, y que la mejora futura es una cookie HttpOnly \+ Secure \+ SameSite con protección CSRF. 5\. Pruebas: token sin exp, token firmado con otro algoritmo (alg none o HS512), token de usuario revocado, token expirado. |
| :---- |

### **Paso 1.7 \- Transparencia y control para el paciente (1.5 h)**

*Refuerza los derechos del titular (acceso, portabilidad, control sobre quién ve su historial) y es lo más vistoso en la demo.*

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 1.7 \- Funciones para el paciente Primero verifica que ya funcionan: rol paciente, GET /pacientes/me, GET /doctores y PATCH /pacientes/{id}/transferir-doctor (con 3 doctores sembrados y un paciente demo con cuenta propia). Si falta algo, impleméntalo. Luego agrega: 1\. GET /pacientes/me/accesos: lista paginada de los accesos al historial del paciente autenticado (consulta audit\_logs con recurso \= "paciente:\<su id\>"): fecha y hora, acción, nombre y rol del profesional. Solo el propio paciente puede verla. 2\. GET /pacientes/me/export: devuelve en JSON los datos del paciente ya descifrados (derecho de acceso y portabilidad) y registra el evento con la acción exportacion. 3\. models.py, Paciente: campos consentimiento\_fecha (DateTime) y consentimiento\_version (String, ej. "v1.0"). En el seed, asígnalos a los pacientes demo. 4\. Front, página MiHistorial.jsx: muestra el consentimiento (fecha y versión), la lista "Quién accedió a mi historial", un botón "Descargar mis datos" y el botón "Transferir mi historial" con confirmación explícita (diálogo que nombre al doctor actual y al nuevo). 5\. Pruebas: un paciente no puede ver los accesos ni exportar los datos de otro paciente; la transferencia por un paciente distinto del dueño devuelve 403; tras la transferencia el nuevo doctor ve el historial y el anterior recibe 403/404. |
| :---- |

### **Paso 1.8 \- OPCIONAL: acceso de emergencia (break-glass)**

*Solo si te sobra tiempo. Es un dilema ético real (seguridad vs. atención oportuna) y suma en la sección de ética. Si no lo implementas, explica en el informe por qué.*

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 1.8 \- Break-glass (opcional) Implementa POST /pacientes/{id}/acceso-emergencia (solo rol doctor): permite a un doctor NO asignado ver el historial de un paciente solo si envía una justificación de al menos 20 caracteres. El acceso dura 30 minutos, se registra con una acción acceso\_emergencia y la justificación en detalle, y aparece en GET /audit-logs/alertas como evento a revisar por el auditor. El paciente lo ve en GET /pacientes/me/accesos marcado como "acceso de emergencia". Incluye pruebas y deja claro en docs/ que es un mecanismo excepcional y auditado. |
| :---- |

### **Paso 1.9 \- Checkpoint de la Fase 1**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 1.9 \- Checkpoint Ejecuta toda la suite de pruebas, scripts/verificar\_cifrado.py y scripts/verificar\_cadena\_logs.py. Entrégame una tabla: requisito \| cómo se verifica \| resultado (OK/FALLA). Incluye: cifrado AES-256-GCM, rotación, logs encadenados, bloqueo de cuenta, rate limiting, headers, política de contraseñas, JWT, backup/restauración, funciones del paciente. No arregles nada nuevo todavía; solo reporta. |
| :---- |

| VERIFICA ANTES DE SEGUIR Todo en OK y un commit por paso. Recién entonces pasa a la Fase 2\. |
| :---- |

# ✅ **FASE 2 \- Análisis de seguridad con herramientas (3 a 4 horas)**

*En E1 solo describías qué herramienta usarías. En E2 la rúbrica pide aplicarla: escaneo inicial, hallazgos, correcciones y re-escaneo, con evidencia. Usa al menos dos herramientas de categorías distintas; lo ideal es todas las de la tabla.*

| Categoría | Herramienta | Qué analiza |
| :---- | :---- | :---- |
| SAST (código Python) | Bandit | Patrones inseguros en el backend |
| Dependencias | pip-audit y npm audit | Vulnerabilidades conocidas (CVE) en librerías |
| DAST (app corriendo) | OWASP ZAP (baseline y API scan) | Inyección, headers, CORS, configuración |
| TLS | testssl.sh o sslyze | Versiones y cifrados TLS del servidor |
| Secretos | gitleaks | Credenciales en el repo e historial |
| Imágenes y Dockerfiles | Trivy y Hadolint | Vulnerabilidades en imágenes y malas prácticas en Dockerfile |

### **Paso 2.1 \- Escaneo inicial ("antes")**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 2.1 \- Escaneos antes Todo se ejecuta en contenedores sobre el despliegue local de Docker; no instales herramientas en mi equipo. Agrega servicios con profiles: \["tools"\] a docker-compose.yml (o a docker-compose.scan.yml) y crea scripts/security\_scan.sh (y .ps1 si uso Windows) que reciba "before" o "after", guarde los reportes en reports/\<before\|after\>/ y ejecute, cada uno de forma independiente (si uno falla, continúa con los demás y deja un resumen): \- Bandit sobre backend/app y backend/scripts: salida JSON y HTML. \- pip-audit sobre backend/requirements.txt: salida JSON. \- npm audit \--json dentro de un contenedor de Node con frontend/. \- gitleaks (imagen oficial) sobre todo el repo con historial: reporte JSON. \- Hadolint sobre docker/\*/Dockerfile. \- Trivy (imagen oficial): escaneo de las imágenes construidas (backend y edge) y del sistema de archivos del repo; salida JSON. \- testssl.sh (imagen oficial) contra edge:8443 desde la red app\_net. \- OWASP ZAP (ghcr.io/zaproxy/zaproxy:stable): zap-baseline.py contra http\://backend:8000 y zap-api-scan.py con http\://backend:8000/openapi.json, ambos DENTRO de la red de Docker (así evitas el problema del certificado autofirmado; el TLS ya lo cubre testssl). Para los endpoints protegidos configura el header "Authorization: Bearer \<token\>" de un usuario de pruebas (consulta la documentación oficial de ZAP); si no lo logras, documenta la limitación. Usa docker-compose.scan.yml con ENV=development solo para esta ejecución, porque en producción /openapi.json está deshabilitado. Al final imprime una tabla con el número de hallazgos por herramienta y severidad. NO modifiques el código de la app en este paso. |
| :---- |

| TÚ (MANUAL, sin prompt) \- Levanta el sistema con scripts/dev.sh up y siembra la base antes de escanear: el análisis se hace sobre el despliegue local de Docker. \- Ejecuta: ./scripts/security\_scan.sh before \- Guarda capturas de los reportes HTML (Bandit y ZAP): irán al informe y a la presentación. |
| :---- |

### **Paso 2.2 \- Tabla de hallazgos**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 2.2 \- Hallazgos Lee reports/before/\* y crea docs/hallazgos.md con una tabla: ID \| herramienta \| severidad \| descripción \| archivo o endpoint \| ¿falso positivo? (sí/no \+ justificación) \| decisión (corregir / aceptar riesgo / trabajo futuro) \| corrección propuesta. Reglas: agrupa duplicados; NO omitas hallazgos de severidad media o alta; NO inventes hallazgos (cada fila debe apuntar a una entrada real del reporte); para cada "aceptar riesgo" escribe la justificación en una frase que yo pueda usar en el informe. Al final agrega un resumen con conteos por herramienta y severidad. |
| :---- |

### **Paso 2.3 \- Corregir**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 2.3 \- Correcciones Corrige los hallazgos marcados "corregir" en docs/hallazgos.md, empezando por severidad alta y media. Haz un commit por grupo de hallazgos (mensaje: "fix(sec): \<id\> \<resumen\>"). Para cada corrección, actualiza la fila en docs/hallazgos.md con el commit y una nota de cómo se verificó. Si una corrección rompe pruebas existentes, arréglalas. No ocultes un hallazgo con comentarios tipo "nosec" salvo que sea un falso positivo justificado por escrito en la tabla. |
| :---- |

### **Paso 2.4 \- Re-escaneo ("después") y comparativa**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 2.4 \- Escaneos después Ejecuta scripts/security\_scan.sh after y genera docs/comparativa\_antes\_despues.md con: conteo por herramienta y severidad antes y después; lista de hallazgos resueltos; lista de hallazgos que persisten con su justificación (falso positivo, riesgo aceptado, trabajo futuro). Debe ser fiel a los reportes reales: no inventes mejoras. |
| :---- |

| VERIFICA ANTES DE SEGUIR Tienes reports/before y reports/after, docs/hallazgos.md y docs/comparativa\_antes\_despues.md. Para cada hallazgo que no corregiste hay una justificación escrita: eso también puntúa en la rúbrica. |
| :---- |

# **FASE 3 \- DPIA y consideraciones éticas (3 a 4 horas)**

*La DPIA evalúa riesgos para los derechos y libertades de los titulares de los datos (los pacientes), no para la empresa. La IA te ayuda a redactar el borrador a partir del código real; las decisiones y las citas legales las revisas tú.*

### **Paso 3.1 \- Inventario de datos**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 3.1 \- Inventario de datos Lee models.py, schemas.py y los routers y crea docs/inventario\_datos.md con una tabla de TODOS los campos que guarda el sistema (usuarios, pacientes, audit\_logs, diagnosticos\_cie10): campo \| descripción \| categoría (identificador directo / cuasi-identificador / dato de salud sensible / dato financiero / dato técnico) \| ¿cifrado en reposo? \| roles que pueden verlo \| finalidad \| ¿es necesario? (sí/no \+ razón, para evaluar minimización). Señala explícitamente los cuasi-identificadores que combinados podrían reidentificar a una persona aun sin nombre (por ejemplo edad \+ género \+ fecha de admisión \+ hospital). No inventes campos que no existan en el código. |
| :---- |

### **Paso 3.2 \- DPIA completa**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 3.2 \- DPIA Redacta docs/DPIA.md siguiendo esta estructura (usa SOLO las referencias de la lista del PROMPT 0; marca \[VERIFICAR\] cualquier artículo de ley o plazo que no esté ahí; NO afirmes una base legal concreta ni números de artículo, propón opciones y márcalas \[VERIFICAR\]): 1\. Descripción sistemática del tratamiento: qué datos, de quién, para qué, quién accede, dónde se almacenan y por cuánto tiempo (usa docs/inventario\_datos.md). 2\. Ciclo de vida de los datos, en tabla: recolección \| almacenamiento \| uso \| compartición (transferencia del paciente a otro doctor) \| transmisión \| retención \| eliminación o anonimización. Para cada etapa: qué ocurre en CriptoMed, riesgo principal y control REAL implementado (cita el archivo del repo donde está). 3\. Necesidad y proporcionalidad: finalidad, minimización, consentimiento (campos consentimiento\_fecha y consentimiento\_version), derechos del titular que el sistema soporta (acceso, portabilidad, control de quién accede) y los que no (indica cuáles y por qué). 4\. Identificación de riesgos PARA LOS TITULARES, de 8 a 12, con probabilidad (1-5), impacto (1-5), riesgo inherente \= P x I, medidas de mitigación (con referencia a controles reales) y riesgo residual. Incluye al menos: fuga masiva de la base de datos, acceso indebido de personal interno, reidentificación, transferencia a un doctor equivocado, indisponibilidad en una emergencia, retención excesiva, uso secundario no autorizado, error de mapeo CIE-10 (dato clínico incorrecto), pérdida de llaves de cifrado. 5\. Consulta y responsables: propone quién sería el Oficial de Datos Personales de una clínica pequeña y cómo se ejercen los derechos \[VERIFICAR obligaciones del Reglamento D.S. 016-2024-JUS\]. 6\. Conclusión y plan de revisión (por ejemplo cada 12 meses o ante cambios importantes). Referencias para citar: GDPR art. 35, ISO/IEC 29134, Reglamento de la Ley 29733\. Entrégamelo en Markdown. Al final lista todo lo marcado \[VERIFICAR\]. |
| :---- |

| TÚ (MANUAL, sin prompt) Revisa cada \[VERIFICAR\] en la DPIA: abre el texto oficial del Reglamento (El Peruano o gob.pe) y confirma artículos y plazos antes de citarlos. Ajusta las probabilidades e impactos según tu criterio: la puntuación debe poder defenderse en la presentación. |
| :---- |

### **Paso 3.3 \- Mapa de flujo de datos (diagrama)**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 3.3 \- Diagrama de flujo de datos Crea docs/flujo\_datos.mmd con un diagrama Mermaid (flowchart) del flujo de datos del paciente: entrada de datos en admisión \-\> API \-\> cifrado AES-256-GCM \-\> PostgreSQL \-\> lectura por doctor/administrativo (filtrado por rol) \-\> logs de auditoría encadenados \-\> backups cifrados; y el flujo de transferencia a otro doctor y de exportación al paciente. Marca en cada flecha el control de seguridad (TLS 1.3, RBAC, cifrado, log). Debe reflejar el código real. |
| :---- |

### **Paso 3.4 \- Sección de ética y privacidad**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 3.4 \- Ética y privacidad Redacta docs/etica\_privacidad.md (máximo 2 páginas) con estas secciones, cada una conectada a una decisión concreta del sistema (cita archivo o endpoint): 1\. Autonomía y consentimiento: la transferencia self-service del paciente, el registro de consentimiento y la vista "quién accedió a mi historial". 2\. Minimización y finalidad: por qué cada campo es necesario (usa docs/inventario\_datos.md) y qué se evitó recolectar. 3\. Tensión ética 1: derecho de cancelación del titular vs. obligación de conservar la historia clínica durante un plazo legal \[VERIFICAR el plazo en la norma técnica del MINSA antes de citarlo\]. 4\. Tensión ética 2: seguridad estricta vs. atención oportuna en emergencias (acceso de emergencia: implementado o no, y por qué). 5\. Reidentificación y datos sintéticos: el dataset no contiene pacientes reales, pero el sistema se diseñó como si los contuviera; por qué no se usan datos reales en pruebas. 6\. Transparencia sobre el uso de IA generativa en el desarrollo: qué se generó con IA y cómo se revisó (pruebas, escaneos, revisión manual). Sé honesto. 7\. Qué consideraciones éticas NO aplican y por qué (por ejemplo, no hay decisiones automatizadas ni perfilado con IA sobre los pacientes). Tono: claro y sin relleno. Marca \[VERIFICAR\] lo que dependa de una norma. |
| :---- |

| VERIFICA ANTES DE SEGUIR Existen docs/inventario\_datos.md, docs/DPIA.md, docs/flujo\_datos.mmd y docs/etica\_privacidad.md, y ya resolviste todos los \[VERIFICAR\]. |
| :---- |

# **FASE 4 \- Reescribir el informe en Notion (5 a 6 horas)**

*El profesor dijo que el informe se leía como una lista de requisitos y que varias decisiones no tenían fuente. Ahora el informe es una narrativa de diseño: cada decisión se explica con Decisión → Por qué → Estándar → Alternativa descartada → Evidencia. La lista de requisitos pasa a un anexo.*

### **Estructura objetivo (12 a 15 páginas sin anexos)**

| \# | Sección | Extensión | Prompt |
| :---- | :---- | :---- | :---- |
| \- | Resumen ejecutivo | 1/2 pág | 4.1 |
| 1 | Problema y contexto | 1 pág | 4.1 |
| 2 | Solución y arquitectura | 1.5 pág | 4.1 |
| 3 | Diseño de seguridad (reposo, tránsito, identidad, autorización, trazabilidad, continuidad, despliegue y aislamiento) | 5 a 6 pág | 4.2 a 4.4 |
| 4 | Funcionalidad clave: control del paciente | 1 pág | 4.4 |
| 5 | Verificación con herramientas (antes y después) | 1.5 pág | 4.5 |
| 6 | Riesgos e incidentes | 1 pág | 4.6 |
| 7 | Privacidad y ética (resumen de la DPIA) | 2 pág | 4.7 |
| 8 | Lecciones aprendidas y retrospectiva | 1 pág | 4.8 |
| 9 | Trabajo futuro y recomendaciones | 1/2 pág | 4.8 |
| A-E | Anexos: matriz de trazabilidad, DPIA completa, reportes, diccionario de datos y roles, referencias | \- | 4.9 |

### **Paso 4.0 \- Reglas de escritura (pégalas al empezar la sesión de redacción)**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 4.0 \- Reglas de redacción del informe Vas a ayudarme a redactar el informe técnico de CriptoMed para publicarlo en Notion. Entrega todo en Markdown compatible con Notion (títulos con \#, tablas con \|, listas con \-). REGLAS 1\. Narrativa de diseño, no checklist: cada sección explica cómo funciona el sistema y por qué se diseñó así. Evita listas largas de requisitos; usa párrafos cortos, tablas pequeñas y diagramas. 2\. Cada decisión técnica se escribe en este formato: \*\*Decisión\*\* (qué se hizo) \-\> \*\*Por qué\*\* (el problema que resuelve) \-\> \*\*Estándar o fuente\*\* \-\> \*\*Alternativa descartada y razón\*\* \-\> \*\*Evidencia\*\* (archivo, script, captura o reporte del repo). 3\. Cita SOLO fuentes de esta lista: FIPS 197; NIST SP 800-38D; NIST SP 800-57 Part 1; NIST SP 800-63B; NIST SP 800-52 Rev. 2; NIST SP 800-92; NIST SP 800-61; RFC 8446; RFC 7519; RFC 8725; OWASP Password Storage Cheat Sheet; OWASP Logging Cheat Sheet; OWASP ASVS; CIS Docker Benchmark; OWASP Docker Security Cheat Sheet; GDPR art. 35; ISO/IEC 29134; HIPAA Security Rule 45 CFR 164.312; Ley 29733; Reglamento D.S. 016-2024-JUS; ANPD. Todo lo demás se marca \[VERIFICAR\]. 4\. Nunca remitas al lector a un README o markdown para entender algo: si es importante, se explica en el informe. 5\. Escribe solo lo que existe en el repositorio. Si algo no está implementado, dilo y justifícalo; no lo presentes como hecho. 6\. Redacción clara y sin relleno: frases cortas, voz activa, sin repetir el requisito antes de explicar la solución. Español neutro. 7\. Usa los nombres reales de archivos, endpoints y roles del repo. Responde "listo" y espera la primera sección. |
| :---- |

### **Paso 4.1 \- Resumen ejecutivo, problema, solución y arquitectura**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 4.1 Redacta: (a) Resumen ejecutivo de media página: problema, solución, 3 a 4 resultados medibles reales del repo (por ejemplo: campos sensibles cifrados con AES-256-GCM, cadena de logs verificable, hallazgos de ZAP/Bandit antes y después, RTO medido), enlace al repo y las instrucciones para levantar el sistema con docker compose; (b) Sección 1 Problema y contexto (1 pág): clínicas pequeñas en Perú, Ley 29733 y su Reglamento D.S. 016-2024-JUS, datos de IBM Cost of a Data Breach 2025 (7.42 M USD y 279 días; si usas la cifra de ransomware, redáctala correctamente: porcentaje de ORGANIZACIONES de salud afectadas, y márcala \[VERIFICAR\] hasta que yo la confirme en la fuente); (c) Sección 2 Solución y arquitectura (1.5 pág): incluye el diagrama Mermaid de la arquitectura (léelo del README o regéneralo desde el código), tabla de roles con lo que ve cada uno, y el flujo de una petición típica de un doctor. |
| :---- |

### **Paso 4.2 \- Diseño de seguridad (a): datos en reposo y gestión de llaves**

*Aquí se responde directo al profesor: AES-256, integridad, de dónde sale el estándar y cómo se rota la llave.*

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 4.2 Lee backend/app/crypto.py, docs/ROTACION\_LLAVES.md y scripts/rotate\_keys.py y redacta la subsección "3.1 Datos en reposo y gestión de llaves" usando el formato de decisión de las reglas. Debe cubrir: \- Qué campos se cifran y por qué esos (no todos los campos). \- AES-256 en modo GCM: confidencialidad \+ integridad (tag de autenticación); nonce aleatorio de 96 bits; estándares FIPS 197 y NIST SP 800-38D. \- AAD \= tabla.campo.id: qué ataque evita (copiar un valor cifrado a otro registro). \- Alternativa descartada: Fernet (AES-128-CBC \+ HMAC-SHA256: también autenticado, pero llave de cifrado de 128 bits y no está definido en un estándar NIST). Explica con honestidad que la versión inicial usaba Fernet y por qué se migró. \- Gestión del ciclo de vida de las llaves: llaves versionadas, rotación en tres pasos, periodicidad y concepto de periodo criptográfico (NIST SP 800-57 Part 1), qué pasa si se pierde una llave (los datos se vuelven irrecuperables: por eso el respaldo separado). \- Limitación declarada: las llaves viven en variables de entorno; en producción irían en un KMS/HSM con cifrado de sobre (se pasa a Trabajo futuro). \- Evidencia: scripts/verificar\_cifrado.py, captura del SELECT con valores v2:..., prueba de rotación. Máximo 1 página y media. |
| :---- |

### **Paso 4.3 \- Diseño de seguridad (b): tránsito e identidad**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 4.3 Lee main.py, auth.py y la configuración de TLS/despliegue y redacta las subsecciones "3.2 Datos en tránsito" y "3.3 Identidad y sesiones" con el formato de decisión: \- TLS 1.3 (RFC 8446, NIST SP 800-52 Rev. 2): explica con honestidad que el TLS lo termina el contenedor edge (Nginx, solo TLS 1.3) con un certificado autofirmado generado con OpenSSL, y que dentro de la red interna de Docker el tramo edge \-\> backend va en HTTP porque ese puerto no es accesible desde el host (limitación declarada; mejora futura: TLS mutuo interno). Menciona HSTS y el resultado de testssl.sh. Alternativa descartada: HTTP sin cifrar; y una CA reconocida queda para producción real. \- Contraseñas: bcrypt con factor 12 y límite de 72 bytes (OWASP Password Storage Cheat Sheet; Argon2id sería la primera opción y se deja como mejora); política de contraseñas alineada a NIST SP 800-63B (longitud, verificación contra contraseñas comunes, sin rotación obligatoria) y por qué se descartó "cambio cada 90 días" que tenía la versión E1. \- Sesión con JWT (RFC 7519, RFC 8725): algoritmo fijado, exp y sub obligatorios, expiración corta, verificación de usuario activo en cada request (revocación inmediata), cierre por inactividad en el front. Riesgo aceptado: token en localStorage (ver docs/RIESGOS\_ACEPTADOS.md). \- Bloqueo por intentos fallidos, rate limiting y respuesta idéntica ante usuario inexistente. Incluye evidencia (archivo, prueba o captura) en cada decisión. Máximo 1.5 páginas. |
| :---- |

### **Paso 4.3b \- Diseño de seguridad (d): despliegue y aislamiento con Docker**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 4.3b Lee docker-compose.yml, los Dockerfile, docker/edge/nginx.conf, docs/DOCKER.md y docs/HARDENING\_DOCKER.md y redacta "3.7 Despliegue y aislamiento" con el formato de decisión: (a) despliegue local reproducible con Docker Compose (decisión aceptada por el profesor) y por qué se migró desde Render/GitHub Pages; (b) redes: db\_net interna sin salida a internet y un único puerto publicado (8443); (c) contenedores sin root, cap\_drop ALL, sistema de archivos de solo lectura y no-new-privileges (CIS Docker Benchmark y OWASP Docker Security Cheat Sheet; marca \[VERIFICAR\] el número de control); (d) secretos fuera de las imágenes; (e) X-Forwarded-For y por qué el backend confía en él (solo el edge puede alcanzarlo); (f) resultados de Trivy y Hadolint. Incluye un diagrama Mermaid de servicios y redes. Declara los límites: secretos en variables de entorno, volumen de la base de datos sin cifrado de disco, certificado autofirmado. Máximo 1 página. |
| :---- |

### **Paso 4.4 \- Diseño de seguridad (c) y control del paciente**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 4.4 Lee rbac.py, audit.py, docs/LOGS\_INMUTABLES.md, docs/BACKUPS.md y routers/pacientes.py y redacta: "3.4 Autorización", "3.5 Trazabilidad", "3.6 Continuidad" y la Sección 4 "Control del paciente", con el formato de decisión: \- Autorización: RBAC con mínimo privilegio (OWASP ASVS), filtrado de campos en el servidor, tabla rol x recurso; dónde se aplica en el código. \- Trazabilidad: qué se registra, cadena de hashes (SHA-256) para detectar alteración, trigger y rol de solo inserción, verificación con scripts/verificar\_cadena\_logs.py, alertas (login\_fallido, fuera de horario, volumen inusual); NIST SP 800-92 y OWASP Logging Cheat Sheet. Declara el límite: quien controle el servidor podría reescribir la cadena completa; mitigación futura: anclar el hash en un servicio externo. \- Continuidad: backups cifrados con AES-256 (gpg), separación de llaves y dumps, RTO medido en la prueba de restauración (usa el dato real de docs/BACKUPS.md, no inventes uno), RPO según la frecuencia de backup. \- Sección 4: el paciente ve quién accedió a su historial, descarga sus datos, ve su consentimiento y transfiere su historial a otro doctor; cómo queda registrado; conexión con los derechos del titular en la Ley 29733 y su Reglamento \[VERIFICAR artículos\]. Máximo 2.5 páginas en total. |
| :---- |

### **Paso 4.5 \- Verificación con herramientas**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 4.5 Con docs/hallazgos.md y docs/comparativa\_antes\_despues.md redacta la Sección 5 "Verificación con herramientas": una tabla breve por herramienta (qué analiza, hallazgos antes, hallazgos después), los 3 a 5 hallazgos más relevantes con su corrección (formato: hallazgo \-\> riesgo \-\> corrección \-\> evidencia), y una tabla de riesgos aceptados con justificación. Usa solo cifras reales de los reportes. Indica las limitaciones del análisis (por ejemplo, el baseline de ZAP sin autenticar ve poco; TLS verificado aparte). Máximo 1.5 páginas. |
| :---- |

### **Paso 4.6 \- Riesgos e incidentes**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 4.6 Redacta la Sección 6 "Riesgos e incidentes": (a) tabla de riesgos por entidad afectada (pacientes, clínica, personal) SIN filas duplicadas, con riesgo, impacto y control que lo mitiga; (b) plan de respuesta ante incidentes en 5 fases (detección, contención, notificación, remediación, post-mortem; NIST SP 800-61 como referencia) indicando QUÉ parte del sistema apoya cada fase (alertas, bloqueo y revocación de usuarios, restauración de backups, verificación de cadena de logs). En notificación incluye: aviso interno a la dirección de la clínica y notificación a la ANPD dentro de las 48 horas e información a los titulares afectados según el Reglamento D.S. 016-2024-JUS \[VERIFICAR artículo\], y reporte al Centro Nacional de Seguridad Digital si el incidente es digital. Máximo 1 página. |
| :---- |

### **Paso 4.7 \- Privacidad y ética (resumen de la DPIA)**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 4.7 A partir de docs/DPIA.md y docs/etica\_privacidad.md redacta la Sección 7 "Privacidad y ética" (máximo 2 páginas): 1 párrafo de método (qué es una DPIA y por qué se hizo; GDPR art. 35 e ISO/IEC 29134 como referencia, y el Reglamento peruano), el mapa del ciclo de vida de los datos en una tabla compacta, los 5 riesgos principales para los titulares con su riesgo inherente y residual, y las consideraciones éticas clave (autonomía y consentimiento, tensión entre cancelación y conservación de la historia clínica, acceso de emergencia, datos sintéticos, uso de IA generativa). Indica que la DPIA completa está en el Anexo B. Si alguna consideración ética no aplica, explica por qué. |
| :---- |

### **Paso 4.8 \- Lecciones aprendidas, retrospectiva y trabajo futuro**

*La rúbrica penaliza fuerte que falte la retrospectiva. Complétala con tu experiencia real: la IA solo la ordena.*

| TÚ (MANUAL, sin prompt) Antes del prompt, escribe en 6 a 10 viñetas lo que de verdad pasó en tu proceso. Ideas que ya ocurrieron en este proyecto (confírmalas o cámbialas): \- Cifrar con una librería no es lo mismo que poder justificar el algoritmo: la observación sobre Fernet vs. AES-256 enseñó a verificar la especificación antes de afirmar. \- El código generado con IA necesita revisión: el primer models.py tenía errores de sintaxis que habrían roto la ejecución. \- Casi se publican secretos en la documentación: hábito de .env.example y escaneo de secretos desde el día 1\. \- La idea de la transferencia de doctor salió de validar con el profesor a tiempo. \- Qué harías distinto: hacer la DPIA y un modelo de amenazas ANTES de programar; definir los roles sin contradicciones desde el inicio; automatizar los escaneos. \- Qué funcionó: dividir el trabajo en fases con un commit por paso. |
| :---- |

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 4.8 Con las viñetas que te pego abajo, redacta (a) la Sección 8 "Lecciones aprendidas y retrospectiva" (máximo 1 página) en formato Empezar / Parar / Continuar más un párrafo de reflexión honesta sobre el proceso; y (b) la Sección 9 "Trabajo futuro y recomendaciones" (media página) con una tabla: medida \| riesgo que reduce \| por qué no se implementó ahora. Incluye: MFA para todos los roles; certificado de una CA reconocida; llaves en KMS/HSM con cifrado de sobre; WAF; Argon2id; cookie HttpOnly \+ Secure \+ SameSite con protección CSRF; anclaje externo del hash de logs; anonimización o seudonimización en entornos de prueba; acceso de emergencia auditado (si no se implementó); monitoreo centralizado de logs. NO inventes cosas que yo no te haya dicho en las lecciones. MIS VIÑETAS: \[pega aquí tus viñetas\] |
| :---- |

### **Paso 4.9 \- Anexos: matriz de trazabilidad y referencias**

*Las consignas piden que el informe incluya la lista de requerimientos funcionales y de seguridad y lo implementado en la primera entrega. Este anexo lo cumple sin ensuciar el cuerpo del informe.*

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 4.9 Crea docs/matriz\_trazabilidad.md con una tabla: Requisito \| Tipo (negocio / seguridad / funcional / técnico / E2) \| Entrega (E1, E2 o E1 mejorado en E2) \| Estado (Implementado / Parcial / No implementado) \| Dónde está (archivo o endpoint) \| Evidencia (script, captura, reporte). Recorre TODOS estos requisitos, verificándolos en el código real, y si no están completamente implementados dilo y justifícalo: Negocio: valor medido con KPIs/OKRs; cumplimiento de la Ley 29733; backups y recuperación (RTO/RPO). Seguridad: cifrado en reposo; cifrado en tránsito (TLS 1.3 y certificado autofirmado); hashing de contraseñas; RBAC; mínimo privilegio; expiración de sesión por inactividad; logs de auditoría; logs inmutables; política de contraseñas; capacitación y concientización (evidencia: política escrita); revocación inmediata de accesos; herramienta de análisis APLICADA; identificación de riesgos; plan de respuesta a incidentes; recomendaciones futuras. Funcionales: rol paciente; transferencia de doctor; vista de accesos del paciente; exportación de datos; consentimiento. Técnicos: front; backend; base de datos relacional; certificados digitales; despliegue. E2: DPIA; sección de ética y privacidad; informe; presentación; demo. Luego crea docs/referencias.md con la lista única de referencias del informe, con numeración, solo de la lista permitida; incluye la URL oficial solo si la conoces con certeza, si no escribe \[VERIFICAR URL\]. |
| :---- |

| TÚ (MANUAL, sin prompt) \- Pega cada sección en Notion y reemplaza "\[VERIFICAR\]" por la verificación hecha. \- Inserta el diagrama de arquitectura (Mermaid en un bloque de código de Notion) y las capturas: SELECT con datos cifrados, verificación de la cadena de logs, reportes antes/después, rotación de llaves. \- Revisa que las secciones 1 a 4 se entiendan en 15 minutos de lectura. Si suenan a lista de requisitos, pide a la IA: "reescribe en prosa explicando el porqué". \- Publica el Notion y revisa los permisos de lectura para el profesor. |
| :---- |

# **FASE 5 \- Demostración en vivo (2 a 3 horas con ensayo)**

*La rúbrica premia que la demo muestre CADA medida de seguridad en funcionamiento. Haz la demo en local (más controlable) y deja el despliegue como respaldo.*

### **Guion objetivo (10 a 12 minutos)**

| \# | Qué muestras | Medida que evidencia |
| :---- | :---- | :---- |
| 1 | App en https\://localhost:8443: certificado y versión de TLS; y que Postgres (5432) y el backend (8000) no responden desde el host | Datos en tránsito, certificado digital, aislamiento de red |
| 2 | 5 logins fallidos → bloqueo; luego login correcto | Hashing, bloqueo, detección |
| 3 | Doctor A (solo ve sus pacientes) y Doctor B (no ve al paciente demo) | RBAC, mínimo privilegio |
| 4 | Administrativo: no ve el diagnóstico (pestaña Network) | Control de acceso por campos en el servidor |
| 5 | docker compose exec db psql ...: SELECT nombre, diagnostico FROM pacientes LIMIT 3; | Cifrado en reposo (v2:...) |
| 6 | Paciente demo: su historial y quién accedió | Transparencia, derechos del titular |
| 7 | El paciente transfiere a Doctor B; B lo ve, A ya no | Gestión de acceso dinámica |
| 8 | Auditor: log de la transferencia \+ verificación de cadena OK; luego alteración y verificación que FALLA | Logs íntegros / inmutables |
| 9 | Rotación de llave en vivo (v2 → v3) y la app sigue funcionando | Gestión de llaves (pregunta del profesor) |
| 10 | Reporte ZAP/Bandit antes y después (1 minuto) | Herramienta de análisis aplicada |
| 11 | Backup cifrado y tiempo de restauración medido (opcional) | Continuidad |

### **Paso 5.1 \- Script de preparación de la demo**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 5.1 \- Preparar demo Crea scripts/preparar\_demo.sh (y .ps1 si uso Windows) que, usando Docker Compose, deje el sistema en un estado conocido: ejecuta down \-v, levanta con up \-d \--build, espera a que los servicios estén healthy, siembra los datos con las llaves actuales (perfil seed), crea 3 doctores (Dra. Ana Torres, Dr. Luis Ramírez, Dra. Carla Quispe), un administrativo, un auditor, un admin y un "Paciente Demo" asignado a la Dra. Torres con consentimiento registrado. Las contraseñas deben leerse de variables de entorno (DEMO\_PASSWORD\_\*), nunca escribirse en el repo. Al final imprime una tabla: usuario \| rol \| email (sin contraseñas) y verifica que verificar\_cadena\_logs.py y verificar\_cifrado.py (ejecutados con docker compose run \--rm backend ...) y scripts/verificar\_despliegue.sh pasan. |
| :---- |

### **Paso 5.2 \- Guion detallado**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 5.2 \- Guion Crea docs/GUION\_DEMO.md con el guion de la tabla de 11 pasos que te pego abajo. Para cada paso: URL o comando exacto, usuario a usar, qué debo ver en pantalla, y la frase de una línea que diré al público explicando qué medida de seguridad se evidencia. Añade al inicio una lista de preparación (qué abrir, en qué pestañas, en qué orden) y al final una lista de "preguntas probables y respuesta corta" (por qué GCM y no Fernet; dónde está la llave; qué pasa si se pierde; qué pasa si un doctor se va; por qué el certificado es autofirmado). Usa solo lo que existe en el repo. \[pega aquí la tabla de 11 pasos de este documento\] |
| :---- |

### **Paso 5.3 \- Demo de alteración de logs (el momento más convincente)**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 5.3 \- Alterar un log Crea scripts/demo\_alterar\_log.sql (se ejecuta como superusuario dentro del contenedor: docker compose exec \-T db psql \-U "\$POSTGRES\_USER" \-d "\$POSTGRES\_DB" \< scripts/demo\_alterar\_log.sql) que: desactive el trigger de protección de audit\_logs, modifique el campo recurso de UNA fila intermedia, y vuelva a activar el trigger. Documenta en docs/GUION\_DEMO.md el orden: (1) correr verificar\_cadena\_logs.py \-\> OK; (2) ejecutar el SQL de alteración; (3) correr verificar\_cadena\_logs.py \-\> FALLA indicando la fila alterada; (4) correr scripts/preparar\_demo.sh para restaurar un estado limpio. Aclara que esto simula a un atacante con privilegios de superusuario y que sin ese privilegio el trigger y los permisos lo impiden. |
| :---- |

### **Paso 5.4 \- Demo de rotación de llaves**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 5.4 \- Demo de rotación Crea scripts/demo\_rotacion.sh que: (1) agregue una nueva versión de llave a un archivo .env.demo (no al .env real) y la ponga como actual; (2) muestre cuántos campos hay por versión (SELECT con substring del prefijo, agrupado); (3) ejecute scripts/rotate\_keys.py; (4) vuelva a mostrar el conteo por versión (todo en la versión nueva); (5) haga una petición a la API como doctor y compruebe que los datos se leen igual. Todo con Docker: reinicia el backend con la nueva ENC\_KEY\_CURRENT usando docker compose up \-d backend y ejecuta la rotación con docker compose run \--rm backend python scripts/rotate\_keys.py. Debe ser repetible: documenta cómo volver al estado inicial con preparar\_demo.sh. |
| :---- |

### **Paso 5.5 \- Plan B y ensayo**

| TÚ (MANUAL, sin prompt) \- Graba un video de la demo completa antes del día de la entrega. Si algo falla en vivo, lo dices con naturalidad y pasas al video. \- Construye las imágenes con antelación (docker compose build) y deja todo levantado 10 minutos antes: la demo no debe depender de internet ni de descargar imágenes en vivo. \- Ensaya 2 veces seguidas con cronómetro y sin tocar código. \- Ten abiertas las pestañas en el orden del guion; usa zoom del navegador y de la terminal para que se lea. \- Guarda las contraseñas de demo en una nota aparte (no en el informe ni en el repo). \- Prepara respuesta corta a: "¿por qué GCM y no Fernet?", "¿dónde guardas la llave?", "¿qué pasa si se pierde la llave?". |
| :---- |

| VERIFICA ANTES DE SEGUIR Puedes recorrer los 11 pasos sin buscar nada ni editar código, dos veces seguidas, dentro del tiempo que te den. |
| :---- |

# **FASE 6 \- Presentación (2 horas)**

*La consigna: resumen de lo logrado en E1, evidenciar el cumplimiento de objetivos y justificar lo que no se logró. La diapositiva de objetivos vs. resultados es la que más pesa.*

### **Paso 6.1 \- Tabla de objetivos vs. resultados**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 6.1 Crea docs/objetivos\_vs\_resultados.md con una tabla de TODOS los KPIs/OKRs de la Entrega 1 (100% de campos sensibles cifrados; 0 accesos no autorizados; acceso al historial en menos de 30 segundos; 100% de accesos registrados en logs; cumplimiento de la Ley 29733; plan de respuesta a incidentes documentado y probado; detección de accesos anómalos en menos de 24 horas) con las columnas: objetivo \| resultado alcanzado (con el dato real o cómo se mide) \| estado (Cumplido / Parcial / No cumplido) \| evidencia \| si no se cumplió del todo, por qué y qué se haría. No inventes cifras: si un KPI no se puede medir en un prototipo (por ejemplo "0 incidentes en 6 meses"), dilo y propón cómo se mediría en producción. |
| :---- |

### **Paso 6.2 \- Contenido de las diapositivas**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 6.2 Con docs/ y el informe, crea docs/presentacion.md con el contenido de 12 diapositivas (título, 3 a 5 viñetas cortas máximo, y notas del orador de 3 a 4 frases en la voz de la persona que presenta), con este orden: 1\) Portada y problema en una frase; 2\) Contexto y usuarios (Ley 29733 y su Reglamento); 3\) Resumen de la Entrega 1 en UNA diapositiva (dataset, caso de negocio, KPIs, arquitectura base); 4\) Arquitectura final; 5\) Cifrado en reposo y rotación de llaves (con la corrección AES-256-GCM y por qué); 6\) Identidad y acceso, incluida la transferencia del paciente; 7\) Trazabilidad: logs encadenados y alertas; 8\) Análisis con herramientas, antes vs. después; 9\) DPIA: 3 riesgos principales y su mitigación; 10\) Objetivos vs. resultados (tabla de docs/objetivos\_vs\_resultados.md); 11\) Lo que no se logró, por qué y trabajo futuro; 12\) Lecciones aprendidas y paso a la demo. Menos texto, más tablas y capturas. Indica en cada diapositiva qué captura o diagrama va. |
| :---- |

| TÚ (MANUAL, sin prompt) Pasa ese contenido a PowerPoint o Google Slides. Si prefieres, pídeme a mí (en esta conversación) que arme las diapositivas con esa estructura cuando tengas los resultados de las Fases 1 a 3\. |
| :---- |

# **FASE 7 \- Revisión final (1.5 a 2 horas)**

### **Paso 7.1 \- Consistencia y secretos**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 7.1 \- Auditoría de consistencia Revisa todo el repositorio y los documentos de docs/ y dime (sin corregir todavía) si hay: (a) menciones a "ARDA", "Fernet", "AES-128" o "ENCRYPTION\_KEY" que ya no corresponden; (b) contradicciones de roles (por ejemplo, un documento dice que administrativo ve diagnósticos y el código no); (c) secretos, contraseñas o llaves en cualquier archivo, incluidos .md y capturas de configuración; (d) afirmaciones del informe o de docs/ que no tengan respaldo en el código (por ejemplo "logs inmutables" sin trigger); (e) cualquier \[VERIFICAR\] sin resolver; (f) referencias del informe fuera de la lista permitida. Entrégame una tabla con archivo, línea y corrección propuesta. |
| :---- |

### **Paso 7.2 \- Prueba de humo end-to-end**

| PROMPT PARA TU IA  (copia todo el cuadro) PASO 7.2 \- Smoke test Crea tests/test\_e2e\_smoke.py que, contra la API local, recorra el flujo completo con cada rol: login; lista de pacientes según rol; Administrativo sin campos clínicos; Doctor B no ve al paciente demo; el paciente transfiere a Doctor B; Doctor B ahora lo ve y Doctor A ya no; el auditor ve el evento de transferencia; la cadena de logs es válida; un token revocado deja de funcionar. Ejecútalo dentro de Docker (docker compose run \--rm sobre la red app\_net) contra la base preparada con preparar\_demo.sh y muéstrame el resultado. |
| :---- |

### **Paso 7.3 \- Cierre**

| TÚ (MANUAL, sin prompt) \- Prueba el despliegue desde cero: clona el repo en una carpeta nueva, copia .env.example a .env, genera secretos y certificado, ejecuta scripts/dev.sh reset y scripts/verificar\_despliegue.sh. Idealmente hazlo en otro equipo o en una máquina virtual para comprobar que el README basta. \- Verifica que el repo sea accesible y esté enlazado desde el informe; que no haya secretos en el historial (corre gitleaks otra vez). \- Revisa que Notion tenga permisos de lectura para el profesor y que ningún valor secreto aparezca en capturas. \- Lee en voz alta el resumen ejecutivo y las secciones 1 a 4: si algo suena a lista de requisitos, reescríbelo en prosa. \- Cierra con un tag: git tag entrega-2 && git push \--tags |
| :---- |

| VERIFICA ANTES DE SEGUIR Checklist final: informe publicado, repo enlazado, DPIA y ética incluidas, reportes antes/después, demo ensayada, presentación lista, video de respaldo grabado. |
| :---- |

# **ANEXO A \- Decisión → estándar o fuente**

*Responde al comentario "no se justifica de dónde sale el estándar". Cuando cites un artículo concreto de una ley o norma, ábrelo y compruébalo antes de escribirlo.*

| Decisión | Fuente que la respalda |
| :---- | :---- |
| AES con llave de 256 bits | FIPS 197 |
| Modo GCM (cifrado autenticado: confidencialidad \+ integridad) | NIST SP 800-38D |
| Nonce aleatorio de 96 bits, sin reutilizarlo con la misma llave | NIST SP 800-38D |
| Rotación y periodo de uso de llaves | NIST SP 800-57 Part 1 |
| TLS 1.3 en tránsito | RFC 8446; NIST SP 800-52 Rev. 2 |
| Hash de contraseñas con bcrypt (factor de costo 12\) | OWASP Password Storage Cheat Sheet |
| Política de contraseñas (longitud, sin rotación forzada, lista de contraseñas comunes) | NIST SP 800-63B |
| JWT con algoritmo fijado, exp y sub obligatorios | RFC 7519; RFC 8725 |
| RBAC y mínimo privilegio | OWASP ASVS (control de acceso); modelo RBAC de NIST |
| Registro y verificación de logs de auditoría | NIST SP 800-92; OWASP Logging Cheat Sheet; HIPAA 45 CFR 164.312(b) |
| Controles técnicos para datos de salud (referencia complementaria) | HIPAA Security Rule, 45 CFR 164.312 |
| Aislamiento y endurecimiento de contenedores (redes internas, sin root, cap\_drop) | CIS Docker Benchmark; OWASP Docker Security Cheat Sheet |
| Marco legal peruano | Ley 29733; Reglamento D.S. 016-2024-JUS; ANPD |
| Evaluación de impacto (DPIA) | GDPR art. 35; ISO/IEC 29134; Reglamento D.S. 016-2024-JUS |
| Respuesta a incidentes | NIST SP 800-61; notificación a la ANPD en 48 h (Reglamento) |

# **ANEXO B \- Textos listos para pegar en el informe**

*Úsalos como base y ajusta a lo que realmente implementaste.*

### **Cifrado en reposo (reemplaza el párrafo de Fernet / AES-256)**

Los campos sensibles (nombre, diagnóstico, medicación, resultados de pruebas y monto facturado) se cifran en la capa de aplicación con AES-256 en modo GCM (FIPS 197; NIST SP 800-38D), un esquema de cifrado autenticado que garantiza confidencialidad e integridad: cualquier alteración del texto cifrado provoca un fallo de verificación al descifrar. Cada cifrado usa un nonce aleatorio de 96 bits y se vincula al registro mediante datos asociados autenticados (tabla, campo e identificador del paciente), de modo que un valor cifrado no puede copiarse a otro registro sin ser detectado. Elegimos GCM sobre la solución inicial (Fernet, que combina AES-128-CBC con HMAC-SHA256) para alcanzar una llave de 256 bits respaldada por un estándar NIST y simplificar la justificación del diseño.

### **Rotación de llaves**

Cada valor cifrado lleva un prefijo con la versión de la llave que lo produjo (por ejemplo, v2:). El sistema mantiene un anillo de llaves: las nuevas escrituras usan siempre la versión vigente, mientras que las lecturas utilizan la versión indicada por el prefijo. Para rotar, se añade una nueva versión, se ejecuta un proceso que re-cifra todos los registros y, al verificar que ninguno conserva la versión anterior, se retira esta del entorno. La periodicidad se define según el concepto de periodo criptográfico de NIST SP 800-57, y la rotación es inmediata ante sospecha de compromiso. En producción, las llaves residirían en un servicio de gestión de llaves (KMS/HSM) con cifrado de sobre; en este prototipo se gestionan mediante variables de entorno, limitación que declaramos expresamente.

### **Autoridad y notificación de incidentes**

Ante un incidente de seguridad que comprometa datos personales, la clínica, como responsable del tratamiento, debe notificar a la Autoridad Nacional de Protección de Datos Personales (ANPD) dentro de las 48 horas de haber tomado conocimiento, e informar a los titulares afectados, conforme al Reglamento de la Ley N° 29733 (D.S. N° 016-2024-JUS). Si el incidente ocurre en un entorno digital, también corresponde reportarlo al Centro Nacional de Seguridad Digital. \[Verifica el artículo exacto en el texto oficial antes de citarlo.\]

### **Política de contraseñas**

La política se alinea con NIST SP 800-63B: longitud mínima de 12 caracteres, verificación contra contraseñas comunes o filtradas, sin reglas de composición forzadas ni expiración periódica obligatoria (solo ante sospecha de compromiso). Las contraseñas se almacenan con bcrypt con factor de costo 12, conforme al OWASP Password Storage Cheat Sheet.

# **ANEXO C \- Plan de 5 días, qué recortar y Plan B**

## **Plan sugerido de 6 días (≈ 36 horas)**

| Día | Trabajo | Horas |
| :---- | :---- | :---- |
| 1 | Fase 0 (triage) \+ Fase D (Docker: compose, certificados, verificación desde cero) | 6 |
| 2 | Pasos 1.1 a 1.4 (AES-GCM, rotación, logs encadenados, bloqueo y alertas) | 6 |
| 3 | Pasos 1.5 a 1.9 (backups, endurecimiento, vista del paciente, checkpoint) | 5 |
| 4 | Fase 2 (herramientas: antes, corregir, después) \+ Fase 3 (DPIA y ética) | 7 |
| 5 | Fase 4 (informe completo en Notion) | 6 |
| 6 | Fase 5 (demo y ensayo) \+ Fase 6 (presentación) \+ Fase 7 (revisión) | 6 |

## **Si te falta tiempo: qué recortar, en este orden**

- Paso 1.8 (acceso de emergencia): se explica en el informe como trabajo futuro y consideración ética.

- Exportación de datos del paciente (parte del paso 1.7).

- Migración a cookie HttpOnly (ya está como riesgo aceptado en 1.6c).

- Automatizar backups (deja solo la prueba manual de restauración con tiempo medido).

- Argon2id (bcrypt con costo 12 está justificado).

- Trivy y Hadolint (deja Bandit, pip-audit y ZAP como mínimo) y el endurecimiento extra de contenedores (read\_only, límites) si te rompe servicios: aflójalo y documenta por qué.

## **Qué NO recortar**

- AES-256-GCM con rotación de llaves (es lo que observó el profesor).

- Al menos dos herramientas de análisis aplicadas, con reporte antes y después.

- DPIA y la sección de ética y privacidad.

- Informe reestructurado como narrativa, con fuentes y lecciones aprendidas.

- Demo ensayada y video de respaldo.

- Despliegue reproducible: docker compose up desde un clon limpio, siguiendo solo el README.

## **Plan B si no alcanzas a migrar a AES-256-GCM (30 minutos)**

Deja Fernet, pero corrige el informe: "Fernet cifra con AES-128 en modo CBC y autentica con HMAC-SHA256 (cifrado autenticado, especificación de la librería cryptography, no un estándar NIST); la llave de 32 bytes se divide en 16 bytes para firmar y 16 para cifrar". Para la rotación usa MultiFernet.rotate(), que re-cifra un token con la primera llave de la lista. Funciona y es honesto, pero pierdes el argumento de AES-256 y el respaldo en NIST; la migración a GCM es la opción más fuerte.

## **Cuando termines cada fase**

Vuelve a esta conversación y pásame los resultados (reportes, tabla de hallazgos, DPIA). Con eso puedo revisarte el informe antes de publicarlo o armar las diapositivas de la presentación.