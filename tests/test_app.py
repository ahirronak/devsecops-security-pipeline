"""Behavior and security regression tests for the remediated application."""

import hashlib

from app import app


def client():
    app.config.update(TESTING=True)
    return app.test_client()


def test_home_page_is_available():
    response = client().get("/")

    assert response.status_code == 200
    assert b"DevSecOps Secure App" in response.data


def test_health_endpoint():
    response = client().get("/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "application": "devsecops-secure-app",
        "status": "ok",
    }


def test_search_escapes_untrusted_input():
    payload = "<script>alert('training')</script>"
    response = client().get("/search", query_string={"q": payload})

    assert response.status_code == 200
    assert payload.encode("utf-8") not in response.data
    assert b"&lt;script&gt;" in response.data


def test_hash_endpoint_uses_sha256():
    response = client().get("/hash", query_string={"value": "hello"})

    assert response.status_code == 200
    assert response.get_json()["sha256"] == hashlib.sha256(b"hello").hexdigest()


def test_security_headers_are_applied():
    response = client().get("/")

    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]
    assert response.headers["Referrer-Policy"] == "no-referrer"
