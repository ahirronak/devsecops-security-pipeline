"""Basic behavior tests for the intentionally vulnerable training app."""

import hashlib

from app import app


def client():
    app.config.update(TESTING=True)
    return app.test_client()


def test_home_page_is_available():
    response = client().get("/")

    assert response.status_code == 200
    assert b"DevSecOps Training App" in response.data


def test_health_endpoint():
    response = client().get("/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "application": "devsecops-training-app",
        "status": "ok",
    }


def test_search_reflects_input_for_security_scanner_demo():
    """Document the known XSS weakness until the remediation phase."""
    payload = "<script>alert('training')</script>"
    response = client().get("/search", query_string={"q": payload})

    assert response.status_code == 200
    assert payload.encode("utf-8") in response.data


def test_login_accepts_the_training_credential():
    response = client().post(
        "/login",
        data={"username": "admin", "password": "admin123"},
    )

    assert response.status_code == 200
    assert response.get_json()["message"] == "Login successful"


def test_hash_endpoint_uses_known_weak_hash_for_demo():
    response = client().get("/hash", query_string={"value": "hello"})

    assert response.status_code == 200
    assert response.get_json()["md5"] == hashlib.md5(b"hello").hexdigest()
