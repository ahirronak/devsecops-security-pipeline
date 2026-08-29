"""Minimal Flask application used to demonstrate a secured CI/CD pipeline."""

import hashlib
import os
import secrets
from html import escape

from flask import Flask, jsonify, request
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "FLASK_SECRET_KEY", secrets.token_hex(32)
)
csrf = CSRFProtect(app)


@app.after_request
def add_security_headers(response):
    """Apply browser security controls to every application response."""
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; base-uri 'self'; form-action 'self'; "
        "frame-ancestors 'none'"
    )
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = (
        "camera=(), geolocation=(), microphone=()"
    )
    response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/")
def home():
    """Return the small application page discovered by OWASP ZAP."""
    return """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <title>DevSecOps Secure App</title>
      </head>
      <body>
        <h1>DevSecOps Secure App</h1>

        <form action="/search" method="get">
          <label for="q">Search</label>
          <input id="q" name="q" type="text">
          <button type="submit">Search</button>
        </form>

        <p><a href="/hash?value=demo">Generate a SHA-256 example</a></p>
      </body>
    </html>
    """


@app.get("/health")
def health():
    """Return application health for tests and the CI pipeline."""
    return jsonify(status="ok", application="devsecops-secure-app")


@app.get("/search")
def search():
    """Display user input only after HTML escaping it."""
    safe_query = escape(request.args.get("q", ""), quote=True)
    return f"<h1>Search results</h1><p>You searched for: {safe_query}</p>"


@app.get("/hash")
def secure_hash():
    """Return a SHA-256 digest for the supplied demonstration value."""
    value = request.args.get("value", "demo")
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return jsonify(value=value, sha256=digest)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
