import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Carga las variables del archivo .env
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Faltan las credenciales de Supabase en el archivo .env")

supabase: CLient = create_client(url, key)