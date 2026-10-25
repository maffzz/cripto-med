"""
Configuración de pytest para el proyecto CriptoMed.
"""

import sys
from pathlib import Path

# Agregar el directorio padre al path para poder importar app
sys.path.insert(0, str(Path(__file__).parent.parent))
