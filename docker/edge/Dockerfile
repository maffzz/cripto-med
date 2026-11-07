# Multi-stage Dockerfile para CriptoMed Edge (Nginx + Frontend)
# Etapa 1: Build del frontend React
FROM node:20.19.0-alpine AS builder

WORKDIR /app

# Copiar package files desde frontend/
COPY frontend/package*.json ./

# Instalar dependencias
RUN npm ci

# copiar codigo fuente desde frontend/
COPY frontend/ ./

# forzar /api: el backend no se publica en el host (puerto 8000 interno)
ENV VITE_API_URL=/api

# Credenciales de demo — se inyectan como ARG desde docker-compose.yml
# (solo datos de prueba académicos, no secretos de producción)
ARG DEMO_PASSWORD_ADMIN
ARG DEMO_PASSWORD_DOCTOR
ARG DEMO_PASSWORD_ADMINISTRATIVO
ARG DEMO_PASSWORD_AUDITOR
ARG DEMO_PASSWORD_PACIENTE

ENV VITE_DEMO_PASSWORD_ADMIN=$DEMO_PASSWORD_ADMIN
ENV VITE_DEMO_PASSWORD_DOCTOR=$DEMO_PASSWORD_DOCTOR
ENV VITE_DEMO_PASSWORD_ADMINISTRATIVO=$DEMO_PASSWORD_ADMINISTRATIVO
ENV VITE_DEMO_PASSWORD_AUDITOR=$DEMO_PASSWORD_AUDITOR
ENV VITE_DEMO_PASSWORD_PACIENTE=$DEMO_PASSWORD_PACIENTE

# build del frontend
RUN npm run build

# Etapa 2: Nginx con frontend compilado
FROM nginx:1.27-alpine

# Copiar build desde builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copiar configuración de nginx
COPY docker/edge/nginx.conf /etc/nginx/nginx.conf

# Exponer puertos
EXPOSE 8080 8443

STOPSIGNAL SIGTERM

CMD ["nginx", "-g", "daemon off;"]
