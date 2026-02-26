import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Carga las variables del archivo .env
load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Faltan las credenciales de Supabase en el archivo .env")

supabase: Client = create_client(url, key)