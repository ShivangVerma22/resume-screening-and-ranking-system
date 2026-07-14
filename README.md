# Resume Screening & Candidate Ranking System

Simple TF-IDF based resume ranking tool. No database, no LLM.

## Run locally (without Docker)

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Run with Docker

```bash
docker build -t resume-screening-app .
docker run -p 8501:8501 resume-screening-app
```

Or using Docker Compose:

```bash
docker-compose up --build
```

App will be available at: http://localhost:8501

## CI/CD Pipeline (GitHub Actions)

Located at `.github/workflows/ci-cd.yml`. It runs automatically on every
push/PR to the `main` branch:

1. **CI job** — installs dependencies, checks Python syntax, builds the Docker image (sanity check).
2. **CD job** — on push to `main` only, logs into Docker Hub and pushes the image with two tags: `latest` and the commit SHA.

### Required GitHub Secrets

Go to your repo → **Settings → Secrets and variables → Actions** and add:

| Secret name | Value |
|---|---|
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | A Docker Hub access token (not your password) — generate one at hub.docker.com → Account Settings → Security |

Once these are set, every push to `main` will automatically build and publish
your Docker image to Docker Hub.
