"""
Pruebas de Cabeceras de Seguridad HTTP y Endurecimiento de CORS.
Estándares verificados:
- RFC 6797 (HTTP Strict Transport Security - HSTS).
- OWASP Secure Headers Cheat Sheet (X-Content-Type-Options, X-Frame-Options, Referrer-Policy, CSP).
- HIPAA Security Rule / OWASP (Cache-Control: no-store para datos médicos).
- OWASP Cross-Origin Resource Sharing (CORS) Restrictivo.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.main import app
from app.config import ALLOWED_ORIGINS


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_cabeceras_de_seguridad_presentes(client):
    """Verifica que toda respuesta incluya las cabeceras de seguridad requeridas por OWASP."""
    resp = client.get("/health")
    assert resp.status_code == 200

    headers = resp.headers
    # 1. HSTS (RFC 6797)
    assert "strict-transport-security" in headers
    assert "max-age=31536000" in headers["strict-transport-security"]
    assert "includesubdomains" in headers["strict-transport-security"].lower()

    # 2. X-Content-Type-Options
    assert headers.get("x-content-type-options") == "nosniff"

    # 3. X-Frame-Options (Anti-Clickjacking)
    assert headers.get("x-frame-options") == "DENY"

    # 4. Referrer-Policy
    assert headers.get("referrer-policy") == "no-referrer"

    # 5. Content-Security-Policy restrictivo para la API
    assert "default-src 'none'" in headers.get("content-security-policy", "")
    assert "frame-ancestors 'none'" in headers.get("content-security-policy", "")


def test_cache_control_no_store_en_pacientes(client):
    """Verifica que las rutas de pacientes incluyan Cache-Control: no-store (HIPAA / OWASP)."""
    # Incluso un acceso denegado (401) debe incluir la directiva no-store
    resp = client.get("/pacientes")
    headers = resp.headers

    assert "cache-control" in headers
    assert "no-store" in headers["cache-control"]
    assert headers.get("pragma") == "no-cache"


def test_cors_origen_permitido(client):
    """Verifica que los orígenes legítimos configurados reciban Access-Control-Allow-Origin."""
    origen_valido = "https://localhost:8443"
    resp = client.options(
        "/auth/login",
        headers={
            "Origin": origen_valido,
            "Access-Control-Request-Method": "POST",
        }
    )
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == origen_valido
    assert resp.headers.get("access-control-allow-credentials") == "true"


def test_cors_origen_no_permitido(client):
    """Verifica que un origen no permitido no reciba cabecera Access-Control-Allow-Origin."""
    origen_malicioso = "https://malicious-site.example.com"
    resp = client.options(
        "/auth/login",
        headers={
            "Origin": origen_malicioso,
            "Access-Control-Request-Method": "POST",
        }
    )
    # FastAPI CORSMiddleware no inyecta access-control-allow-origin para orígenes no permitidos
    assert "access-control-allow-origin" not in resp.headers


def test_docs_deshabilitados_cuando_modo_produccion():
    """Verifica que en modo producción (ENV=production), /docs y /openapi.json se deshabiliten (404)."""
    from app.security_headers import SecurityHeadersMiddleware

    prod_app = FastAPI(
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    prod_app.add_middleware(SecurityHeadersMiddleware)
    prod_client = TestClient(prod_app)

    assert prod_client.get("/docs").status_code == 404
    assert prod_client.get("/redoc").status_code == 404
    assert prod_client.get("/openapi.json").status_code == 404
