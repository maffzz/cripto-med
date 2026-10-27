# Multi-stage Dockerfile para CriptoMed Edge (Nginx + Frontend)
# Etapa 1: Build del frontend React
FROM node:20.19.0-alpine AS builder

WORKDIR /app

# Copiar package files desde frontend/
COPY frontend/package*.json ./

# Instalar dependencias
RUN npm ci

# Copiar código fuente desde frontend/
COPY frontend/ ./

# Build del frontend
RUN npm run build

# Etapa 2: Nginx con frontend compilado
FROM nginx:1.27-alpine

# Copiar build desde builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copiar configuración de nginx
COPY docker/edge/nginx.conf /etc/nginx/nginx.conf

# Exponer puertos
EXPOSE 8080 8443

# Usuario no root (ya está en nginx-unprivileged)
STOPSIGNAL SIGTERM

CMD ["nginx", "-g", "daemon off;"]
