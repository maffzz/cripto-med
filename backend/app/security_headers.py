"""
Middleware de Cabeceras de Seguridad HTTP (OWASP / RFC 6797 / HIPAA).
Inyecta cabeceras de endurecimiento y previene almacenamiento en caché de datos médicos.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        # 1. HTTP Strict Transport Security (RFC 6797)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # 2. Protección contra MIME-sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # 3. Protección contra Clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # 4. Política de Referrer estricta
        response.headers["Referrer-Policy"] = "no-referrer"

        # 5. Content Security Policy estricta para la API
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"

        # 6. Cross-Origin-Resource-Policy (CORP) para aislamiento de recursos API (OWASP ZAP / SEC-ZAP-01)
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

        # 7. Cache-Control: no-store para endpoints con datos sensibles de salud (HIPAA / OWASP)
        if request.url.path.startswith("/pacientes"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
            response.headers["Pragma"] = "no-cache"

        return response
