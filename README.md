# SULTAN BANTEN

Sistem Utama Layanan Tanggap Informasi, Manajemen Opini, dan Branding Digital Terpadu — platform crisis response & media engagement untuk Biro Adpim Setda Provinsi Banten.

Action layer dari intelijen **Mata Bathin** (Flask API + Vue.js 3).

## Stack

| Layer | Teknologi |
|---|---|
| Backend | Python Flask, SQLAlchemy, JWT, Flask-Migrate |
| Frontend | Vue.js 3, Vite, Pinia, Vue Router, Tailwind CSS, Chart.js |
| Database | SQLite (dev) → PostgreSQL (produksi) |

## Struktur

```
sultan-banten/
├── backend/          # Flask API
├── frontend/         # Vue.js 3 SPA
└── SultanBanten-PRD.md
```

## Setup cepat

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

## API inti (milestone setup)

- `GET /api/health`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `GET /api/issues` — Crisis Room
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

## Referensi

## Dokumentasi

- [Panduan Pengguna (User Manual)](./USER_MANUAL.md) — cara pakai per role & skenario demo
- [SultanBanten-PRD.md](./SultanBanten-PRD.md) — spesifikasi fitur F.01–F.14 dan rencana 8 minggu
