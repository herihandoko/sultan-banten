# SIAGAPIM

**Sistem Informasi Analisis Gema Aktual Pimpinan**

Media monitoring untuk memantau berita dan isu aktual yang menyangkut pimpinan — pantauan harian untuk Biro Adpim Setda Provinsi Banten.

Action layer dari intelijen **Mata Bathin** (Flask API + Vue.js 3). Nama sebelumnya: SULTAN BANTEN.

## Stack

| Layer | Teknologi |
|---|---|
| Backend | Python Flask, SQLAlchemy, JWT, Flask-Migrate |
| Frontend | Vue.js 3, Vite, Pinia, Vue Router, Tailwind CSS, Chart.js |
| Database | SQLite (dev) / PostgreSQL (Docker & produksi) |

## Struktur

```
sultan-banten/          # folder repo (historis)
├── backend/            # Flask API
├── frontend/           # Vue.js 3 SPA
├── docker-compose.yml
└── SultanBanten-PRD.md # spesifikasi (akan diselaraskan ke SIAGAPIM)
```

## Setup dengan Docker (PostgreSQL existing)

Project memakai Postgres yang sudah jalan (`cms-vplus-postgres-1`, port host **5433**).

```bash
# 1. Pastikan DB aplikasi sudah ada (sekali saja)
docker exec cms-vplus-postgres-1 \
  psql -U postgres -c "CREATE DATABASE sultan_banten OWNER postgres;"

# 2. Sesuaikan kredensial di .env.docker jika perlu, lalu build & run
docker compose up -d --build
```

| Layanan | URL |
|---|---|
| Frontend (nginx) | http://localhost:8080 |
| API Flask | http://localhost:5001 |
| Postgres | `cms-vplus-postgres-1:5432` (dari container) / `localhost:5433` (dari host) |

Seed demo jalan otomatis saat backend start (`RUN_SEED=true`). Matikan dengan `RUN_SEED=false` di `.env.docker`.

Backend join network Docker `cms-vplus_default` agar bisa resolve hostname Postgres.

### Standalone (VM / tanpa Postgres external)

```bash
# di server
git clone https://github.com/herihandoko/sultan-banten.git
cd sultan-banten
cp .env.standalone.example .env.standalone   # atau buat dari template
# set CORS_ORIGINS ke http://<IP-VM>:8080
docker compose -f docker-compose.standalone.yml --env-file .env.standalone up -d --build
```

App: `http://<IP>:8080` · API: `http://<IP>:5001`

### Backend lokal + Postgres Docker

```bash
cd backend
# di .env:
# DATABASE_URL=postgresql+psycopg2://postgres:secret@127.0.0.1:5433/sultan_banten
pip install -r requirements.txt
python seed.py
python wsgi.py
```

## Setup cepat (SQLite lokal)

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # sudah ada .env untuk lokal
python seed.py         # buat DB + role + user demo
python wsgi.py         # http://127.0.0.1:5001
```

### Frontend

```bash
cd frontend
npm install
npm run dev            # http://localhost:5173
```

Vite mem-proxy `/api` ke backend di port `5001`.

## Akun demo

| Username | Password | Role |
|---|---|---|
| `admin` | `admin123` | Super Admin |
| `editor` | `editor123` | Tim Editor/Kreatif |
| `pimpinan` | `pimpinan123` | Pimpinan |
| `asn` | `asn123` | User ASN Banten (Diskominfo) |
| `asn2` | `asn123` | User ASN (Dinas Kesehatan) |
| `asn3` | `asn123` | User ASN (Dinas PUPR) |
| `opd` | `opd123` | Admin OPD Teknis (Dinas PUPR) |
| `opd_kes` | `opd123` | Admin OPD Teknis (Dinas Kesehatan) |
| `media` | `media123` | Admin Media & KOL |

## API inti

- `GET /api/health`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `GET /api/issues` — Crisis Room / isu aktual
- `POST /api/issues` — input manual isu (fallback)
- `POST /api/mata-bathin/webhook/alert` — ingest alert Mata Bathin
- `GET /api/mata-bathin/status`

## Integrasi Mata Bathin

Konfigurasi di `backend/.env`:

```
MATA_BATHIN_ENABLED=true
MATA_BATHIN_BASE_URL=https://...
MATA_BATHIN_API_KEY=...
```

Jika integrasi belum siap, Crisis Room tetap jalan dengan **input manual**.

## Dokumentasi

- [Panduan Pengguna (User Manual)](./USER_MANUAL.md)
- [Business Process](./BUSINESS_PROCESS.md)
- [SultanBanten-PRD.md](./SultanBanten-PRD.md) — spesifikasi fitur F.01–F.14 (rebrand SIAGAPIM)
