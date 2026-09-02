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

The frontend **never** talks to the droplet's raw IP address — all requests 
go through the `api.mf-member-monitor.com` domain, which Nginx handles.


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
- **Status:** Broken since Nginx was introduced / reconfigured
- **Symptom:** Data is not being written into the database with the current 
  configuration

### Likely cause
Before Nginx and Docker networking were set up, the ETL script probably 
connected to Postgres via `localhost` or a public/direct IP + exposed port. 
Now that Postgres:
- runs in its own container, and
- is only reachable via the internal `app-network` using the hostname 
  `postgres-db`,

...the ETL script needs to either:
1. **Run inside the same Docker network** (e.g., as another container attached 
   to `app-network`, or a one-off container run with `--network app-network`), 
   so it can resolve `postgres-db`, **or**
2. If it runs from outside Docker (e.g., directly on the droplet or from 
   your laptop), it needs a connection string using an address Postgres 
   actually exposes — which currently doesn't exist, since the DB isn't 
   published anywhere. You'd need to either expose a port for it (not 
   recommended for security) or run the ETL as a container on `app-network`.

**Fill in / to investigate:**
- Where does the ETL currently run from? `[FILL IN — laptop / droplet / other]`
- What connection string/host does it currently use? `[FILL IN]`
- ETL script location: `[FILL IN]`
- Source(s) of data being extracted: `[FILL IN]`

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

## 10. Open Items / TODO

- [ ] Fix ETL → database connection (Section 8)
- [ ] Add automated scheduling for ETL (cron / systemd timer / Airflow, etc.)
- [ ] Document database schema
- [ ] Document Flask API endpoints
- [ ] Add backup strategy for PostgreSQL
- [ ] Move SSH password out of any shared documentation
- [ ] Document `docker-compose.yml` / container restart policies
- [ ] Consider CI/CD for backend deploys (currently manual?) `[FILL IN]`