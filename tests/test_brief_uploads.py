"""Adjuntos de /api/v1/send-brief: camino feliz y topes pendientes de 7.2.

La tarea 7.2 (cap de tamano, numero y content type de adjuntos) no esta
implementada todavia: hoy no existe ningun limite en el codigo, asi que los
tests de rechazo documentan el comportamiento correcto como xfail estricto.
Cuando 7.2 aterrice, pasaran y hay que quitarles el marcador.
"""

import pytest

from tests.conftest import valid_brief_form

OVERSIZED = 12 * 1024 * 1024  # cualquier tope razonable (p. ej. 10 MB) lo rechaza


def test_brief_accepts_legitimate_attachment(client, fake_supabase, sent_emails):
    files = [("attachments", ("logo.png", b"contenido-de-prueba", "image/png"))]
    response = client.post(
        "/api/v1/send-brief", data=valid_brief_form(), files=files
    )
    assert response.status_code == 200
    assert len(fake_supabase.inserts["design_briefs"]) == 1

    # El adjunto subido viaja en el correo junto al PDF generado.
    attachment_names = [a["filename"] for a in sent_emails[0]["attachments"]]
    assert "logo.png" in attachment_names


@pytest.mark.xfail(
    strict=True,
    reason="Tarea 7.2 pendiente: no hay tope de tamano de adjunto; un archivo "
    "enorme se lee entero en memoria (512 MB en Render) y responde 200",
)
def test_brief_rejects_oversized_attachment(client):
    files = [("attachments", ("grande.bin", b"x" * OVERSIZED, "application/octet-stream"))]
    response = client.post(
        "/api/v1/send-brief", data=valid_brief_form(), files=files
    )
    assert response.status_code in (413, 422)


@pytest.mark.xfail(
    strict=True,
    reason="Tarea 7.2 pendiente: no hay tope de numero de adjuntos",
)
def test_brief_rejects_too_many_attachments(client):
    files = [
        ("attachments", (f"archivo-{i}.png", b"data", "image/png")) for i in range(20)
    ]
    response = client.post(
        "/api/v1/send-brief", data=valid_brief_form(), files=files
    )
    assert response.status_code in (413, 422)


@pytest.mark.xfail(
    strict=True,
    reason="Tarea 7.2 pendiente: no hay filtro de content type de adjuntos",
)
def test_brief_rejects_disallowed_content_type(client):
    files = [("attachments", ("programa.exe", b"MZ\x90\x00", "application/x-msdownload"))]
    response = client.post(
        "/api/v1/send-brief", data=valid_brief_form(), files=files
    )
    assert response.status_code in (400, 415, 422)
