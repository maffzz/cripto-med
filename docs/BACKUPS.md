# Backups y recuperación — CriptoMed

> **Estado real del prototipo:** backup y restauración son operaciones manuales locales. El repositorio no configura una frecuencia, un scheduler, almacenamiento off-site, Object Lock ni WAL archiving. Las secciones de frecuencia y custodia externa que antes aparecían como política se retiran: son recomendaciones para un despliegue futuro, no controles implementados. Esta documentación no acredita cumplimiento de HIPAA ni de otro marco normativo.

**Referencias de diseño (no certificaciones):**
- **NIST SP 800-34 Rev. 1:** *Contingency Planning Guide for Federal Information Systems*.
- **NIST SP 800-57 Part 1 Rev. 5:** *Recommendation for Key Management* (Sección 8.2: *Cryptographic Key Separation*).
- **NIST SP 800-38D / FIPS 197:** *Galois/Counter Mode (GCM) & Advanced Encryption Standard (AES-256)*.
- **HIPAA Security Rule 45 CFR § 164.308(a)(7):** *Contingency Plan (Data Backup Plan & Disaster Recovery Plan)*.

---

## 1. Capacidad implementada y objetivos

| Capacidad | Estado |
| :--- | :--- |
| Formato | `pg_dump -Fc`, cifrado con GPG (AES-256) por `scripts/backup.sh` |
| Frecuencia | Manual: debe ejecutarse `./scripts/backup.sh`; no existe programación en el repositorio |
| Retención | Se conservan los 7 archivos más recientes, no siete días |
| Ubicación | `./backups/` en el host; excluir del control de versiones y proteger el host |
| Copia off-site / inmutable | No configurada |
| WAL archiving / recuperación punto-en-tiempo | No configurado |
| Objetivo de RPO | 24 horas solo si una persona ejecuta y comprueba el backup diariamente; no es una garantía actual |
| RTO observado | 3 segundos en una restauración local de prueba el 2026-11-16; no es un SLA ni una garantía para otro entorno |

Para uso real deben definirse responsables, frecuencia, destino externo, cifrado/custodia de llaves, retención aprobada y objetivos RPO/RTO; luego probarse periódicamente.

---

## 2. Cifrado y custodia de llaves: requisitos pendientes de operación

El script cifra el dump con `BACKUP_PASSPHRASE`. La separación efectiva y la recuperación de `BACKUP_PASSPHRASE` y `ENC_KEYS` dependen de la configuración del host/operador; el repositorio no integra ni evidencia un gestor KMS/Vault ni control dual. No almacenar la passphrase junto al backup.

- **Cifrado en reposo del dump**: El archivo se cifra con `gpg --symmetric --cipher-algo AES256` empleando una frase de paso de alta entropía (`BACKUP_PASSPHRASE`), generada criptográficamente por `scripts/generate_secrets.py`.
- **Doble capa de protección**:
  1. La base de datos contiene los campos sensibles de los pacientes (`nombre`, `diagnostico`, `monto_facturado`, `medicacion`, `resultado_test`) ya cifrados a nivel de aplicación con **AES-256-GCM** y llaves versionadas ligadas a contexto (**AAD**).
  2. El volcado completo (`pg_dump`) se encuentra a su vez encapsulado y cifrado con **AES-256 simétrico vía GPG**.
- **Pendiente antes de producción:** custodiar ambos secretos en un gestor apropiado, con acceso restringido y procedimiento probado de recuperación. Si la clave de cifrado de campos no está disponible, los datos cifrados restaurados no podrán descifrarse.

---

## 3. Procedimientos Operativos

### 3.1 Ejecución manual de backup
Ejecuta el script host que orquesta el contenedor `backup` (profile `tools`):
```bash
./scripts/backup.sh
```
*En entornos Windows PowerShell:*
```powershell
.\scripts\backup.ps1
```

### 3.2 Restauración Controlada en Entorno Aislado
Para validar la operatividad sin afectar la base de producción (`criptomed`), la restauración se efectúa siempre sobre una base de datos de contingencia separada: `criptomed_restore_test`.
```bash
./scripts/restore.sh backups/backup_YYYY-MM-DD_HHMM.dump.gpg
```
*En entornos Windows PowerShell:*
```powershell
.\scripts\restore.ps1 backups\backup_YYYY-MM-DD_HHMM.dump.gpg
```

### 3.3 Verificación Forense Posterior a la Restauración
Compara conteos tabla por tabla, valida criptográficamente cada eslabón de la cadena de auditoría SHA-256 y verifica el descifrado de pacientes con AAD:
```bash
docker compose run --rm backend python scripts/verificar_restauracion.py
```

---

## 4. Evidencia de backup y restauración en esta revisión

El **2026-11-16** se generó un backup cifrado y se restauró en `criptomed_restore_test`, sin reemplazar la base principal. La restauración tomó **3 segundos** según el script; es una observación local, no un SLA ni una garantía de recuperación. El archivo queda en `backups/` (excluido de Git) y debe protegerse en el host.

| Parámetro | Resultado observado |
| :--- | :--- |
| **Archivo** | `backups/backup_2026-11-16_1232.dump.gpg` |
| **Cifrado / tamaño** | GPG simétrico AES-256 / aproximadamente 293 KiB |
| **Restauración** | Completada en 3 segundos en `criptomed_restore_test` |
| **Conteos comparados** | usuarios 7/7; pacientes 501/501; audit_logs 70/70; diagnosticos_cie10 14.409/14.409 |
| **Integridad y descifrado** | 70 eventos de auditoría validados; 5/5 pacientes de muestra descifrados con las llaves/AAD actuales |
| **RPO** | No medido ni garantizado; depende de ejecutar y comprobar backups. WAL archiving no está configurado |

La comprobación requirió corregir en `backend/scripts/verificar_restauracion.py` una evaluación booleana inválida de una expresión SQLAlchemy. La restauración y verificación terminaron correctamente tras el cambio. La base aislada de prueba permanece en el volumen local; la base principal no se reemplazó.

## 5. Evidencia histórica de restauración

La prueba del **2026-11-04** se conserva solo como referencia histórica. No debe confundirse con la evidencia actual ni con un SLA.

| Parámetro | Valor Obtenido en Prueba | Estándar / KPI |
| :--- | :--- | :--- |
| **Fecha y Hora de la Prueba** | 2026-11-04 14:42 UTC-5 | NIST SP 800-34 |
| **Archivo de Respaldo Generado** | `backups/backup_2026-11-04_1442.dump.gpg` | GPG AES-256 |
| **Tamaño del Respaldo Cifrado** | **284 KB** (500 pacientes + 14,409 códigos CIE-10 + 5 logs) | Compresión -Fc + GPG |
| **Duración del Proceso de Backup** | **2 segundos** | < 1 minuto |
| **Tiempo de Restauración (medición histórica)** | **1 segundo** | No implica RTO vigente |
| **RPO** | No medido; depende de la frecuencia real de backups | Sin garantía actual; WAL archiving no configurado |
| **Base de Datos Destino de Prueba** | `criptomed_restore_test` | Aislada de producción |

### Resultados de Integridad Forense (`verificar_restauracion.py`):
- **usuarios**: 2 / 2 (100% recuperado)
- **pacientes**: 500 / 500 (100% recuperado)
- **diagnosticos_cie10**: 14,409 / 14,409 (100% recuperado)
- **audit_logs**: 5 / 5 (100% recuperado)
- **Cadena de Auditoría SHA-256**: 5/5 eslabones validados en esa prueba histórica.
- **Descifrado de Pacientes (AES-256-GCM + AAD)**: Muestra de 5 pacientes descifrada exitosamente con las llaves vigentes del anillo `ENC_KEYS`.
