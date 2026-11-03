"""GET /projects: ambos idiomas, forma de la respuesta y validacion de lang."""


EXPECTED_KEYS = {
    "id",
    "title",
    "description",
    "architecture",
    "technical_details",
    "image_url",
    "logo_url",
    "repository_url",
    "live_url",
    "technologies",
    "created_at",
}


def test_projects_es(client):
    response = client.get("/projects", params={"lang": "es"})
    assert response.status_code == 200
    projects = response.json()
    assert [p["title"] for p in projects] == ["Proyecto uno", "Proyecto dos"]
    assert projects[0]["description"] == "Descripcion uno"


def test_projects_en(client):
    response = client.get("/projects", params={"lang": "en"})
    assert response.status_code == 200
    projects = response.json()
    assert [p["title"] for p in projects] == ["Project one", "Project two"]
    assert projects[0]["description"] == "Description one"


def test_projects_default_lang_is_es(client):
    response = client.get("/projects")
    assert response.status_code == 200
    assert response.json()[0]["title"] == "Proyecto uno"


def test_projects_response_shape(client):
    response = client.get("/projects", params={"lang": "en"})
    projects = response.json()
    assert len(projects) == 2
    for project in projects:
        assert set(project.keys()) == EXPECTED_KEYS
        assert isinstance(project["technologies"], list)


def test_projects_rejects_unknown_lang(client):
    response = client.get("/projects", params={"lang": "fr"})
    assert response.status_code == 422
