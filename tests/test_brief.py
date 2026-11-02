"""POST /api/v1/send-brief: camino feliz multi-feature y bugs conocidos de 0.9."""

import pytest
import resend

from tests.conftest import FAKE_INSERT_ID, valid_brief_form

FOUR_FEATURES = ["ecommerce", "blog", "seo", "cms"]


def test_brief_happy_path_multiple_features(client, fake_supabase, sent_emails):
    """Guarda de la 1.1: las CUATRO features seleccionadas llegan al insert.

    La regresion original declaraba features como Form(str), con lo que FastAPI
    descartaba todas las repeticiones menos una antes de validar.
    """
    response = client.post("/api/v1/send-brief", data=valid_brief_form())
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["id"] == FAKE_INSERT_ID

    inserts = fake_supabase.inserts["design_briefs"]
    assert len(inserts) == 1
    row = inserts[0]
    assert row["features"] == FOUR_FEATURES
    assert row["full_data"]["features"] == FOUR_FEATURES
    assert row["client_name"] == "Cliente de Prueba"
    assert row["client_email"] == "cliente@example.com"

    # El correo sale (mockeado) con el PDF del brief adjunto.
    assert len(sent_emails) == 1
    attachment_names = [a["filename"] for a in sent_emails[0]["attachments"]]
    assert attachment_names[0].endswith(".pdf")


def test_brief_single_feature_still_binds_as_list(client, fake_supabase):
    response = client.post(
        "/api/v1/send-brief", data=valid_brief_form(features=["ecommerce"])
    )
    assert response.status_code == 200
    assert fake_supabase.inserts["design_briefs"][0]["features"] == ["ecommerce"]


@pytest.mark.xfail(
    strict=True,
    reason="Issue 0.9 / tarea 7.3: email del brief es str plano (router.py:30) "
    "mientras /contact usa EmailStr; un correo malformado debe ser 422",
)
def test_brief_rejects_malformed_email(client, fake_supabase):
    response = client.post(
        "/api/v1/send-brief", data=valid_brief_form(email="no-es-un-correo")
    )
    assert response.status_code == 422
    assert fake_supabase.inserts == {}


@pytest.mark.xfail(
    strict=True,
    reason="Issue 0.9 / revisar con 2.4: brief guardado pero correo fallido "
    "devuelve 500 (service.py:99, router.py:234); el cliente reintenta y "
    "duplica la fila. Guardado exitoso debe responder exito",
)
def test_brief_saved_but_email_failed_still_returns_success(
    client, fake_supabase, monkeypatch
):
    def failing_send(params):
        raise RuntimeError("resend caido (fake)")

    monkeypatch.setattr(resend.Emails, "send", failing_send)

    response = client.post("/api/v1/send-brief", data=valid_brief_form())

    # La fila SI se guardo antes de que el correo fallara...
    assert len(fake_supabase.inserts["design_briefs"]) == 1
    # ...asi que la respuesta correcta es exito con el id, no un 500.
    assert response.status_code == 200
    assert response.json()["id"] == FAKE_INSERT_ID
