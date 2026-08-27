# DevSecOps Security Pipeline

> **Warning:** This repository begins with an intentionally vulnerable Flask
> application for local security-scanner training. Do not deploy it publicly.

The application provides a minimal target for demonstrating:

- SonarQube static application security testing (SAST)
- Trivy software composition analysis (SCA)
- Trivy container image scanning
- OWASP ZAP dynamic application security testing (DAST)

## Current training weaknesses

- Reflected cross-site scripting in `/search`
- A fake hard-coded administrator password
- Weak MD5 hashing in `/hash`
- Flask debug mode enabled
- Missing common HTTP security headers
- Intentionally outdated Python dependencies

These weaknesses will later be fixed to demonstrate a failed pipeline followed
by successful remediation.

## Run locally

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python app.py
```

Open <http://localhost:5000> or check <http://localhost:5000/health>.

## Run tests

```bash
python -m pytest
```

## Run with Docker

```bash
docker build -t secure-flask-app .
docker run --rm -p 5000:5000 secure-flask-app
```

The container definition intentionally omits a non-root `USER` instruction so
that a later Trivy misconfiguration scan has an additional training finding.

## Phase 5 security gate setup

The GitHub Actions workflow now runs these checks in order:

1. pytest
2. SonarQube Cloud SAST and Quality Gate
3. Trivy dependency, secret, and Dockerfile misconfiguration scan

Before pushing the workflow, configure the following GitHub repository values:

- Secret: `SONAR_TOKEN`
- Variable: `SONAR_ORGANIZATION`
- Variable: `SONAR_PROJECT_KEY`

Copy the organization and project keys from the SonarQube Cloud project setup.
Trivy is configured to fail the security gate for Medium, High, or Critical
findings. No vulnerability exceptions are configured in this training version.
