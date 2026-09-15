# Guía de Configuración de Base de Datos - CriptoMed

Esta guía explica paso a paso cómo configurar PostgreSQL en Docker y cargar los datos iniciales para el proyecto CriptoMed.

## Requisitos Previos

- Docker Desktop instalado y corriendo
- Python 3.12+ instalado
- Git (para clonar el repositorio)

## Paso 1: Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd cripto-med
```

## Paso 2: Crear el Entorno Virtual de Python

```bash
python3 -m venv .venv
source .venv/bin/activate  # En Linux/Mac
# o
.venv\Scripts\activate  # En Windows
```

## Paso 3: Instalar Dependencias

```bash
pip install -r backend/requirements.txt
```

## Paso 4: Configurar Variables de Entorno

El archivo `.env.example` contiene las variables de configuración. Cópialo a `.env`:

```bash
cp .env.example .env
```

**Importante:** El archivo `.env` ya está configurado con:
- `DATABASE_URL=postgresql://criptomed:criptomed123@127.0.0.1:5433/criptomed`
- `JWT_SECRET`, `ENCRYPTION_KEY`, etc.

No modificar el puerto 5433 (se usa para evitar conflictos con PostgreSQL local).

## Paso 5: Iniciar PostgreSQL en Docker

```bash
docker compose up -d
```

Esto inicia un contenedor PostgreSQL con:
- Usuario: `criptomed`
- Contraseña: `criptomed123`
- Base de datos: `criptomed`
- Puerto: `5433` (mapeado al host)

### Verificar que el contenedor esté corriendo

```bash
docker compose ps
```

Deberías ver el contenedor `criptomed_db` con estado `Up` y `healthy`.

## Paso 6: Crear las Tablas de la Base de Datos

```bash
python backend/scripts/setup_db_docker.py
```

Este script crea las siguientes tablas:
- `usuarios`
- `pacientes`
- `diagnosticos_cie10`
- `audit_logs`

**Salida esperada:**
```
=== script de configuracion de tablas para criptomed (docker) ===
este script creara las tablas en postgresql usando docker

tablas creadas exitosamente:
  - usuarios
  - pacientes
  - diagnosticos_cie10
  - audit_logs

=== configuracion completada exitosamente ===
ahora puedes ejecutar el script seed_db.py para cargar los datos de ejemplo
```

## Paso 7: Cargar los Datos Iniciales (Seed)

```bash
python backend/scripts/seed_db.py
```

Este script:
1. Carga los diagnósticos CIE-10 desde `data/cie10.csv`
2. Carga los pacientes desde `data/healthcare_dataset_mapped.csv` (cifrando campos sensibles)
3. Crea 4 usuarios iniciales con contraseñas hasheadas

**Salida esperada:**
```
=== script de carga de datos para criptomed ===
este script cargara los datos de ejemplo en la base de datos

--- paso 1: cargar diagnosticos cie10 ---
se cargaron 14409 diagnosticos cie10

--- paso 2: cargar pacientes ---
se cargaron 55500 pacientes

--- paso 3: crear usuarios iniciales ---
se crearon 4 usuarios iniciales

--- verificacion de datos ---
usuarios en bd: 4
pacientes en bd: 55500
diagnosticos cie10 en bd: 14409

ejemplo de paciente:
  nombre (cifrado): gAAAAABqqU7NcwJ9EEPbBSWhsFg0Dugi1meCY_NzYhB6eWa79t...
  nombre (descifrado): Bobby JacksOn...
  edad: 30
  genero: Male

=== carga de datos completada exitosamente ===
```

## Usuarios Iniciales

| Email                  | Contraseña | Rol           |
|------------------------|------------|---------------|
| admin@criptomed.com    | admin123   | admin         |
| doctor@criptomed.com   | doctor123  | doctor        |
| admin@clinica.com      | admin123   | administrativo|
| auditor@criptomed.com  | auditor123 | auditor       |

## Campos Cifrados

Los siguientes campos de la tabla `pacientes` están cifrados con AES-256 (Fernet):
- `nombre`
- `diagnostico`
- `monto_facturado`
- `medicacion`
- `resultado_test`

## Solución de Problemas

### Error: "docker compose up -d" falla

**Causa:** Docker Desktop no está corriendo.

**Solución:**
1. Abre Docker Desktop
2. Espera a que esté completamente iniciado
3. Ejecuta `docker compose up -d` de nuevo

### Error: "role 'criptomed' does not exist"

**Causa:** El contenedor PostgreSQL no se inicializó correctamente.

**Solución:**
```bash
docker compose down -v
docker compose up -d
```

Esto elimina el volumen y recrea el contenedor desde cero.

### Error: "No module named 'sqlalchemy'"

**Causa:** Las dependencias no están instaladas en el entorno virtual.

**Solución:**
```bash
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### Error: Puerto 5432 ya está en uso

**Causa:** Ya tienes PostgreSQL local (Homebrew) corriendo en el puerto 5432.

**Solución:** El proyecto usa el puerto 5433 en la configuración. Asegúrate de que el `.env` tenga:
```
DATABASE_URL=postgresql://criptomed:criptomed123@127.0.0.1:5433/criptomed
```

### Error: "cannot import name 'Base' from 'app.database'"

**Causa:** El archivo `backend/app/database.py` tiene errores de sintaxis.

**Solución:** Verifica que `database.py` exporte `Base` con mayúscula:
```python
Base = declarative_base()
```

## Detener PostgreSQL

Para detener el contenedor PostgreSQL:

```bash
docker compose down
```

Para detener y eliminar los datos (volumen):

```bash
docker compose down -v
```

**Advertencia:** `docker compose down -v` elimina todos los datos de la base de datos. Úsalo solo si quieres reiniciar desde cero.

## Verificar Conexión a la Base de Datos

Para verificar que puedes conectarte a PostgreSQL:

```bash
docker exec -it criptomed_db psql -U criptomed -d criptomed -c "\dt"
```

Esto debería mostrar las 4 tablas creadas.

## Próximos Pasos

Una vez que la base de datos esté configurada:

1. Iniciar el backend FastAPI:
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

2. Configurar el frontend React (documentación pendiente)

3. Probar la autenticación y los endpoints

## Archivos Importantes

- `docker-compose.yml`: Configuración de Docker Compose para PostgreSQL
- `.env`: Variables de entorno (no subir a git)
- `.env.example`: Plantilla de variables de entorno
- `backend/app/database.py`: Configuración de SQLAlchemy
- `backend/app/models.py`: Modelos de la base de datos
- `backend/app/crypto.py`: Funciones de cifrado/descifrado
- `backend/scripts/setup_db_docker.py`: Script para crear tablas
- `backend/scripts/seed_db.py`: Script para cargar datos iniciales
