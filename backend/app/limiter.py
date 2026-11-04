"""
Configuración centralizada de Rate Limiting para CriptoMed.
Utiliza slowapi con extracción de IP real del cliente (NIST SP 800-63B / OWASP).
"""

from slowapi import Limiter
from app.audit import extract_client_ip

limiter = Limiter(key_func=extract_client_ip)
