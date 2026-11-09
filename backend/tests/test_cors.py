from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


def test_local_vite_origins_are_in_cors_allowlist():
    expected = {"http://localhost:5173", "http://127.0.0.1:5173"}
    assert expected.issubset(set(settings.cors_origins))


def test_cors_preflight_allows_localhost_vite_origin():
    client = TestClient(app)
    try:
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "content-type",
            },
        )
    finally:
        client.close()

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_preflight_allows_loopback_vite_origin():
    client = TestClient(app)
    try:
        response = client.options(
            "/health",
            headers={
                "Origin": "http://127.0.0.1:5173",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "content-type",
            },
        )
    finally:
        client.close()

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"


def test_cors_preflight_rejects_unlisted_origin():
    client = TestClient(app)
    try:
        response = client.options(
            "/health",
            headers={
                "Origin": "https://untrusted.example",
                "Access-Control-Request-Method": "GET",
            },
        )
    finally:
        client.close()

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers
