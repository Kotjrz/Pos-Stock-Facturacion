from __future__ import annotations 

import os
from pathlib import Path 
from urllib.parse import urlparse

from dotenv import load_dotenv, set_key

ENV_PATH = Path(".env")

def ensureDatabaseUrl() -> str:
    load_dotenv(ENV_PATH)
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    while True:
        url = input(
            "Ingrese la cadena de conexion a la base de datos "
            "(ejemplo: postgres://user:password@localhost:5432/dbname): \n> "
        ).strip()
        if isValidDatabaseUrl(url):
            break
        print("La cadena de conexion no es valida. Intente de nuevo.")
    
    if not ENV_PATH.exists():
        ENV_PATH.touch()
    set_key(ENV_PATH, "DATABASE_URL", url)
    print ("Cadena de conexion guardada en el archivo .env")
    return url

def isValidDatabaseUrl(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"postgresql", "postgres"} and parsed.hostname and parsed.path