# Políticas de Contraseñas - CriptoMed

## Política de Contraseñas

### 1. Requisitos de Contraseñas

#### 1.1 Complejidad Mínima
- Longitud mínima: 12 caracteres
- Debe contener al menos:
  - 1 letra mayúscula (A-Z)
  - 1 letra minúscula (a-z)
  - 1 número (0-9)
  - 1 carácter especial (!@#$%^&*)

#### 1.2 Contraseñas Prohibidas
- No usar contraseñas comunes: `password123`, `admin123`, `123456789`
- No usar información personal: fecha de nacimiento, nombre del paciente, etc.
- No usar la misma contraseña en múltiples sistemas
- No compartir contraseñas con nadie

#### 1.3 Rotación de Contraseñas
- Frecuencia: Cada 90 días
- Rotación inmediata si se sospecha compromiso
- Las contraseñas anteriores no pueden reutilizarse por 1 año

### 2. Gestión de Contraseñas

#### 2.1 Almacenamiento
- Todas las contraseñas se almacenan hasheadas con bcrypt
- Nunca se almacenan contraseñas en texto claro
- Los hashes de contraseñas tienen un factor de trabajo de 12

#### 2.2 Recuperación de Contraseñas
- No hay recuperación de contraseñas (solo reset)
- El usuario debe solicitar un reset al administrador
- El reset genera una contraseña temporal que debe cambiarse en el primer login

#### 2.3 Bloqueo de Cuentas
- Después de 5 intentos fallidos de login, la cuenta se bloquea por 15 minutos
- El administrador puede desbloquear manualmente
- Se notifica al usuario por email cuando la cuenta es bloqueada

### 3. Políticas para Usuarios Temporales

#### 3.1 Contraseñas Iniciales
- Las contraseñas iniciales (como `admin123`) deben cambiarse en el primer login
- Sistema forzará cambio de contraseña en el primer login
- El usuario tiene 7 días para cambiar la contraseña

#### 3.2 Contraseñas de Servicio
- Las contraseñas de servicio (API keys, tokens) se rotan cada 90 días
- Se almacenan en variables de entorno, no en código
- Se usan secrets managers en producción (ej: AWS Secrets Manager)

### 4. Seguridad en el Desarrollo

#### 4.1 Contraseñas de Desarrollo
- Las contraseñas de desarrollo son diferentes a las de producción
- Las contraseñas de prueba se rotan cada 30 días
- No usar contraseñas de producción en desarrollo

#### 4.2 Control de Acceso
- Los desarrolladores solo tienen acceso a contraseñas de desarrollo
- El acceso a contraseñas de producción es solo para personal autorizado
- Los commits no deben contener contraseñas o llaves privadas

### 5. Monitoreo y Auditoría

#### 5.1 Detección de Contraseñas Débiles
- El sistema rechaza contraseñas que no cumplan los requisitos
- Se notifica al usuario cuando intenta usar una contraseña débil
- Se sugieren contraseñas más fuertes

#### 5.2 Logs de Contraseñas
- Los intentos de login fallidos se registran en `audit_logs`
- Se registra: usuario, IP, timestamp, número de intento
- Los administradores pueden ver patrones de ataques de fuerza bruta

### 6. Procedimientos de Emergencia

#### 6.1 Compromiso de Contraseñas
- Si una contraseña es comprometida:
  1. El usuario debe cambiarla inmediatamente
  2. El administrador debe revocar el token JWT
  3. Se debe investigar cómo fue comprometida
  4. Se debe revisar el log de auditoría para actividades sospechosas

#### 6.2 Compromiso Masivo
- Si hay un compromiso masivo de contraseñas:
  1. Forzar cambio de contraseñas para todos los usuarios
  2. Rotar todas las llaves JWT y de encriptación
  3. Revocar todos los tokens activos
  4. Notificar a todos los usuarios del cambio

### 7. Educación y Concientización

#### 7.1 Capacitación de Usuarios
- Los usuarios reciben capacitación sobre:
  - Cómo crear contraseñas fuertes
  - Por qué no deben compartir contraseñas
  - Cómo reconocer phishing de contraseñas
  - Qué hacer si olvidan su contraseña

#### 7.2 Recordatorios Automáticos
- El sistema envía recordatorios de cambio de contraseña 7 días antes de la fecha límite
- Los usuarios pueden solicitar un recordatorio en cualquier momento
- Los administradores pueden recordar cambio a usuarios específicos

### 8. Cumplimiento Normativo

#### 8.1 Ley Peruana N° 29733
- Las contraseñas son consideradas datos personales sensibles
- Deben protegerse con medidas de seguridad razonables
- El acceso a contraseñas debe estar controlado
- Debe haber registro de quién accede a contraseñas

#### 8.2 ISO 27001
- Políticas de contraseñas alineadas con estándares internacionales
- Procesos formales de gestión de contraseñas
- Auditoría regular de políticas de contraseñas

---

## Resumen Ejecutivo

**Objetivo:** Proteger el acceso al sistema CriptoMed mediante políticas de contraseñas robustas

**Principios:**
- Complejidad mínima de 12 caracteres
- Rotación cada 90 días
- Almacenamiento hashead con bcrypt
- No reutilización de contraseñas
- Bloqueo después de 5 intentos fallidos

**Responsables:**
- Usuarios: Crear contraseñas fuertes, no compartirlas, cambiarlas periódicamente
- Administradores: Forzar cambios, desbloquear cuentas, investigar compromisos
- Auditores: Verificar cumplimiento, revisar logs de auditoría
