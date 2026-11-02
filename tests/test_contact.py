"""POST /contact: camino feliz, honeypot y validacion del correo."""

VALID_MESSAGE = {
    "name": "Ana Prueba",
    "email": "ana@example.com",
    "message": "Hola, me interesa un proyecto",
}


def test_contact_happy_path(client, fake_supabase, sent_emails):
    response = client.post("/contact", json=VALID_MESSAGE)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["ticket_id"].startswith("REF-")

    inserts = fake_supabase.inserts["portfolio_contact"]
    assert len(inserts) == 1
    assert inserts[0]["name"] == "Ana Prueba"
    assert inserts[0]["email"] == "ana@example.com"
    # El honeypot nunca llega a la tabla.
    assert "phone_extension" not in inserts[0]

    assert len(sent_emails) == 1
    assert body["ticket_id"] in sent_emails[0]["subject"]


def test_contact_honeypot_short_circuits(client, fake_supabase, sent_emails):
    # phone_extension lleno: respuesta de exito falsa, sin insert y sin correo.
    response = client.post(
        "/contact", json={**VALID_MESSAGE, "phone_extension": "555"}
    )
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Processed"}
    assert fake_supabase.inserts == {}
    assert sent_emails == []


def test_contact_rejects_malformed_email(client, fake_supabase):
    # /contact ya usa EmailStr; este test fija el contraste con el brief, que
    # todavia no valida (ver tests/test_brief.py).
    response = client.post(
        "/contact", json={**VALID_MESSAGE, "email": "no-es-un-correo"}
    )
    assert response.status_code == 422
    assert fake_supabase.inserts == {}
