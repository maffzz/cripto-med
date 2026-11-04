# Registro de Riesgos Aceptados — CriptoMed

**Estándares y Referencias:**
- **RFC 8725:** *JSON Web Token Best Current Practices* (Sección 3.11: *Token Storage and Leakage*).
- **OWASP Session Management Cheat Sheet:** *HTML5 Web Storage Considerations*.
- **OWASP Cross-Site Scripting (XSS) Prevention Cheat Sheet**.
- **NIST SP 800-63B:** *Digital Identity Guidelines* (Sección 7.1: *Session Binding*).

---

## 1. Riesgo RA-01: Almacenamiento de Tokens JWT de Acceso en `localStorage`

| Identificador | Nivel de Riesgo Inherente | Nivel de Riesgo Residual | Estado |
| :--- | :--- | :--- | :--- |
| **RA-01** | **Medio** (Exposición teórica a XSS) | **Bajo** (Controles compensatorios activos) | **Aceptado Temporalmente** |

### Descripción del Riesgo
En la versión actual de la interfaz web (Single Page Application con React + Vite), el token JWT emitido tras la autenticación (`access_token`) se almacena en el `localStorage` del navegador para adjuntarlo como encabezado `Authorization: Bearer <token>` en las peticiones Axios hacia la API.

El almacenamiento web HTML5 (`localStorage`) es accesible por cualquier código JavaScript que se ejecute en el mismo origen (`https://localhost:8443`). Por tanto, si un atacante lograra explotar una vulnerabilidad de Cross-Site Scripting (XSS) en la aplicación, podría extraer el token de la sesión activa del usuario.

---

## 2. Controles Compensatorios y Mitigaciones Implementadas

Se ha decidido **aceptar temporalmente este riesgo** en la Entrega 2 respaldado por cinco controles de endurecimiento y mitigación en profundidad:

1. **Content Security Policy (CSP) Restrictiva (Paso 1.6a)**:
   - Configurada tanto a nivel de cabecera HTTP en el Edge Nginx (`docker/edge/nginx.conf`) y backend FastAPI (`SecurityHeadersMiddleware`), como en el archivo HTML del cliente (`frontend/index.html`).
   - Política `script-src 'self'`: Impide la carga y ejecución de scripts provenientes de dominios de terceros o fuentes no autorizadas.
   - Política `connect-src 'self' https://localhost:8443`: Impide que un script malicioso exfiltre datos hacia servidores externos controlados por el atacante.

2. **Ausencia Total de Renderizado Inseguro en React**:
   - Se auditó exhaustivamente la base de código del frontend confirmando que **no se utiliza `dangerouslySetInnerHTML`** en ningún componente. Todo el contenido dinámico es escapado automáticamente por el motor de React antes de su inserción en el DOM.

3. **Expiración de Token Corta (`JWT_EXPIRE_MINUTES = 15`)**:
   - Los tokens poseen un período de validez reducido a **15 minutos**. En caso de una filtración fortuita, la ventana de oportunidad para reutilizar el token robado es sumamente estrecha.

4. **Temporizador de Inactividad en el Cliente (15 minutos)**:
   - Implementado en `frontend/src/context/AuthContext.jsx`. Si el usuario no registra actividad física (teclado, mouse, scroll, tacto) durante 15 minutos, la sesión se destruye localmente (`localStorage.removeItem('token')`) y la aplicación redirige al login.

5. **Revocación Inmediata del Lado del Servidor (RFC 8725)**:
   - El backend **no confía ciegamente en la firma del JWT**: en cada solicitud entrante, la dependencia `get_current_user` consulta en tiempo real el registro del usuario en la base de datos PostgreSQL.
   - Si el administrador desactiva al usuario (`activo = False`) o si la cuenta es bloqueada por intentos fallidos (`bloqueado_hasta > now`), el token queda revocado y es rechazado **inmediatamente**, sin esperar a que transcurran los 15 minutos de expiración.

---

## 3. Plan de Mitigación Futura / Roadmap Arquitectónico

Para la versión final de producción en nube, se contempla la migración hacia el patrón de sesión seguro:
1. **Cookies de Sesión `HttpOnly`**:
   - Almacenar el JWT o la sesión en una cookie marcada con las banderas:
     - `HttpOnly` (inmune a lectura por JavaScript/XSS).
     - `Secure` (transmitida únicamente sobre conexiones TLS 1.3).
     - `SameSite=Strict` o `SameSite=Lax` (aislamiento contra peticiones cross-site).
2. **Protección Anti-CSRF**:
   - Implementación del patrón *Double Submit Cookie* o token anti-CSRF sincronizado para proteger los métodos que mutan estado (`POST`, `PUT`, `DELETE`).
