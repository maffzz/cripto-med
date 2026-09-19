# Configuración HTTPS - CriptoMed

## HTTP vs HTTPS

### Desarrollo (Actual)
- **Protocolo:** HTTP
- **Razón:** Los navegadores rechazan certificados SSL autofirmados en HTTPS (error NET::ERR_CERT_AUTHORITY_INVALID)
- **Puerto:** 8000
- **URL:** http://127.0.0.1:8000

### Producción (Recomendado)
- **Protocolo:** HTTPS
- **Razón:** Cumplir con el requisito de "certificados digitales" y proteger datos en tránsito
- **Puerto:** 8443 (o 443 con permisos de root)
- **URL:** https://criptomed.utec.edu.pe (ejemplo)

---

## Certificados Autofirmados

Los certificados fueron generados con OpenSSL:

```bash
cd backend/certs
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes
```

**Detalles del certificado:**
- País: PE
- Estado/Provincia: LIMA
- Localidad: LIMA
- Organización: UTEC
- Unidad Organizacional: UTEC
- Common Name: UTEC
- Email: maria.lazon@utec.edu.pe
- Validez: 365 días

---

## Configuración de HTTPS en Producción

### Opción 1: Usar Certificados Autofirmados (Solo para Demo/Desarrollo)

En `backend/app/main.py`:

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8443,
        ssl_keyfile="backend/certs/key.pem",
        ssl_certfile="backend/certs/cert.pem"
    )
```

**Pros:**
- Fácil de configurar
- No requiere pagar por certificados
- Suficiente para demostración académica

**Contras:**
- Los navegadores mostrarán advertencia de "sitio no seguro"
- No confiable para producción real
- No cumple con estándares de confianza

### Opción 2: Usar Certificados de Let's Encrypt (Recomendado para Producción)

**Pasos:**
1. Instalar certbot:
```bash
sudo apt-get install certbot python3-certbot nginx
```

2. Obtener certificado:
```bash
sudo certbot certonly --standalone -d criptomed.utec.edu.pe
```

3. Configurar uvicorn:
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=443,
        ssl_keyfile="/etc/letsencrypt/live/criptomed.utec.edu.pe/privkey.pem",
        ssl_certfile="/etc/letsencrypt/live/criptomed.utec.edu.pe/fullchain.pem"
    )
```

**Pros:**
- Gratis y confiable
- Automáticamente renovable
- Cumple con estándares de confianza
- Los navegadores no muestran advertencias

**Contras:**
- Requiere dominio público
- Requiere acceso a puertos 80/443
- Requiere renovación automática

### Opción 3: Usar Certificados Comerciales (Producción Empresarial)

**Pasos:**
1. Comprar certificado a autoridad de confianza (DigiCert, Comodo, etc.)
2. Configurar uvicorn con certificados comprados
3. Configurar renovación automática

**Pros:**
- Máxima confianza
- Soporte incluido
- Validación extendida (EV)

**Contras:**
- Costo anual (~$100-$500 USD)
- Requiere validación de organización

---

## Configuración Actual (Desarrollo)

**backend/app/main.py:**
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
```

**frontend/src/context/AuthContext.jsx:**
```javascript
// Todas las URLs usan HTTP
const response = await axios.post('http://127.0.0.1:8000/auth/login', formData);
```

---

## Pasos para Migrar a HTTPS en Producción

1. **Decidir tipo de certificado:**
   - Autofirmado (demo): Solo para proyecto académico
   - Let's Encrypt (gratis): Para producción real sin costo
   - Comercial (pago): Para producción empresarial

2. **Actualizar `backend/app/main.py`:**
   - Cambiar puerto a 8443 o 443
   - Añadir `ssl_keyfile` y `ssl_certfile`

3. **Actualizar URLs en frontend:**
   - Cambiar `http://127.0.0.1:8000` a `https://criptomed.utec.edu.pe`
   - Usar variable de entorno para diferenciar desarrollo/producción

---

## Evidencia de Implementación

**JWT Headers en Network Tab:**
![JWT Headers](images/JWT_logs.png)
- Demuestra que las llamadas al backend incluyen el header `Authorization: Bearer <token>`
- El token JWT se envía en cada request autenticado
- Validación de que la autenticación JWT está funcionando correctamente

4. **Actualizar firewall:**
   - Abrir puerto 443 o 8443
   - Configurar reglas de firewall

5. **Probar:**
   - Verificar que el sitio cargue con HTTPS
   - Verificar que no haya advertencias del navegador
   - Verificar que API funcione correctamente

---

## Consideraciones de Seguridad

### Encriptación en Tránsito
- **HTTPS (actual HTTP):** ❌ Datos viajan en texto claro entre navegador y servidor
- **HTTPS (con certificado):** ✅ Datos encriptados con TLS 1.2/1.3

### Actualmente
- **Desarrollo:** HTTP (aceptable para proyecto académico)
- **Producción:** Debe ser HTTPS (requerimiento del proyecto)

---

## Recomendación

Para el proyecto académico actual (DS3031):
- **Desarrollo:** HTTP es aceptable (simplifica desarrollo)
- **Demo/Presentación:** HTTPS con certificados autofirmados
- **Producción (si se implementa):** HTTPS con Let's Encrypt o certificados comerciales

El informe final debe explicar esta diferencia y justificar por qué se usa HTTP en desarrollo.
