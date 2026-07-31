# MLH Portfolio

A personal portfolio site built with Flask, MySQL/MariaDB, and Docker — created during the [MLH Fellowship](https://fellowship.mlh.io/) (Meta, Production Engineering track). It showcases my experience, education, and hobbies, and includes a small guestbook-style timeline feature backed by a real database, plus a live server status endpoint for basic observability.

**Live site:** [mlh-chloe.duckdns.org](https://mlh-chloe.duckdns.org)

## Features

- **Home page** — bio, work experience, education, and certifications, rendered from data via Jinja templates
- **Hobbies page** — image gallery of hobbies, using the same reusable template pattern
- **Timeline / guestbook** — visitors can leave a message (name, email, content) that's persisted to MySQL and displayed via a JSON API
- **Status page** — live server health (CPU, memory, disk, DB connectivity) exposed through a `/api/system_status` endpoint
- **Dynamic nav bar** — page list is defined once in the backend and rendered across every template

## Architecture

```
                    ┌────────────────────┐
  HTTPS (443) ────► │  nginx (reverse     │
  HTTP  (80)  ────► │  proxy + TLS)       │
                    │  Let's Encrypt      │
                    │  auto-renew via     │
                    │  certbot            │
                    └─────────┬──────────┘
                              │ proxy_pass
                              ▼
                    ┌────────────────────┐
                    │  Flask app          │
                    │  (Gunicorn/Flask    │
                    │   dev server)       │
                    │  Jinja2 templates   │
                    └─────────┬──────────┘
                              │ Peewee ORM
                              ▼
                    ┌────────────────────┐
                    │  MariaDB / MySQL    │
                    └────────────────────┘
```

- **Backend:** [Flask](https://flask.palletsprojects.com/) serves both server-rendered HTML pages and a small JSON API.
- **ORM/Database:** [Peewee](http://docs.peewee-orm.com/) models map to a MariaDB/MySQL instance for persisting timeline posts.
- **Reverse proxy / TLS:** nginx sits in front of the app, terminates HTTPS with a Let's Encrypt certificate (auto-provisioned/renewed by [certbot](https://certbot.eff.org/)), and forwards requests to the Flask container.
- **Rate limiting:** nginx applies `limit_req` to `POST /api/timeline_post` only (1 request/min per client IP), protecting the write path from abuse while leaving read traffic unrestricted.
- **Containerization:** each layer (app, database, nginx) runs as its own service via Docker Compose, with a separate compose file for local development vs. production.
- **Deployment:** `redeploy-site.sh` pulls the latest `main`, then rebuilds and restarts the production stack — a simple, scriptable deploy path for a small VPS.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| ORM | Peewee |
| Database | MariaDB / MySQL |
| Templating | Jinja2 |
| Reverse proxy / TLS | nginx, Let's Encrypt (certbot) |
| Containerization | Docker, Docker Compose |
| Testing | pytest |

## Project Structure

```
app/
├── __init__.py          # Flask app, routes, Peewee models
├── static/
│   ├── img/              # site images
│   └── styles/           # CSS
└── templates/            # Jinja2 templates (index, hobbies, timeline, status)
tests/
├── conftest.py            # pytest fixtures (isolated in-memory SQLite for tests)
├── test_app.py            # route/endpoint tests
└── test_db.py              # Peewee model tests
user_conf.d/
└── myportfolio.conf       # nginx server config (TLS, reverse proxy, rate limiting)
docker-compose.yml          # local development stack (app + MariaDB)
docker-compose.prod.yml     # production stack (app + MariaDB + nginx/certbot)
Dockerfile                  # Flask app image
redeploy-site.sh             # pull latest main + rebuild/restart prod stack
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Home page (about, experience, education, certifications) |
| `GET` | `/hobbies` | Hobbies gallery page |
| `GET` | `/timeline` | Timeline/guestbook page |
| `GET` | `/api/timeline_post` | Returns all timeline posts as JSON, newest first |
| `POST` | `/api/timeline_post` | Creates a timeline post (`name`, `email`, `content`) |
| `GET` | `/status` | Server status page |
| `GET` | `/api/system_status` | JSON snapshot of CPU, memory, disk usage, and DB connectivity |

## Getting Started

### Option 1: Docker (recommended)

This spins up the Flask app and a MariaDB database together.

```bash
git clone https://github.com/chloe-ek/MLH_Portfolio.git
cd MLH_Portfolio
cp example.env .env   # fill in the values described below
docker compose up --build
```

The site will be available at `http://localhost:5000`.

### Option 2: Local Python environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp example.env .env   # fill in the values described below, pointing MYSQL_HOST at a running MySQL/MariaDB instance
export FLASK_ENV=development
flask run
```

The site will be available at `http://localhost:5000`.

### Environment Variables

Copy `example.env` to `.env` and set:

| Variable | Description |
|---|---|
| `URL` | Base URL used when rendering pages (e.g. `localhost:5000`) |
| `MYSQL_DATABASE` | Database name |
| `MYSQL_USER` | Database user |
| `MYSQL_PASSWORD` | Database password |
| `MYSQL_HOST` | Database host (`mysql` when using Docker Compose) |
| `MYSQL_ROOT_PASSWORD` | Root password for the MariaDB container |

## Testing

```bash
./run_test.sh
```

This installs dependencies and runs the pytest suite, which covers page rendering, the timeline API, and the Peewee models against an isolated in-memory SQLite database.

## Deployment

The production stack (`docker-compose.prod.yml`) adds an nginx container in front of the app for TLS termination and reverse proxying, configured via `user_conf.d/myportfolio.conf`. To deploy the latest `main` branch to the server:

```bash
./redeploy-site.sh
```

This pulls the latest commit, then rebuilds and restarts all containers with zero manual steps.
