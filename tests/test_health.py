"""GET / y GET /health, sano y degradado."""


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API ready"}


def test_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_degraded_when_supabase_fails(client, fake_supabase):
    fake_supabase.fail = True
    response = client.get("/health")
    assert response.status_code == 503
    assert response.json() == {"status": "degraded"}
