from fastapi.testclient import TestClient

from uptime_platform.main import app


def test_vite_origin_is_allowed() -> None:
    with TestClient(app) as client:
        response = client.options(
            "/api/v1/auth/login",
            headers={
                "Origin": ("http://localhost:5173"),
                "Access-Control-Request-Method": ("POST"),
            },
        )

    assert response.status_code == 200

    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"

    assert response.headers["access-control-allow-credentials"] == "true"
