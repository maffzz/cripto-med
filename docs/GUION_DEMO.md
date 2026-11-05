# Guion de Demostración - CriptoMed

**Duración estimada:** 10-12 minutos  
**Enfoque:** Mostrar CADA medida de seguridad en funcionamiento  
**Entorno:** Local (https://localhost:8443) con Docker Compose

---

## Preparación antes de la demo

**Abrir en este orden:**
1. Terminal 1: Ejecutar `./scripts/preparar_demo.sh` y dejarlo listo
2. Terminal 2: `docker compose logs -f` (para ver logs en tiempo real si es necesario)
3. Terminal 3: Pestaña para comandos SQL: `docker compose exec db psql -U criptomed -d criptomed`
4. Navegador: https://localhost:8443 (aceptar certificado autofirmado)
5. Navegador - Pestaña Network (DevTools) abierta

**Usuarios de demo (contraseña: ver .env):**
- admin@criptomed.local (admin)
- ana.torres@criptomed.local (doctor - Dra. Ana Torres) - tiene al Paciente Demo
- luis.ramirez@criptomed.local (doctor - Dr. Luis Ramírez) - NO tiene al Paciente Demo
- admin1@criptomed.local (administrativo)
- auditor1@criptomed.local (auditor)
- paciente1@criptomed.local (paciente - Paciente Demo)

---

## Guion de 11 pasos

### Paso 1: TLS 1.3 y aislamiento de red

**URL:** https://localhost:8443  
**Comando terminal:** `openssl s_client -connect localhost:8443 -tls1_3`  
**Comando terminal:** `curl -v http://localhost:5432` (debe fallar)  
**Comando terminal:** `curl -v http://localhost:8000` (debe fallar)

**Qué ver en pantalla:**
- Navegador muestra advertencia de certificado autofirmado (aceptar)
- Navegador DevTools → Security muestra TLS 1.3 negociado
- `openssl s_client` muestra "TLSv1.3" y cipher suite moderno
- `curl` a puertos 5432 y 8003 falla con "Connection refused"

**Frase para el público:**
> "Primero, muestro que el tráfico está protegido con TLS 1.3 exclusivo y que los puertos de base de datos y backend no son accesibles desde el host, evidenciando aislamiento de red."

**Medida de seguridad evidenciada:** Datos en tránsito, certificado digital, aislamiento de red

---

### Paso 2: Bloqueo por intentos fallidos

**URL:** https://localhost:8443  
**Usuario:** admin@criptomed.local  
**Acción:** Intentar login 5 veces con contraseña incorrecta, luego login correcto

**Qué ver en pantalla:**
- Después del 5to intento fallido, mensaje de bloqueo temporal
- Intento #6 falla incluso con contraseña correcta
- Esperar 15 minutos o resetear con `docker compose exec backend python -c "from app.database import SessionLocal; from app.models import Usuario; db = SessionLocal(); u = db.query(Usuario).filter(Usuario.email == 'admin@criptomed.local').first(); u.bloqueado_hasta = None; u.intentos_fallidos = 0; db.commit(); print('Desbloqueado')"`
- Login correcto ahora funciona

**Frase para el público:**
> "El sistema bloquea automáticamente tras 5 intentos fallidos para prevenir ataques de fuerza bruta, conforme a NIST SP 800-63B."

**Medida de seguridad evidenciada:** Hashing, bloqueo, detección

---

### Paso 3: RBAC - Doctor A ve solo sus pacientes

**URL:** https://localhost:8443  
**Usuario:** ana.torres@criptomed.local (Dra. Ana Torres)  
**Acción:** Login y ver lista de pacientes

**Qué ver en pantalla:**
- Dashboard muestra solo pacientes asignados a Dra. Ana Torres
- Paciente Demo aparece en la lista

**Frase para el público:**
> "Los doctores solo ven los pacientes que tienen asignados, implementando el principio de mínimo privilegio."

**Medida de seguridad evidenciada:** RBAC, mínimo privilegio

---

### Paso 4: Doctor B NO ve al paciente demo

**URL:** https://localhost:8443  
**Usuario:** luis.ramirez@criptomed.local (Dr. Luis Ramírez)  
**Acción:** Login y ver lista de pacientes

**Qué ver en pantalla:**
- Dashboard NO muestra Paciente Demo (no está asignado a Dr. Luis Ramírez)
- Solo muestra pacientes asignados a Dr. Luis Ramírez (si tiene alguno)

**Frase para el público:**
> "Dra. Ana Torres tiene al Paciente Demo, pero Dr. Luis Ramírez no lo ve. Esto confirma que el filtrado por rol funciona en el servidor, no solo en el frontend."

**Medida de seguridad evidenciada:** Control de acceso por campos en el servidor

---

### Paso 5: Cifrado en reposo (v2:...)

**Comando terminal:** `docker compose exec db psql -U criptomed -d criptomed -c "SELECT nombre, diagnostico FROM pacientes LIMIT 3;"`

**Qué ver en pantalla:**
- Los campos nombre y diagnostico muestran valores cifrados con prefijo "v2:" (ej: "v2:gAAAAABl...")
- Los datos no son legibles en texto claro

**Frase para el público:**
> "Los campos sensibles como nombre y diagnóstico están cifrados con AES-256-GCM en reposo. El prefijo v2 indica la versión de la llave usada."

**Medida de seguridad evidenciada:** Cifrado en reposo

---

### Paso 6: Paciente ve su historial y quién accedió

**URL:** https://localhost:8443  
**Usuario:** paciente1@criptomed.local (Paciente Demo)  
**Acción:** Login, ver historial, ver accesos

**Qué ver en pantalla:**
- Dashboard muestra historial completo del Paciente Demo
- Sección "Mis accesos" muestra lista de quién accedió (Dra. Ana Torres, fechas, IPs)

**Frase para el público:**
> "El paciente puede ver su historial completo y quién ha accedido a sus datos, cumpliendo con los derechos de acceso y transparencia de la Ley 29733."

**Medida de seguridad evidenciada:** Transparencia, derechos del titular

---

### Paso 7: Transferencia self-service

**URL:** https://localhost:8443  
**Usuario:** paciente1@criptomed.local (Paciente Demo)  
**Acción:** Transferir historial a Dr. Luis Ramírez

**Qué ver en pantalla:**
- Paciente selecciona "Transferir doctor"
- Elige Dr. Luis Ramírez de la lista
- Confirma la transferencia
- Mensaje de éxito

**Luego:** Login como luis.ramirez@criptomed.local → Ahora ve Paciente Demo  
**Luego:** Login como ana.torres@criptomed.local → Ya NO ve Paciente Demo

**Frase para el público:**
> "El paciente puede transferir su historial a otro doctor sin intervención administrativa. Dr. Luis Ramírez ahora ve al paciente y Dra. Ana Torres ya no. La transferencia queda registrada en logs."

**Medida de seguridad evidenciada:** Gestión de acceso dinámica

---

### Paso 8: Logs inmutables (cadena SHA-256)

**Comando terminal:** `docker compose run --rm backend python scripts/verificar_cadena_logs.py`

**Qué ver en pantalla:**
- Script reporta "Cadena de logs válida" con número de registros
- Todos los hashes verifican correctamente

**Luego:** Ejecutar `scripts/demo_alterar_log.sql` (ver Paso 5.3)  
**Luego:** `docker compose run --rm backend python scripts/verificar_cadena_logs.py`  
**Qué ver en pantalla:**
- Script reporta "Cadena de logs rota" con el registro alterado
- Muestra el seq del registro alterado

**Frase para el público:**
> "Los logs de auditoría están encadenados con SHA-256. Al alterar un registro manualmente, la cadena se rompe y el sistema lo detecta. Esto evidencia inmutabilidad."

**Medida de seguridad evidenciada:** Logs íntegros / inmutables

---

### Paso 9: Rotación de llaves en vivo

**Comando:** `./scripts/demo_rotacion.sh` (ver Paso 5.4)

**Qué ver en pantalla:**
- Script agrega nueva versión de llave (v3)
- Muestra conteo de campos por versión antes (v2: X, v3: 0)
- Ejecuta rotación: todos los campos migran a v3
- Muestra conteo después (v2: 0, v3: X)
- Reinicia backend con nueva ENC_KEY_CURRENT
- Petición a API como doctor: datos se leen igual

**Frase para el público:**
> "El sistema soporta rotación de llaves en vivo. Migré todos los datos de v2 a v3 sin interrumpir el servicio. Esto permite cumplir con recomendaciones de NIST SP 800-57 sobre periodos criptográficos."

**Medida de seguridad evidenciada:** Gestión de llaves

---

### Paso 10: Herramientas de análisis (antes/después)

**Archivos:** Mostrar `docs/hallazgos.md` y `docs/comparativa_antes_despues.md`

**Qué ver en pantalla:**
- Tabla de hallazgos iniciales: 3,596 hallazgos
- Tabla de hallazgos finales: 1,396 hallazgos
- Reducción del 61.18%
- Hallazgos corregidos: SEC-BANDIT-01/02, SEC-PIP-03/04, SEC-NPM-01, SEC-HADO-02/03/04, SEC-ZAP-01

**Frase para el público:**
> "Apliqué herramientas de seguridad (Bandit, Trivy, ZAP, etc.) antes y después de las correcciones. Reduje los hallazgos en un 61.18%, demostrando mejora continua de la postura de seguridad."

**Medida de seguridad evidenciada:** Herramienta de análisis aplicada

---

### Paso 11: Backup cifrado y restauración (opcional)

**Comando:** `./scripts/backup.sh` → `./scripts/restore.sh`  
**Qué ver en pantalla:**
- Backup creado: backup_YYYY-MM-DD_HHMM.dump.gpg
- Restauración exitosa a base separada
- Script `verificar_restauracion.py` reporta OK

**Frase para el público:**
> "Los backups se cifran con GPG AES-256. La restauración se prueba regularmente con RTO medido en [tiempo real de docs/BACKUPS.md]."

**Medida de seguridad evidenciada:** Continuidad

---

## Preguntas probables y respuesta corta

**¿Por qué GCM y no Fernet?**
> Fernet usa AES-128-CBC y no es estándar NIST. Migré a AES-256-GCM que es estándar FIPS 197 y NIST SP 800-38D, con autenticación integrada (tag).

**¿Dónde guardas la llave?**
> Actualmente en variables de entorno del contenedor Docker. En producción iría en un KMS/HSM con cifrado de sobre (trabajo futuro).

**¿Qué pasa si se pierde la llave?**
> Los datos cifrados se vuelven irrecuperables. Por eso se guardan backups separados de las llaves y se documenta el procedimiento de rotación.

**¿Qué pasa si un doctor se va?**
> Los pacientes pueden transferir su historial a otro doctor self-service. El sistema mantiene trazabilidad de quién fue el doctor anterior y el nuevo.

**¿Por qué el certificado es autofirmado?**
> Para demo y desarrollo. En producción se usaría un certificado de una CA reconocida como Let's Encrypt.

---

## Restaurar estado limpio

Si algo sale mal durante la demo, ejecutar:
```bash
./scripts/preparar_demo.sh
```

Esto restaura el estado inicial con todos los usuarios de demo y el Paciente Demo asignado a Dra. Ana Torres.
