"""Intentionally vulnerable Flask app for local DevSecOps training only.

Do not expose this application to the internet or use its patterns in a real app.
The weaknesses are present so SonarQube, Trivy, and OWASP ZAP have findings to
detect during later phases of the project.
"""

import hashlib

from flask import Flask, jsonify, request


app = Flask(__name__)

# Intentionally insecure: fake hard-coded training credential for SAST testing.
ADMIN_PASSWORD = "admin123"


@app.get("/")
def home():
    """Return a tiny page that gives ZAP a few routes to discover."""
    return """
    <!doctype html>
    <html lang="en">
      <head><title>DevSecOps Training App</title></head>
      <body>
        <h1>DevSecOps Training App</h1>

        <form action="/search" method="get">
          <label for="q">Search</label>
          <input id="q" name="q" type="text">
          <button type="submit">Search</button>
        </form>

        <form action="/login" method="post">
          <label for="username">Username</label>
          <input id="username" name="username" type="text">
          <label for="password">Password</label>
          <input id="password" name="password" type="password">
          <button type="submit">Log in</button>
        </form>
      </body>
    </html>
    """


@app.get("/health")
def health():
    """Health endpoint used by tests and the future CI pipeline."""
    return jsonify(status="ok", application="devsecops-training-app")


@app.get("/search")
def search():
    """Intentionally reflect input without escaping it (reflected XSS)."""
    query = request.args.get("q", "")
    return f"<h1>Search results</h1><p>You searched for: {query}</p>"


@app.post("/login")
def login():
    """Intentionally use a hard-coded password and simplistic authentication."""
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    if username == "admin" and password == ADMIN_PASSWORD:
        return jsonify(message="Login successful", user=username)

    return jsonify(message="Invalid credentials"), 401


@app.get("/hash")
def weak_hash():
    """Intentionally use MD5 so the SAST scanner can report weak cryptography."""
    value = request.args.get("value", "demo")
    digest = hashlib.md5(value.encode("utf-8")).hexdigest()  # noqa: S324
    return jsonify(value=value, md5=digest)


if __name__ == "__main__":
    # Intentionally insecure: debug mode must never be enabled in production.
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
