"""Configuracion compartida de la suite.

Ningun test toca servicios reales: Supabase se sustituye por un fake en cada
modulo que lo importa y en la dependencia del router del brief, y
resend.Emails.send se captura en una lista. Ambos reemplazos son autouse, asi
que ningun test puede escribir en la base ni enviar correo aunque existan
credenciales reales en el entorno.
"""

import os

# Antes de cualquier import de la app: app.db.supabase_client crea el cliente
# al importar y exige SUPABASE_URL/SUPABASE_KEY. Se fijan valores dummy aqui,
# pisando cualquier credencial real del entorno, para que el import funcione
# sin .env y ninguna clave verdadera quede a la vista de la app.
os.environ["SUPABASE_URL"] = "http://localhost:54321"
os.environ["SUPABASE_KEY"] = "test-dummy-key"
os.environ["RESEND_API_KEY"] = "test-dummy-resend-key"

from types import SimpleNamespace

import pytest
import resend
from fastapi.testclient import TestClient

import app.main as app_main
import app.features.contact.data as contact_data
import app.features.projects.data as projects_data
from app.features.briefs.router import get_supabase

# Filas con la forma que ProjectService espera de la tabla projects. id y
# created_at van como texto porque ProjectResponse los tipa str hoy (issue de
# 0.9 que pertenece a 6.1, fuera del alcance de esta suite).
PROJECT_ROWS = [
    {
        "id": "11111111-1111-1111-1111-111111111111",
        "title_es": "Proyecto uno",
        "title_en": "Project one",
        "description_es": "Descripcion uno",
        "description_en": "Description one",
        "architecture_es": "Arquitectura uno",
        "architecture_en": "Architecture one",
        "technical_details_es": "Detalles uno",
        "technical_details_en": "Details one",
        "image_url": "https://example.com/one.png",
        "logo_url": None,
        "repository_url": "https://example.com/repo-one",
        "live_url": "https://example.com/live-one",
        "technologies": ["Python", "FastAPI"],
        "created_at": "2026-01-02T00:00:00+00:00",
    },
    {
        "id": "22222222-2222-2222-2222-222222222222",
        "title_es": "Proyecto dos",
        "title_en": "Project two",
        "description_es": "Descripcion dos",
        "description_en": "Description two",
        "architecture_es": "Arquitectura dos",
        "architecture_en": "Architecture two",
        "technical_details_es": "Detalles dos",
        "technical_details_en": "Details two",
        "image_url": "https://example.com/two.png",
        "logo_url": None,
        "repository_url": None,
        "live_url": None,
        "technologies": ["TypeScript"],
        "created_at": "2026-01-01T00:00:00+00:00",
    },
]

FAKE_INSERT_ID = 4242


class FakeTableQuery:
    """Imita la cadena table().select()/order()/limit()/insert().execute()."""

    def __init__(self, fake, table_name):
        self._fake = fake
        self._table = table_name
        self._insert_payload = None

    def select(self, *args, **kwargs):
        return self

    def order(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def insert(self, payload):
        self._insert_payload = payload
        return self

    def execute(self):
        if self._fake.fail:
            raise RuntimeError("fake supabase: conexion rechazada")
        if self._insert_payload is not None:
            self._fake.inserts.setdefault(self._table, []).append(self._insert_payload)
            return SimpleNamespace(data=[{"id": FAKE_INSERT_ID, **self._insert_payload}])
        return SimpleNamespace(data=list(self._fake.rows.get(self._table, [])))


class FakeSupabase:
    def __init__(self):
        self.fail = False
        self.rows = {"projects": PROJECT_ROWS}
        self.inserts = {}

    def table(self, name):
        return FakeTableQuery(self, name)


@pytest.fixture(autouse=True)
def fake_supabase(monkeypatch):
    """Un solo fake sustituye al cliente real en cada modulo que lo importo
    con `from ... import supabase`, y la dependencia del router del brief se
    sobreescribe con el mismo objeto."""
    fake = FakeSupabase()
    monkeypatch.setattr(app_main, "supabase", fake)
    monkeypatch.setattr(contact_data, "supabase", fake)
    monkeypatch.setattr(projects_data, "supabase", fake)
    app_main.app.dependency_overrides[get_supabase] = lambda: fake
    yield fake
    app_main.app.dependency_overrides.pop(get_supabase, None)


@pytest.fixture(autouse=True)
def sent_emails(monkeypatch):
    """Captura todo resend.Emails.send. El servicio de contacto fijo
    resend.api_key al importar; se reafirma el valor dummy por si el entorno
    traia uno real."""
    sent = []

    def fake_send(params):
        sent.append(params)
        return {"id": "fake-email-id"}

    monkeypatch.setattr(resend.Emails, "send", fake_send)
    monkeypatch.setattr(resend, "api_key", "test-dummy-resend-key")
    yield sent


@pytest.fixture()
def client(fake_supabase, sent_emails):
    return TestClient(app_main.app)


def valid_brief_form(**overrides):
    """Formulario minimo valido para /api/v1/send-brief. La lista en features
    hace que httpx repita la clave, que es el formato que el endpoint soporta
    desde la 1.1."""
    data = {
        "name": "Cliente de Prueba",
        "email": "cliente@example.com",
        "projectType": "website",
        "projectDescription": "Un sitio de prueba para la suite",
        "features": ["ecommerce", "blog", "seo", "cms"],
        "budget": "r2",
        "timeline": "one_month",
        "locale": "es",
    }
    data.update(overrides)
    return data
