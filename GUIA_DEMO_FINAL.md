# Guía de Demo Final - CriptoMed

**Fecha:** Noviembre 2026  
**Propósito:** Demostración en vivo para DS3031 - Ética y Seguridad de Datos

---

## Preparación (Antes de la Demo)

### 1. Verificar Docker
```bash
docker --version
docker compose version
```

### 2. Generar Secretos (si no existen)
```bash
python3 scripts/generate_secrets.py --generate-env
```

### 3. Generar Certificados (si no existen)
```bash
./scripts/gen_cert.sh
```

### 4. Preparar Demo desde Cero
```bash
./scripts/preparar_demo.sh
```

Este script:
- Limpia volúmenes anteriores
- Levanta servicios con build
- Espera a que db, backend y edge estén healthy
- Crea 7 usuarios de demo específicos
- Asigna Paciente Demo a Dra. Ana Torres
- Verifica cadena de logs, cifrado y despliegue

### 5. Verificar Despliegue
```bash
./scripts/verificar_despliegue.sh
```

Debería mostrar 8 verificaciones OK.

---

## Guion de Demo (11 Pasos)

### Paso 1: Login como Admin
- **URL:** https://localhost:8443
- **Usuario:** admin@criptomed.local
- **Contraseña:** [DEMO_PASSWORD_ADMIN del .env]
- **Qué ver:** Dashboard con stats cards, gráficos, lista de pacientes
- **Frase:** "Como administrador, tengo acceso total al sistema"

### Paso 2: Ver Dashboard
- **Qué ver:** Stats cards (total pacientes, activos, rol), gráficos (hospital, tipo admisión)
- **Frase:** "El dashboard muestra métricas en tiempo real con gráficos de pacientes por hospital y tipo de admisión"

### Paso 3: Login como Doctor A (Dra. Ana Torres)
- **URL:** https://localhost:8443
- **Usuario:** ana.torres@criptomed.local
- **Contraseña:** [DEMO_PASSWORD_DOCTOR del .env]
- **Qué ver:** Solo pacientes asignados (incluyendo Paciente Demo)
- **Frase:** "Como doctor, solo veo mis pacientes asignados por principio de mínimo privilegio"

### Paso 4: Ver Paciente Demo
- **Qué ver:** Paciente Demo con todos los datos clínicos (diagnóstico, medicación, resultado_test)
- **Frase:** "Los datos clínicos están cifrados con AES-256-GCM en reposo"

### Paso 5: Login como Doctor B (Dr. Luis Ramírez)
- **URL:** https://localhost:8443
- **Usuario:** luis.ramirez@criptomed.local
- **Contraseña:** [DEMO_PASSWORD_DOCTOR del .env]
- **Qué ver:** NO ve Paciente Demo (no está en su lista)
- **Frase:** "Doctor B no puede ver al paciente demo porque no está asignado a él"

### Paso 6: Login como Administrativo
- **URL:** https://localhost:8443
- **Usuario:** admin1@criptomed.local
- **Contraseña:** [DEMO_PASSWORD_ADMINISTRATIVO del .env]
- **Qué ver:** Pacientes pero SIN campos clínicos (diagnóstico, medicación, resultado_test ocultos)
- **Frase:** "El administrativo ve datos básicos y facturación, pero NO ve datos clínicos sensibles"

### Paso 7: Login como Paciente
- **URL:** https://localhost:8443
- **Usuario:** paciente1@criptomed.local
- **Contraseña:** [DEMO_PASSWORD_PACIENTE del .env]
- **Qué ver:** Mi Historial con consentimiento, doctor asignado, accesos, datos personales, clínicos, administrativos
- **Frase:** "Como paciente, puedo ver mi historial completo y controlar quién accede"

### Paso 8: Exportar Datos (Derecho de Portabilidad)
- **Acción:** Click en "Descargar mis datos (JSON)"
- **Qué ver:** Toast de éxito y descarga de JSON
- **Frase:** "El paciente puede exportar sus datos (derecho de portabilidad conforme a Ley 29733 y GDPR)"

### Paso 9: Ver Accesos (Trazabilidad)
- **Qué ver:** Tabla de accesos con nombre profesional, rol, timestamp, acción
- **Frase:** "Todos los accesos están registrados en logs inmutables con cadena SHA-256"

### Paso 10: Transferir a Doctor B
- **Acción:** Seleccionar Dr. Luis Ramírez, click en "Transferir"
- **Qué ver:** Modal de confirmación, toast de éxito
- **Frase:** "El paciente puede transferir su historial a otro doctor de forma autónoma"

### Paso 11: Verificar Transferencia en Auditor
- **URL:** https://localhost:8443
- **Usuario:** auditor1@criptomed.local
- **Contraseña:** [DEMO_PASSWORD_AUDITOR del .env]
- **Qué ver:** Logs de auditoría con evento de transferencia
- **Frase:** "El auditor ve todos los eventos de transferencia en los logs inmutables"

---

## Demo Adicional (Opcional)

### Demo de Rotación de Llaves
```bash
./scripts/demo_rotacion.sh
```

Esta demo:
- Muestra conteo de campos por versión (antes)
- Agrega nueva versión v3 de llave
- Muestra migración de datos
- Verifica que API funciona con nueva llave

### Demo de Alteración de Logs
```bash
docker compose exec -T db psql -U app -d criptomedschema < scripts/demo_alterar_log.sql
```

Luego verificar cadena:
```bash
docker compose run --rm backend python scripts/verificar_cadena_logs.py
```

Debe mostrar que la cadena es inválida (detecta alteración).

---

## Dark Mode (Mejora UX)

Para demostrar dark mode:
- Click en icono Luna/Sol en el navbar
- Alternar entre modo claro y oscuro
- Preferencia se persiste en localStorage

---

## Dashboard Oficial de Datos Personales (Mejora Técnica)

Para demostrar el dashboard del Oficial:
- Login como admin
- Click en "Dashboard Oficial" en el navbar
- Ver métricas de cumplimiento legal:
  - Bancos de datos registrados
  - Solicitudes ARCO pendientes
  - Incidentes de seguridad
  - Cumplimiento de retención
  - Pacientes activos, accesos, anonimizados
  - Verificación de cadena de logs

---

## Preguntas Probables y Respuestas

**P: ¿Cómo se cifran los datos?**
R: AES-256-GCM con llaves versionadas y AAD (datos asociados autenticados) para prevenir copia entre registros.

**P: ¿Cómo se protege el tráfico?**
R: TLS 1.3 exclusivo en Nginx edge, no se acepta TLS 1.2 ni versiones anteriores.

**P: ¿Cómo se garantiza la inmutabilidad de los logs?**
R: Cadena SHA-256 (hash_prev, hash_actual, seq) con triggers anti-UPDATE/DELETE y rol de aplicación con solo INSERT/SELECT.

**P: ¿Qué pasa si se pierden las llaves de cifrado?**
R: Los datos se vuelven inaccesibles. Por eso se hace backup de ENC_KEYS y BACKUP_PASSPHRASE en gestor de secretos.

**P: ¿Cómo se cumple la Ley 29733?**
R: Cifrado en reposo, cifrado en tránsito, RBAC, logs inmutables, derechos ARCO (acceso, portabilidad, control de accesos), DPIA completa.

**P: ¿Cuánto tiempo se conservan los datos?**
R: 20 años conforme a norma técnica MINSA R.M. Nº 214-2018/MINSA (5 años en archivo activo + 15 años en archivo pasivo).

**P: ¿Qué mejora implementaron?**
R: Toast notifications, skeleton loading, gráficos en dashboard, dark mode, política de retención y anonimización, backups automáticos, dashboard oficial de datos personales.

---

## Verificación Final Después de Demo

### 1. Verificar Cifrado
```bash
docker compose run --rm backend python scripts/verificar_cifrado.py
```

### 2. Verificar Cadena de Logs
```bash
docker compose run --rm backend python scripts/verificar_cadena_logs.py
```

### 3. Verificar Despliegue
```bash
./scripts/verificar_despliegue.sh
```

---

## Capturas para PPT

Recomendación: Tomar capturas de:

1. Login screen
2. Dashboard con gráficos
3. Paciente Demo con datos clínicos
4. Paciente Mi Historial con consentimiento
5. Tabla de accesos (trazabilidad)
6. Dashboard Oficial de Datos Personales
7. Dark mode activado
8. Verificación de cadena de logs (terminal)

---

## Restaurar Estado Limpio (si es necesario)

```bash
./scripts/dev.sh reset
```

Esto:
- Detiene servicios
- Borra volúmenes
- Levanta servicios
- Carga datos semilla

---

## Notas Importantes

- Aceptar certificado autofirmado en el navegador al acceder a https://localhost:8443
- Usar contraseñas del .env (no hardcodeadas)
- Si Docker está lento, usar `docker compose up -d --build` para rebuild
- Si hay errores, revisar logs con `docker compose logs backend`
- Para ver logs en tiempo real: `docker compose logs -f backend`

---

## Timing Estimado

- Preparación: 2-3 minutos
- Demo principal (11 pasos): 5-7 minutos
- Demo adicional (rotación de llaves): 2-3 minutos
- Preguntas: 3-5 minutos
- **Total:** 12-18 minutos

---

## Script de Verificación (One-liner)

Para verificar todo en un solo comando:

```bash
./scripts/verificar_despliegue.sh && docker compose run --rm backend python scripts/verificar_cifrado.py && docker compose run --rm backend python scripts/verificar_cadena_logs.py
```

Debería mostrar todas las verificaciones OK.
