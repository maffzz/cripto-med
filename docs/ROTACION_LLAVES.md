# Procedimiento Operativo: Rotación de Llaves de Cifrado en Reposo

**Proyecto:** CriptoMed — DS3031 Ética y Seguridad de los Datos  
**Estándares y Referencias:**
- **NIST SP 800-57 Part 1 (Rev. 5):** *Recommendation for Key Management — Cryptoperiod & Key Transitions*.
- **FIPS 197:** *Advanced Encryption Standard (AES)*.
- **NIST SP 800-38D:** *Galois/Counter Mode (GCM)*.

---

## 1. Fundamentos y Política de Rotación

### 1.1 Periodo Criptográfico (Cryptoperiod)
Conforme a **NIST SP 800-57 Part 1**, el periodo criptográfico es el lapso durante el cual una clave criptográfica específica está autorizada para ser utilizada por los sistemas legítimos. Para la protección de datos médicos sensibles en reposo mediante AES-256:
- **Rotación Ordinaria (Periódica):** Cada **12 meses**. Limita la cantidad de texto plano protegido por una sola clave y reduce la ventana de exposición en caso de compromiso desapercibido.
- **Rotación Extraordinaria (Inmediata):** Obligatoria ante cualquier sospecha o evidencia de compromiso de credenciales, brecha de seguridad física/lógica, o baja del personal con acceso a variables de entorno.

### 1.2 Principio de Conservación y Respaldo Independiente
> [!WARNING]
> **Regla Crítica de Recuperación:** Las llaves históricas (`v1`, `v2`, etc.) **nunca deben eliminarse** antes de concluir satisfactoriamente la migración de todos los registros en base de datos. Si una llave se retira prematuramente del anillo, los registros que aún dependan de ella se vuelven **matemáticamente irrecuperables**.
> 
> Las llaves criptográficas deben respaldarse **POR SEPARADO** de los respaldos de la base de datos (pg_dump), evitando que un atacante que comprometa un volcado obtenga simultáneamente el material de descifrado.

---

## 2. Procedimiento de Rotación en 3 Pasos

El sistema CriptoMed utiliza un esquema de **anillo de llaves versionadas** (`ENC_KEYS`) con prefijo identificador (`kid:payload`). La llave activa (`ENC_KEY_CURRENT`) cifra las nuevas inserciones y actualizaciones, mientras que el anillo permite descifrar registros en versiones históricas durante la ventana de transición.

### Paso 1: Generación y Expansión del Anillo
1. Generar una nueva llave de 32 bytes (256 bits) en formato `base64url`:
   ```bash
   docker compose run --rm backend python scripts/generate_keys.py
   ```
   *(Ejemplo de salida: `Xk8s9B...32bytes...`)*

2. En el archivo `.env` del entorno operativo:
   - Mantener las llaves existentes en `ENC_KEYS` y añadir la nueva con el siguiente identificador secuencial (ej. `v3`).
   - Actualizar `ENC_KEY_CURRENT` apuntando a la nueva versión.
   ```ini
   # Anillo de llaves con versiones históricas y nueva versión:
   ENC_KEYS=v1:...,v2:...,v3:<nueva_llave_base64url>
   ENC_KEY_CURRENT=v3
   ```

3. Reiniciar el backend para cargar el nuevo anillo en memoria:
   ```bash
   docker compose up -d backend
   ```
   *A partir de este instante, todas las escrituras nuevas usarán automáticamente `v3`, mientras que las lecturas de pacientes existentes con `v2` o `v1` siguen funcionando sin interrupción.*

---

### Paso 2: Re-cifrado en Lotes de la Base de Datos
El script `scripts/rotate_keys.py` recorre la tabla `pacientes` procesando en lotes (`--batch-size 500`) con transacciones aisladas por lote, descifrando con la versión original y re-cifrando hacia `ENC_KEY_CURRENT`.

1. **Simulación previa (Dry-Run):**
   Verifica que todos los registros puedan descifrarse correctamente sin aplicar cambios en disco:
   ```bash
   docker compose run --rm backend python scripts/rotate_keys.py --dry-run
   ```

2. **Ejecución en Caliente:**
   Aplica la migración definitiva de todos los campos sensibles (`nombre`, `diagnostico`, `monto_facturado`, `medicacion`, `resultado_test`):
   ```bash
   docker compose run --rm backend python scripts/rotate_keys.py
   ```
   *El script es 100% idempotente: ejecutarlo nuevamente reportará 0 campos modificados y no alterará los datos.*

---

### Paso 3: Verificación Criptográfica y Retiro de Llave Antigua
1. **Comprobar en PostgreSQL que ningún registro conserva versiones anteriores:**
   Conéctate a la base de datos y ejecuta la consulta de auditoría:
   ```bash
   docker compose exec db psql -U criptomed -d criptomed -c "
   SELECT count(*) AS registros_sin_migrar 
   FROM pacientes 
   WHERE nombre NOT LIKE 'v3:%' 
      OR diagnostico NOT LIKE 'v3:%' 
      OR monto_facturado NOT LIKE 'v3:%';
   "
   ```
   **Criterio de Aceptación:** El resultado debe ser exactamente `0`.

2. **Ejecutar el script de verificación integral:**
   ```bash
   docker compose run --rm backend python scripts/verificar_cifrado.py
   ```

3. **Retiro Seguro de la Llave Histórica:**
   Una vez verificado que el 100% de los registros están migrados a `v3`, edita `.env` para retirar `v1` (o la llave dada de baja):
   ```ini
   ENC_KEYS=v2:...,v3:...
   ENC_KEY_CURRENT=v3
   ```
   Reinicia el backend para aplicar la desincorporación definitiva:
   ```bash
   docker compose up -d backend
   ```

---

## 3. Limitaciones Actuales y Trabajo Futuro

| Aspecto | Implementación Actual (Prototipo) | Producción Recomendada |
|---|---|---|
| **Almacenamiento de Llaves** | Variables de entorno (`.env` local) en contenedor Docker. | Gestor centralizado KMS/HSM (AWS KMS, GCP Cloud KMS o HashiCorp Vault). |
| **Esquema de Cifrado** | AES-256-GCM directo con llaves maestras en anillo. | Cifrado de sobre (*Envelope Encryption*) mediante DEK (Data Encryption Key) por paciente y KEK (Key Encryption Key) en HSM. |
| **Automatización** | Disparado manualmente mediante script operativo CLI. | Job programado en CI/CD o orquestador de tareas periódicas con monitoreo y alertas. |
