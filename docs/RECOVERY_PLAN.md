# Plan de Recuperación ante Desastres - CriptoMed

## Resumen Ejecutivo
Este documento describe los procedimientos para recuperar el sistema CriptoMed en caso de desastres (fuga de datos, pérdida de datos, corrupción de base de datos, ataque de ransomware, etc.).

## 1. Tipos de Desastres Considerados

### 1.1 Fuga de Datos
- Acceso no autorizado a datos sensibles de pacientes
- Exposición de credenciales o llaves de encriptación
- Brecha de seguridad en el backend

### 1.2 Pérdida de Datos
- Fallo de hardware del servidor
- Corrupción de la base de datos
- Eliminación accidental de datos
- Ataque de ransomware

### 1.3 Ataque de Ransomware
- Encriptación maliciosa de archivos
- Demanda de rescate
- Compromiso de integridad de datos

---

## 2. Procedimientos de Recuperación

### 2.1 Recuperación desde Backup

**Paso 1: Evaluar el alcance del incidente**
- Identificar qué datos fueron comprometidos
- Determinar el punto en el tiempo del último backup válido
- Documentar el incidente con fecha, hora y causa

**Paso 2: Detener el sistema afectado**
```bash
# Detener backend
# Detener frontend (si aplica)
# Detener PostgreSQL
docker compose down
```

**Paso 3: Restaurar desde backup**
```bash
# Restaurar base de datos desde backup
docker exec -i criptomed_db psql -U criptomed criptomed < backups/criptomed_backup_YYYYMMDD_HHMMSS.sql
```

**Paso 4: Verificar integridad de datos**
- Verificar que los datos restaurados están cifrados correctamente
- Verificar que los logs de auditoría estén intactos
- Ejecutar pruebas de sanity check en la aplicación

**Paso 5: Reiniciar el sistema**
```bash
# Reiniciar PostgreSQL
docker compose up -d

# Reiniciar backend
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Reiniciar frontend
cd frontend
npm run dev
```

**Paso 6: Comunicación**
- Notificar a stakeholders (admin, clínica, pacientes afectados)
- Informar a autoridades si aplica (Ley N° 29733)
- Documentar lecciones aprendidas

### 2.2 Recuperación en caso de Ransomware

**Paso 1: Aislar el sistema**
- Desconectar la red del servidor afectado
- No pagar el rescate (política estándar de seguridad)
- Preservar evidencia forense

**Paso 2: Evaluar impacto**
- Identificar archivos encriptados
- Determinar si hay copias limpias disponibles
- Evaluar riesgo de propagación

**Paso 3: Recuperación desde backup limpio**
- Restaurar desde backup anterior al ataque
- Verificar que el backup no está comprometido
- Cambiar todas las credenciales expuestas

**Paso 4: Investigación forense**
- Analizar logs de auditoría para identificar el vector de ataque
- Escanear el sistema con herramientas antivirus
- Identificar vulnerabilidades explotadas

**Paso 5: Reinicio seguro**
- Cambiar todas las contraseñas
- Rotar llaves de encriptación
- Aplicar parches de seguridad
- Implementar medidas adicionales de monitoreo

---

## 3. Plan de Rotación de Llaves

### 3.1 Rotación de Llaves de Encriptación
- Frecuencia: Cada 90 días
- Procedimiento:
  1. Generar nueva llave Fernet
  2. Actualizar `.env` con nueva `ENCRYPTION_KEY`
  3. Migrar datos cifrados con la llave anterior a la nueva
  4. Eliminar llave anterior de forma segura

### 3.2 Rotación de Llaves JWT
- Frecuencia: Cada 30 días
- Procedimiento:
  1. Generar nuevo `JWT_SECRET`
  2. Actualizar `.env`
  - Los tokens existentes dejarán de ser válidos
  - Los usuarios deberán volver a hacer login

---

## 4. Plan de Pruebas de Recuperación

### 4.1 Pruebas Mensuales
- Verificar que el script de backup funciona
- Restaurar un backup de prueba en entorno de staging
- Verificar integridad de datos restaurados

### 4.2 Pruebas Trimestrales
- Simular incidente de fuga de datos
- Ejecutar procedimiento de recuperación completo
- Medir tiempo de recuperación (objetivo: < 4 horas)

---

## 5. Responsabilidades

### 5.1 Equipo Técnico
- Ejecutar procedimientos de recuperación
- Investigar causa raíz del incidente
- Implementar parches de seguridad

### 5.2 Administración
- Comunicar con stakeholders
- Notificar a autoridades si aplica
- Coordinar respuesta legal

### 5.3 Auditor
- Verificar que el incidente fue contenido
- Documentar medidas tomadas
- Recomendar mejoras de seguridad

---

## 6. Tiempos Objetivo de Recuperación

| Tipo de Incidente | Tiempo Objetivo de Recuperación |
|------------------|--------------------------------|
| Fuga de datos sin pérdida | < 2 horas |
| Pérdida de datos con backup | < 4 horas |
| Ransomware con backup limpio | < 8 horas |
| Corrupción de base de datos | < 6 horas |

---

## 7. Contactos de Emergencia

- Soporte Técnico: [email]
- Seguridad: [email]
- Legal: [email]
- Autoridades: [contacto si aplica]

---

## 8. Lecciones Aprendidas (se actualizará después de incidentes reales)

- [Se llenará después del primer incidente de recuperación]
