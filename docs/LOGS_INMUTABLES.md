# Diseño de Logs de Auditoría Inmutables y Verificables

**Proyecto:** CriptoMed — DS3031 Ética y Seguridad de los Datos  
**Estándares y Referencias:**
- **NIST SP 800-92:** *Guide to Computer Security Log Management* (Integridad de registros y protección de trazas forenses).
- **OWASP Logging Cheat Sheet:** *Tamper-evident logging and log protection*.
- **HIPAA Security Rule 45 CFR 164.312(b):** *Audit Controls*.

---

## 1. Problema de Seguridad y Justificación
En la arquitectura inicial de Entrega 1, la tabla `audit_logs` era una tabla estándar de base de datos relacional. En ese modelo, un atacante o usuario interno con privilegios elevados podía:
1. Modificar campos (ej. alterar el `usuario_id` o `recurso`) para encubrir exfiltraciones de datos médicos.
2. Eliminar selectivamente filas de acceso a historias clínicas sin dejar traza alguna.
3. Truncar la tabla completa tras una intrusión.

Para resolver esto conforme a **NIST SP 800-92** y el **OWASP Logging Cheat Sheet**, se implementó un mecanismo dual de:
1. **Detección Criptográfica de Alteraciones (Tamper-evident):** Encadenamiento secuencial de hashes SHA-256 (cadena tipo blockchain).
2. **Prevención Operativa de Modificaciones (Tamper-resistant):** Triggers PostgreSQL a nivel de motor y asignación de mínimo privilegio al usuario de la aplicación.

---

## 2. Arquitectura de la Cadena de Hashes (SHA-256)

Cada fila insertada en `audit_logs` contiene dos campos criptográficos fundamentales:
- `hash_prev`: Hash SHA-256 de la fila cronológicamente anterior (`seq - 1`).
- `hash_actual`: Hash SHA-256 calculado a partir del contenido íntegro del evento actual concatenado con `hash_prev`.

```
[ Registro seq = 1 (Génesis) ]
  hash_prev   : "0" * 64
  datos       : [ usuario_id | accion | recurso | ts_iso | ip | detalle ]
  hash_actual : SHA-256( hash_prev | datos )
        │
        ▼
[ Registro seq = 2 ]
  hash_prev   : hash_actual de seq 1
  datos       : [ usuario_id | accion | recurso | ts_iso | ip | detalle ]
  hash_actual : SHA-256( hash_prev | datos )
        │
        ▼
[ Registro seq = 3 ]
  hash_prev   : hash_actual de seq 2
  ...
```

### 2.1 Fórmula Canónica de Hash
```text
hash_actual = SHA-256( hash_prev | usuario_id | accion | recurso | timestamp_iso | ip_origen | detalle )
```
- **Separador:** Carácter `|`.
- **Valores nulos:** Se representan como cadena vacía `""`.
- **Timestamp:** Formato estricto ISO-8601 UTC en microsegundos (`%Y-%m-%dT%H:%M:%S.%fZ`).

### 2.2 Serialización Atómica de Escrituras
Para prevenir condiciones de carrera en entornos multihilo o peticiones HTTP simultáneas, la función centralizada `log_action(...)` en `app/audit.py` adquiere un candado transaccional en PostgreSQL:
```sql
SELECT pg_advisory_xact_lock(42424242);
```
El bloqueo se libera automáticamente al confirmarse la transacción (`commit`), garantizando una secuencia lineal estricta y sin bifurcaciones en `seq`.

---

## 3. Capa de Prevención en Base de Datos (Triggers y Roles)

A nivel de PostgreSQL se implementaron dos barreras complementarias en [`scripts/sql/proteger_audit_logs.sql`](file:///Users/chrisperez/Downloads/cripto-med/scripts/sql/proteger_audit_logs.sql):

1. **Trigger de Fila (`BEFORE UPDATE OR DELETE`):**
   ```sql
   CREATE TRIGGER trigger_bloqueo_modificacion_audit_logs
   BEFORE UPDATE OR DELETE ON audit_logs
   FOR EACH ROW EXECUTE FUNCTION proteger_audit_logs_func();
   ```
   Cualquier sentencia `UPDATE` o `DELETE` lanzará una excepción y abortará inmediatamente la transacción.

2. **Trigger de Sentencia (`BEFORE TRUNCATE`):**
   ```sql
   CREATE TRIGGER trigger_bloqueo_truncate_audit_logs
   BEFORE TRUNCATE ON audit_logs
   EXECUTE FUNCTION proteger_audit_logs_truncate_func();
   ```
   Impide el vaciado masivo de la tabla mediante `TRUNCATE TABLE audit_logs;`.

3. **Mínimo Privilegio de la Aplicación (`app_user`):**
   El backend opera en producción con el usuario de base de datos `app_user`, al cual se le otorga:
   - `GRANT SELECT, INSERT ON audit_logs TO app_user;`
   - `REVOKE UPDATE, DELETE, TRUNCATE ON audit_logs FROM app_user;`

---

## 4. Verificación Forense (`scripts/verificar_cadena_logs.py`)

La integridad se audita en cualquier momento ejecutando el script forense:
```bash
docker compose run --rm backend python scripts/verificar_cadena_logs.py
```
El script recorre todos los eventos ordenados por `seq`:
1. Comprueba que `hash_prev` de la fila actual coincida exactamente con `hash_actual` de la fila anterior.
2. Recalcula el SHA-256 de los datos de la fila y valida que sea idéntico a `hash_actual`.
3. Ante la menor discrepancia (un solo carácter modificado o una fila eliminada), se detiene, imprime el número de secuencia `seq` y el `id` de la fila alterada, y termina con código de salida `1`.

---

## 5. Límites Declarados y Mitigación Futura

> [!IMPORTANT]
> **Límites de Seguridad (Modelo de Amenazas):**
> Si un adversario obtiene acceso total como **superusuario de PostgreSQL (`postgres`)** o acceso como `root` al servidor físico:
> - Podría deshabilitar temporalmente los triggers (`ALTER TABLE audit_logs DISABLE TRIGGER ALL;`).
> - Podría modificar un registro intermedio y **recalcular toda la cadena de hashes subsiguiente** hasta el final, generando una cadena matemáticamente válida en apariencia.

### Mitigación Futura (Trabajo Futuro):
- **Anclaje Periódico Externo (*Hash Anchoring*):** Publicar periódicamente (ej. cada hora o diariamente) el último `hash_actual` en un servicio de almacenamiento inmutable de escritura única WORM (*Write Once Read Many*, como AWS S3 Object Lock) o un servicio público de sellado de tiempo criptográfico (RFC 3161). De este modo, un atacante no podría reescribir la cadena histórica porque no coincidiría con el hash ya anclado externamente.
