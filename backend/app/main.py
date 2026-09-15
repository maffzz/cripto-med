from fastapi import FastAPI # framework web para la api

from app.config import JWT_SECRET # secreto jwt para saber si ya se configuro

app = FastAPI( # instancia principal de la aplicacion
    title="CriptoMed", # nombre que aparece en /docs
    description="Historiales clínicos con RBAC, cifrado y auditoría — DS3031", # texto de la documentacion
    version="0.1.0", # version inicial del api
)

@app.get("/health") # endpoint publico para verificar que el servidor vive
def health() -> dict[str, str]: # no exige autenticacion
    jwt_ready = "pending" if JWT_SECRET == "cambiar-en-local" else "configured" # pending = placeholder del .env
    return {"status": "ok", "service": "criptomed", "jwt_secret": jwt_ready} # no devuelve el secreto, solo el estado