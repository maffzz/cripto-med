from sqlalchemy import create_engine # crea el motor de conexion a la base de datos
from sqlalchemy.ext.declarative import declarative_base # base para los modelos orm
from sqlalchemy.orm import sessionmaker # fabrica de sesiones para interactuar con la db

from app.config import DATABASE_URL # url de conexion desde el archivo de configuracion

# crea el motor de conexion a postgresql
engine = create_engine(DATABASE_URL, pool_pre_ping=True) # pool_pre_ping verifica que la conexion este viva antes de usarla

# crea la clase sessionlocal para crear sesiones de base de datos
sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # autocommit=false para controlar transacciones manualmente

# base declarativa para que los modelos hereden de ella
base = declarative_base() # todos los modelos heredaran de esta base


# funcion dependency injection para fastapi
def get_db(): # crea una sesion de db y la cierra automaticamente
    db = sessionlocal() # crea una nueva sesion
    try:
        yield db # la sesion se inyecta en el endpoint
    finally:
        db.close() # cierra la sesion despues de usarla