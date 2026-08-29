# DevSecOps Security Pipeline

> The `vulnerable-demo-v1` tag contains the intentionally vulnerable training
> version. The `main` branch contains the remediated application.

The application provides a minimal target for demonstrating:

- SonarQube static application security testing (SAST)
- Trivy software composition analysis (SCA)
- Trivy container image scanning
- OWASP ZAP dynamic application security testing (DAST)

## Remediation demonstrated

- Escaped untrusted search input to prevent reflected cross-site scripting
- Removed the unnecessary hard-coded administrator login
- Replaced MD5 with SHA-256
- Disabled Flask debug mode and used Gunicorn in the container
- Added CSP, anti-clickjacking, content-type and privacy headers
- Upgraded and separated runtime and development dependencies
- Changed to a smaller Alpine image running as a non-root user

The preserved tag and current branch demonstrate a failed pipeline followed by
security remediation.

## Before and after results

These counts were observed during the local remediation scans. Vulnerability
databases change over time, so future totals may differ.

| Security check | Vulnerable tag | Remediated main branch |
| --- | ---: | ---: |
| Unit tests | 5 passed | 5 passed |
| Trivy dependency vulnerabilities | 16 | 0 |
| Trivy Dockerfile misconfigurations | 1 | 0 |
| Trivy image vulnerabilities | 101 | 0 |
| ZAP blocking findings | 2 | 0 |
| Container runtime user | root | `appuser` (UID 10001) |

## Run locally

```bash
python -m venv .venv
python -m pip install -r requirements-dev.txt
python app.py
```

Open <http://localhost:5000> or check <http://localhost:5000/health>.

## Run tests

```bash
python -m pytest --cov=app --cov-report=term-missing --cov-report=xml:coverage.xml
```

The XML report is imported by SonarQube Cloud. The Quality Gate requires at
least 80% coverage on new code; the current test suite covers 97% locally.

## Run with Docker

```bash
docker build -t devsecops-secure-app .
docker run --rm -p 5000:5000 devsecops-secure-app
```

The container uses Gunicorn and runs as the unprivileged `appuser` account.

## Automated security pipeline

The GitHub Actions workflow now runs these checks in order:

1. pytest tests and XML coverage report generation
2. SonarQube Cloud SAST, coverage import, and Quality Gate
3. Trivy dependency, secret, and Dockerfile misconfiguration scan
4. Docker image build
5. Trivy Docker image vulnerability scan
6. Temporary application container startup and health check
7. OWASP ZAP baseline DAST scan against the running container
8. Final security gate enforcement
9. Approved Docker image publication to GitHub Container Registry (GHCR)

Before pushing the workflow, configure the following GitHub repository values:

- Secret: `SONAR_TOKEN`
- Variable: `SONAR_ORGANIZATION`
- Variable: `SONAR_PROJECT_KEY`

Copy the organization and project keys from the SonarQube Cloud project setup.
Trivy is configured to fail the security gate for Medium, High, or Critical
findings. No vulnerability exceptions are configured in this training version.

ZAP performs a passive baseline scan in an isolated Docker network. The rules
in `.zap/rules.tsv` promote two Medium-risk findings to blocking failures:
missing anti-clickjacking protection and a missing Content Security Policy.
HTML, JSON, and Markdown ZAP reports are uploaded to the GitHub Actions run as
an artifact and retained for 14 days. The temporary application is removed
after every scan, including failed scans.

## Conditional image publishing

On pushes to `main`, an image is published to GHCR only when every test and
security check passes. Pull requests are scanned but never publish images. Each
approved image uses the immutable Git commit SHA as its tag:

```text
ghcr.io/ahirronak/devsecops-security-pipeline:<commit-sha>
```

The workflow uses GitHub's temporary `GITHUB_TOKEN`, so no registry password or
personal access token needs to be stored. The intentionally vulnerable version
is preserved by the Git tag `vulnerable-demo-v1`; its failed security gate
prevents it from being published.
