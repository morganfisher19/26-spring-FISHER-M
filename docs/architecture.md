# Architecture — MF Member Monitor

## 1. Overview

Full-stack web application with a manual ETL pipeline feeding a PostgreSQL 
database, a Flask API backend, and a React (Vite) frontend.

| Layer      | Technology               | Hosting                           |
|------------|--------------------------|-----------------------------------|
| Frontend   | React + Vite             | Vercel                            |
| Backend    | Flask (Python), Docker   | DigitalOcean Droplet              |
| Database   | PostgreSQL 15, Docker    | DigitalOcean Droplet (same host)  |
| Reverse Proxy | Nginx                 | DigitalOcean Droplet (same host)  |
| ETL        | Python                   | Run manually, currently **broken**|

**Public domains:**
- Frontend: `https://www.mf-member-monitor.com`
- API: `https://api.mf-member-monitor.com`

---

## 2. Architecture Diagram

                          Internet
                             │
             ┌───────────────┴───────────────┐
             ▼                               ▼
https://www.mf-member-monitor.com https://api.mf-member-monitor.com
             │                               │
             ▼                               ▼
    Vercel (React + Vite)                  Nginx
                             (SSL termination, reverse proxy)
                                             │
                                             ▼
                            127.0.0.1:5000 (localhost only)
                                             │
                                             ▼
                                    Flask (Docker container)
                                             │
                                             ▼
                                app-network (Docker bridge network)
                                             │
                                             ▼
                            postgres-db (Docker container, PostgreSQL 15)

[ETL Pipeline] ──(manual run) ──▶ postgres-db ⚠️ BROKEN — see Section 6


---

## 3. Frontend

- **Framework:** React + Vite
- **Hosting:** Vercel
- **Domain:** `https://www.mf-member-monitor.com`
- **Served over:** HTTPS
- **API base URL used by frontend:** `https://api.mf-member-monitor.com`

All frontend requests go through the `api.mf-member-monitor.com` domain, 
which Nginx handles.


## 4. Backend

- **Framework:** Flask (Python)
- **Runs inside:** Docker container on the DigitalOcean droplet
- **Container port:** 5000 (internal)
- **Published as:** `127.0.0.1:5000` — bound to localhost only, not exposed 
  to the public internet
- **Reachable only by:** processes on the droplet itself — i.e., Nginx

### Docker image contents
- Python
- Flask
- Project dependencies (`requirements.txt`)
- Application source code

This packaging means the app runs identically regardless of the host OS.

**Fill in:**
- Flask app entry point / file name: `app.py`
- Key API routes/endpoints: `https://api.mf-member-monitor.com/api/health`
- Environment variables the Flask app expects (DB connection string, secret 
  keys, etc.): `[FILL IN]`

---

## 5. Reverse Proxy (Nginx)

Nginx sits between the public internet and the Flask container.

**Responsibilities:**
- Receives all incoming HTTPS requests to `api.mf-member-monitor.com`
- Terminates SSL (HTTPS → HTTP internally)
- Routes requests to Flask at `127.0.0.1:5000`
- Hides the backend from direct public access

**Benefits:**
- Single public entry point
- Centralized HTTPS handling
- Backend stays private
- Easier to scale/add services later

**Fill in:**
- Config file location on droplet: `[FILL IN — typically /etc/nginx/sites-available/...]`
- SSL cert provider/method (e.g. Let's Encrypt / Certbot): `[FILL IN]`
- Any rate limiting / header rules configured: `[FILL IN]`

---

## 6. Database

- **Engine:** PostgreSQL 15
- **Hosting:** Docker container on the DigitalOcean droplet
- **Public exposure:** None — not published to the internet
- **Access:** Only via the Docker network, using the internal hostname 
  `postgres-db` (Docker's built-in DNS resolves this — no public IP needed)

**Fill in:**
- Database name: `[FILL IN]`
- Schema / key tables: `[FILL IN]`
- Backup strategy: `[FILL IN — currently none noted]`

---

## 7. Docker Networking

A custom Docker bridge network (`app-network`) connects the backend 
containers so they can reach each other by name without exposing ports 
publicly.

app-network (Docker bridge)
├── flask-app (Flask backend, internal port 5000)
└── postgres-db (PostgreSQL 15, internal port 5432)


Flask connects to Postgres using the hostname `postgres-db`, not an IP.

**Fill in:**
- `docker-compose.yml` location: `[FILL IN]`
- Container restart policy: `[FILL IN]`

---

## 8. ETL Pipeline — ⚠️ Currently Broken

- **Trigger:** Manual (no scheduler/cron currently)
- **Status:** Broken since Nginx was introduced
- **Symptom:** Data is not being written into the database with the current 
  configuration

### Cause
Originally, the PostgreSQL container was publicly exposed:
68.183.104.231:5432
        ↓
    PostgreSQL

Your local pipeline therefore used:
DB_HOST = 68.183.104.231
DB_PORT = 5432

Then we changed your Docker setup to stop exposing PostgreSQL publicly. Your current Docker setup showed:
postgres-db
PORTS: 5432/tcp

rather than:
0.0.0.0:5432->5432/tcp

At the same time, we put flask-app and postgres-db on the Docker network app-network, allowing Flask to connect to PostgreSQL using:

postgres-db:5432

That's why your Flask application started working again.

Your current architecture is therefore:

                        INTERNET
                           │
                           ▼
                    Vercel frontend
                           │
                           ▼
              api.mf-member-monitor.com
                           │
                           ▼
                         Nginx
                           │
                           ▼
                    127.0.0.1:5000
                           │
                           ▼
                    Flask/Gunicorn
                           │
                           ▼
                    Docker network
                     app-network
                           │
                           ▼
                    postgres-db:5432

There is no longer a path from the Internet to PostgreSQL at 68.183.104.231:5432.

That's exactly is why your local pipeline gets:

connection to server at "68.183.104.231", port 5432 failed: Connection refused

Your get_connection() function is:

def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

And your configuration is:

DB_HOST = os.getenv("SERVER")
DB_PORT = 5432

So when you run the pipeline on your Windows computer, it effectively says:

Connect to:

68.183.104.231
port 5432

But we deliberately closed that route.

Therefore:

Windows pipeline
       │
       │ 68.183.104.231:5432
       ▼
DigitalOcean
       ✕
PostgreSQL isn't publicly exposed

The pipeline never gets as far as executing upsert_members(), upsert_bills(), etc. It fails at:

conn = get_connection()

which is exactly what your traceback shows.

### Quick Fix Solution

There are now two different ways to connect to your database, depending on where the code is running.

Flask running on DigitalOcean

Flask is inside Docker, so it should use:

postgres-db:5432

because postgres-db is the Docker DNS name on app-network.

Pipeline running on your Windows computer

Your computer is outside Docker and outside the droplet, so it cannot use:

postgres-db

and it also cannot currently use:

68.183.104.231:5432

because we closed public PostgreSQL access.

So how do we fix the pipeline?

Since you said you ultimately want the pipeline to run automatically on the droplet, I would not undo the security change.

For the temporary period where you still run the pipeline from Windows, the cleanest solution is an SSH tunnel.

It gives your laptop a temporary, encrypted path into the private PostgreSQL database:

Your Windows computer
        │
        │ localhost:5432
        ▼
    SSH tunnel
        │
        │ encrypted SSH connection
        ▼
DigitalOcean Droplet
        │
        ▼
PostgreSQL

Your database remains private.

---

## 9. Where to Run Commands

### Local machine (laptop)
- Frontend development
- Git operations
- Testing the public site (`https://www.mf-member-monitor.com`)
- Testing the public API (`curl https://api.mf-member-monitor.com`)
- DNS testing (`nslookup`)

### DigitalOcean Droplet (production server)
- Docker container management
- Flask backend
- PostgreSQL
- Nginx configuration
- SSL certificates
- Production logs
- System administration

**SSH access:**
ssh root@68.183.104.231

Password: `[FILL IN — store in password manager, not this file]`

---

## 10. Config files
Environment files store variables that should be hidden from git and users. Separated into development and production environments

.env files:
- .env.dev (local development)
- .env.prod (production development)

Config files extract hidden environment variables in a centralized location so rest of code base can aceess that information.

config files:
- pipeline/config.py
- backend/config.py
- frontend/vite.config.ts


## 11. Open Items / TODO

- [ ] Fix ETL → database connection (Section 8)
- [ ] Add automated scheduling for ETL (cron / systemd timer / Airflow, etc.)
- [ ] Document database schema
- [ ] Document Flask API endpoints
- [ ] Add backup strategy for PostgreSQL
- [ ] Move SSH password out of any shared documentation
- [ ] Document `docker-compose.yml` / container restart policies
- [ ] Consider CI/CD for backend deploys (currently manual?) `[FILL IN]`