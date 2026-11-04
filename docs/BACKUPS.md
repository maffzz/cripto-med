# Política de Backups y Plan de Contingencia — CriptoMed

**Estándares y Marcos de Referencia:**
- **NIST SP 800-34 Rev. 1:** *Contingency Planning Guide for Federal Information Systems*.
- **NIST SP 800-57 Part 1 Rev. 5:** *Recommendation for Key Management* (Sección 8.2: *Cryptographic Key Separation*).
- **NIST SP 800-38D / FIPS 197:** *Galois/Counter Mode (GCM) & Advanced Encryption Standard (AES-256)*.
- **HIPAA Security Rule 45 CFR § 164.308(a)(7):** *Contingency Plan (Data Backup Plan & Disaster Recovery Plan)*.

---

## 1. Política y Periodicidad de Respaldos

Siguiendo la arquitectura de resiliencia establecida en la Entrega 1 y los lineamientos de NIST SP 800-34:

| Tipo de Respaldo | Frecuencia | Ventana Horaria | Formato y Retención |
| :--- | :--- | :--- | :--- |
| **Respaldo Completo Semanal** | Domingos | 02:00 AM (UTC-5) | `pg_dump -Fc` cifrado con GPG (AES-256). Retención: 4 semanas (1 mes). |
| **Respaldo Diario** | Lunes a Sábado | 02:00 AM (UTC-5) | `pg_dump -Fc` cifrado con GPG (AES-256). Retención: últimos 7 días. |

### Destino de Almacenamiento
1. **Volumen Local Aislado**: Carpeta local `./backups/` en el host (excluida del control de versiones mediante `.gitignore`).
2. **Réplica Secundaria Fuera de Sitio (Off-site)**: Los respaldos se sincronizan periódicamente a un bucket S3 / Cloud Storage inmutable (con *Object Lock* y ciclo de vida de 30 días) en una región geográfica separada.

---

## 2. Aislamiento y Separación Criptográfica de Llaves (NIST SP 800-57)

> [!CRITICAL]
> **Regla de Separación Criptográfica Estricta:**
> Las llaves criptográficas utilizadas para cifrar los datos en reposo (`ENC_KEYS`) y la frase de paso del respaldo (`BACKUP_PASSPHRASE`) **NUNCA** se almacenan ni se transmiten junto con los archivos de dump de la base de datos (`*.dump.gpg`).

- **Cifrado en reposo del dump**: El archivo se cifra con `gpg --symmetric --cipher-algo AES256` empleando una frase de paso de alta entropía (`BACKUP_PASSPHRASE`), generada criptográficamente por `scripts/generate_secrets.py`.
- **Doble capa de protección**:
  1. La base de datos contiene los campos sensibles de los pacientes (`nombre`, `diagnostico`, `monto_facturado`, `medicacion`, `resultado_test`) ya cifrados a nivel de aplicación con **AES-256-GCM** y llaves versionadas ligadas a contexto (**AAD**).
  2. El volcado completo (`pg_dump`) se encuentra a su vez encapsulado y cifrado con **AES-256 simétrico vía GPG**.
- **Gestión de contingencia de secretos**:
  - `BACKUP_PASSPHRASE` y `ENC_KEYS` se custodian en un gestor de secretos empresarial (KMS / HashiCorp Vault / 1Password for Teams) con control de acceso dual (*Split Knowledge / Two-person control*).
  - Un atacante que obtenga una copia del archivo `.dump.gpg` requeriría romper el cifrado AES-256 de GPG, y aun logrando descifrar el dump, solo obtendría texto cifrado con AES-GCM sin acceso al anillo `ENC_KEYS`.

---

## 3. Procedimientos Operativos

### 3.1 Ejecución de Backup Manual o Programado
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

## 4. Evidencia de Prueba de Restauración y RTO Medido

Prueba oficial de contingencia y recuperación realizada en el entorno de desarrollo y validación:

| Parámetro | Valor Obtenido en Prueba | Estándar / KPI |
| :--- | :--- | :--- |
| **Fecha y Hora de la Prueba** | 2026-11-04 14:42 UTC-5 | NIST SP 800-34 |
| **Archivo de Respaldo Generado** | `backups/backup_2026-11-04_1442.dump.gpg` | GPG AES-256 |
| **Tamaño del Respaldo Cifrado** | **284 KB** (500 pacientes + 14,409 códigos CIE-10 + 5 logs) | Compresión -Fc + GPG |
| **Duración del Proceso de Backup** | **2 segundos** | < 1 minuto |
| **Tiempo de Restauración (RTO Medido)** | **1 segundo** | **RTO < 5 minutos (Superado ampliamente)** |
| **RPO Objetivo** | 24 horas (respaldo diario) / Transaccional (WAL archiving) | Cumplido |
| **Base de Datos Destino de Prueba** | `criptomed_restore_test` | Aislada de producción |

### Resultados de Integridad Forense (`verificar_restauracion.py`):
- **usuarios**: 2 / 2 (100% recuperado)
- **pacientes**: 500 / 500 (100% recuperado)
- **diagnosticos_cie10**: 14,409 / 14,409 (100% recuperado)
- **audit_logs**: 5 / 5 (100% recuperado)
- **Cadena de Auditoría SHA-256**: 5/5 eslabones validados criptográficamente; ningún registro alterado ni roto tras la restauración.
- **Descifrado de Pacientes (AES-256-GCM + AAD)**: Muestra de 5 pacientes descifrada exitosamente con las llaves vigentes del anillo `ENC_KEYS`.
