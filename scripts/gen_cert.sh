#!/bin/bash

# Script para generar certificados SSL autofirmados para localhost
# Funciona en macOS y Linux

CERTS_DIR="certs"
mkdir -p "$CERTS_DIR"

echo "Generando certificado SSL autofirmado para localhost..."

# Generar clave privada y certificado con SAN
openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout "$CERTS_DIR/key.pem" \
  -out "$CERTS_DIR/cert.pem" \
  -days 365 \
  -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"

echo "Certificados generados en $CERTS_DIR/"
echo "  - cert.pem"
echo "  - key.pem"
echo ""
echo "Los certificados son válidos por 365 días."
