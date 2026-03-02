import os
from dotenv import load_dotenv # type: ignore[import-not-found]
from supabase import create_client, Client # type: ignore[import-not-found]

# Carga las variables del archivo .env
load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Faltan las credenciales de Supabase en el archivo .env")

supabase: Client = create_client(url, key)