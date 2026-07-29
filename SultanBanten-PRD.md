# Product Requirement Document (PRD)
## SIAGAPIM — Sistem Informasi Analisis Gema Aktual Pimpinan

**Nama sebelumnya:** SULTAN BANTEN  
**Fokus produk:** Media monitoring isu aktual yang menyangkut pimpinan (pantauan harian)  
**Kategori:** Government Media Monitoring, Crisis Response & Media Engagement Platform  
**Dokumen Acuan:** Rancangan Aksi Perubahan (RAP) PKA (historis: Sultan Banten)  
**Sumber Intelijen:** Mata Bathin — OSINT Media Intelligence Platform  
**Stack Teknologi:** Python Flask (Backend API) & Vue.js 3 (Frontend)  
**Status Dokumen:** Final — Siap Pengembangan (rebrand SIAGAPIM)

---

## Daftar Isi
1. [Ringkasan Eksekutif & Latar Belakang](#1-ringkasan-eksekutif--latar-belakang)
2. [Integrasi dengan Mata Bathin](#2-integrasi-dengan-mata-bathin)
3. [Hubungan PRD dengan RAP](#3-hubungan-prd-dengan-rap)
4. [Arsitektur Sistem](#4-arsitektur-sistem)
5. [Tiga Pilar Utama & Fitur Produk](#5-tiga-pilar-utama--fitur-produk)
6. [Spesifikasi Hak Akses Pengguna](#6-spesifikasi-hak-akses-pengguna)
7. [Kebutuhan Non-Fungsional](#7-kebutuhan-non-fungsional)
8. [Mapping SOP ke Fitur Sistem](#8-mapping-sop-ke-fitur-sistem)
9. [Output/Deliverable Sistem](#9-outputdeliverable-sistem)
10. [Rencana Rilis & Pengembangan](#10-rencana-rilis--pengembangan)
11. [Manajemen Risiko](#11-manajemen-risiko)

---

## 1. Ringkasan Eksekutif & Latar Belakang

Biro Administrasi Pimpinan (Adpim) Setda Provinsi Banten memerlukan **platform media monitoring dan aksi respons** yang terpadu untuk memantau berita/isu aktual yang menyangkut pimpinan setiap hari, serta menindaklanjuti hasil analisis intelijen media secara cepat, terstruktur, dan akuntabel.

**SIAGAPIM** (*Sistem Informasi Analisis Gema Aktual Pimpinan*) adalah platform *media monitoring, crisis response & media engagement* yang berfungsi sebagai **ujung tombak pantauan dan aksi** dari intelligence yang dihasilkan oleh sistem **Mata Bathin** (OSINT Media Intelligence Platform). Jika Mata Bathin adalah "otak" yang mendeteksi, menganalisis, dan memberikan peringatan dini, maka SIAGAPIM adalah "tangan" yang bertindak: memantau isu pimpinan, memvalidasi ke OPD, memproduksi konten klarifikasi, mendistribusikan ke media mitra, mengamplifikasi via ASN dan KOL, serta melacak efektivitas respons.

### 1.1 Pembagian Peran

| Aspek | Mata Bathin (Intel Engine) | SIAGAPIM (Media Monitoring & Action) |
|---|---|---|
| **Fungsi utama** | OSINT collection, AI agent analysis, risk scoring, early warning, rekomendasi | Validasi OPD, produksi konten, diseminasi media, amplifikasi ASN/KOL, tracking respons |
| **Sumber data** | RSS, portal berita, YouTube, media sosial publik | Output intelligence dari Mata Bathin via API |
| **Output** | Issue brief, narrative card, risk alert, rekomendasi tindakan | Konten klarifikasi, rilis terdistribusi, laporan amplifikasi, SLA report |
| **Pengguna** | OSINT analyst, media analyst | PR officer, tim kreatif, OPD, ASN, KOL, pimpinan daerah |
| **Teknologi** | Python FastAPI + LangGraph + PostgreSQL + Next.js | Python Flask + Vue.js + SQLite/PostgreSQL |

### 1.2 Alur End-to-End

```
[Internet / Media Sosial]
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                     MATA BATHIN PIPELINE                         │
│                                                                  │
│  Source Connectors → Ingestion → Enrichment → AI Agents         │
│  → Issue Intelligence → Risk Scoring → Early Warning            │
│  → Briefing → Recommendation                                    │
│                                                                  │
│  OUTPUT: Alert + Issue Brief + Evidence Pack + Recommended       │
│          Action                                                  │
└──────────────────────────────┬──────────────────────────────────┘
                               │ API (REST/Webhook)
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SULTAN BANTEN PLATFORM                       │
│                                                                  │
│  1. Crisis Room ← Menerima alert & issue brief dari Mata Bathin │
│     │                                                            │
│  2. Validasi OPD ← Verifikasi data ke OPD teknis terkait        │
│     │                                                            │
│  3. Produksi Konten ← Buat klarifikasi, infografis, video       │
│     │                                                            │
│  4. Approval Pimpinan ← Review & approve sebelum diseminasi     │
│     │                                                            │
│  5. Media Blast ← Distribusi ke media mitra via WA/Email        │
│     │                                                            │
│  6. Amplifikasi ASN ← Mission board untuk ASN siber             │
│     │                                                            │
│  7. KOL Campaign ← Koordinasi dengan influencer lokal           │
│     │                                                            │
│  8. Monitoring & Laporan ← Track efektivitas + SLA compliance   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Integrasi dengan Mata Bathin

### 2.1 Data yang Diterima dari Mata Bathin

SULTAN BANTEN mengonsumsi data dari Mata Bathin melalui REST API dengan format sebagai berikut:

| Data Stream | Deskripsi | Frekuensi | Mapping ke Fitur Sultan Banten |
|---|---|---|---|
| **Alert Krisis** | Notifikasi isu dengan risk level (R0-R5), "why now", evidence summary | Real-time | F.01 Dashboard Deteksi Isu |
| **Issue Brief** | Ringkasan isu: aktor, narasi, sentimen, timeline, evidence pack | Per isu terdeteksi | F.01, F.03 |
| **Risk Assessment** | Risk score, feature snapshot, rationale, confidence | Update sesuai aktivitas isu | F.01 Dashboard |
| **Narrative Card** | Narrative statement, supporting evidence, aktor publik | Per perkembangan narasi | F.04 (acuan konten) |
| **Recommendation** | Opsi tindakan dari Mata Bathin beserta evidence basis | Saat alert dikeluarkan | F.01, F.04 |
| **Executive Brief** | Brief harian/mingguan untuk pimpinan | Terjadwal (daily/weekly) | F.14 Dashboard Eksekutif |

### 2.2 Data yang Dikirim ke Mata Bathin (Feedback Loop)

SULTAN BANTEN mengirimkan data umpan balik ke Mata Bathin untuk pembelajaran berkelanjutan:

| Data Umpan Balik | Deskripsi | Manfaat |
|---|---|---|
| **Action Taken** | Tindakan yang diambil atas rekomendasi | Mata Bathin belajar efektivitas rekomendasi |
| **OPD Validation Result** | Hasil validasi data dari OPD teknis | Meningkatkan akurasi verification agent |
| **Media Response** | Waktu tayang dan kesesuaian pemberitaan | Mengukur dampak diseminasi |
| **Outcome Assessment** | Dampak setelah respons dilakukan | Lesson learning agent |
| **Manual Correction** | Koreksi analis terhadap hasil AI | Fine-tuning model |

### 2.3 SLA Integrasi

- **Waktu pengiriman alert:** Maksimal 5 menit setelah Mata Bathin menghasilkan alert
- **Availability endpoint:** Minimal 99% selama jam kerja (08.00-17.00)
- **Retry mechanism:** 3x percobaan dengan exponential backoff
- **Fallback:** Jika integrasi terganggu, data dapat diinput manual oleh admin Crisis Room

---

## 3. Hubungan PRD dengan RAP

| Output RAP | Diakomodasi PRD | Keterangan |
|---|---|---|
| **Keputusan Gubernur** (payung hukum) | Tidak | Domain regulasi — diluar cakupan PRD |
| **SK Tim Kerja Sultan Banten** | Tidak | Domain organisasi — diluar cakupan PRD |
| **SOP Alur Koordinasi Kontra-Isu** | **Ya — terintegrasi** | Fitur memetakan setiap tahapan SOP |
| **SLA Media Mitra** | **Ya — fitur monitoring** | SLA Compliance Tracker |
| **Aplikasi/Dashboard Sultan Banten** | **Ya — inti PRD** | Seluruh fitur dalam PRD |
| **Panduan Teknis Tim** | Tidak | Domain dokumentasi manual |
| **Laporan Simulasi & Monitoring** | **Ya — fitur generate report** | Laporan otomatis dari sistem |

---

## 4. Arsitektur Sistem

### 4.1 Diagram Arsitektur

```
┌────────────────────────────────────────────────────────────────────┐
│                        MATA BATHIN                                  │
│  ┌─────────┐ ┌──────────┐ ┌───────────┐ ┌───────────────────┐     │
│  │ OSINT   │ │AI Agent  │ │ Risk &    │ │ Brief &          │     │
│  │ Pipeline│ │Workflow  │ │ Early     │ │ Recommendation   │     │
│  │         │ │          │ │ Warning   │ │ Engine            │     │
│  └─────────┘ └──────────┘ └───────────┘ └───────────────────┘     │
└──────────────────────────┬─────────────────────────────────────────┘
                           │ REST API / Webhook
                           ▼
┌────────────────────────────────────────────────────────────────────┐
│                     SULTAN BANTEN                                   │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                   BACKEND (Python Flask)                      │   │
│  │                                                               │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐   │   │
│  │  │Auth &    │ │Crisis    │ │Media     │ │Amplification  │   │   │
│  │  │RBAC      │ │Room API  │ │Hub API   │ │API (ASN+KOL)  │   │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └───────────────┘   │   │
│  │                                                               │   │
│  │  ┌──────────┐ ┌──────────┐ ┌────────────────────────────┐   │   │
│  │  │Content   │ │Report &  │ │Integrasi Gateway           │   │   │
│  │  │Manager   │ │Export    │ │(Mata Bathin Connector)     │   │   │
│  │  └──────────┘ └──────────┘ └────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                           │                                          │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                   DATABASE (SQLite / PostgreSQL)              │   │
│  │  Pengguna | Isu | Konten | Media | SLA | ASN | KOL | Laporan │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                   FRONTEND (Vue.js 3)                         │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐   │   │
│  │  │Crisis    │ │Media Hub │ │Mission   │ │Dashboard      │   │   │
│  │  │Room Page │ │Pages     │ │Board     │ │Eksekutif      │   │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └───────────────┘   │   │
│  └──────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────┘
```

### 4.2 Stack Teknologi

| Layer | Teknologi | Alasan |
|---|---|---|
| **Backend API** | Python Flask | Setup cepat (PKA 8 minggu), ekosistem Python matang, mudah integrasi |
| **Frontend** | Vue.js 3 + Composition API | Ringan, rendering cepat untuk real-time dashboard |
| **CSS Framework** | Tailwind CSS | Styling cepat dan konsisten |
| **Chart** | Chart.js | Visualisasi grafik sentimen & data |
| **Database** | SQLite (dev/demo) → PostgreSQL (produksi) | SQLite untuk demo portabel, migrasi ke PG untuk produksi |
| **Integrasi Mata Bathin** | REST API + Webhook | Komunikasi berbasis JSON, fault-isolated |
| **Notifications** | Web Notification + integrasi WhatsApp Gateway | Real-time alert ke tim |

### 4.3 Database Schema (Core Tables)

```
users                    — Manajemen pengguna & RBAC
issues                   — Isu yang diterima dari Mata Bathin (alert + brief)
issue_evidence           — Evidence pack dari Mata Bathin
opd_validation           — Tracking validasi data ke OPD
content_items            — Konten klarifikasi yang diproduksi
content_approvals        — Alur approval konten
media_partners           — Database media mitra
media_sla_logs           — Log kepatuhan SLA media
media_blast_logs         — Log pengiriman rilis
missions                 — Mission board untuk ASN siber
mission_participation    — Partisipasi ASN dalam misi
kol_partners             — Direktori KOL lokal
kol_campaigns            — Tracking campaign KOL
reports                  — Laporan yang dihasilkan sistem
audit_logs               — Log aktivitas sistem
```

---

## 5. Tiga Pilar Utama & Fitur Produk

### Pilar 1: SULTAN Crisis Room (Pusat Komando & Kontra-Isu)

Fitur untuk menerima intelijen dari Mata Bathin, memvalidasi ke OPD, dan memproduksi konten klarifikasi.

| Kode | Nama Fitur | Deskripsi | Sumber Data |
|---|---|---|---|
| **F.01** | **Dashboard Crisis Room** | Menampilkan daftar isu aktif, alert real-time dari Mata Bathin, risk level (R0-R5), dan ringkasan issue brief. Sentimen, narasi, dan aktor publik ditampilkan dari data Mata Bathin. | **Mata Bathin API** (Issue Brief, Alert, Risk Assessment) |
| **F.02** | **ALERT Sistem Krisis** | Notifikasi otomatis (web + WhatsApp/Telegram) saat Mata Bathin mengirimkan alert dengan risk level R3+ atau saat batas waktu respons terlampaui. | **Mata Bathin API** (Early Warning) |
| **F.03** | **Validasi Data ke OPD Teknis** | Mengirim permintaan data/klarifikasi ke OPD terkait. OPD menerima notifikasi dan merespon dengan data pendukung. Tracking status: Waiting → Validated → Rejected. Evidence dari Mata Bathin dilampirkan otomatis. | Input OPD + **Mata Bathin Evidence Pack** |
| **F.04** | **Hub Konten Klarifikasi** | Ruang kerja tim editor untuk memproduksi konten klarifikasi: rilis teks, infografis "Banten Meluruskan Fakta", unggahan video. **Narrative card dari Mata Bathin** menjadi acuan dalam menyusun narasi tandingan. Dilengkapi alur review & approval. | Tim editor + **Mata Bathin Narrative Card** |
| **F.05** | **Arsip Isu & Konten** | Database seluruh isu yang pernah ditangani, dapat dicari. Setiap isu memiliki: issue brief dari Mata Bathin, evidence pack, timeline respons, konten yang diproduksi, dan hasil akhir. | **Mata Bathin** + log aktivitas SULTAN |

### Pilar 2: SULTAN Media Hub (Jaringan Amplifikasi Massa)

Fitur untuk mengelola kemitraan media dan distribusi rilis ke publik.

| Kode | Nama Fitur | Deskripsi |
|---|---|---|
| **F.06** | **Database Media Mitra** | Manajemen data redaksi media mitra: nama media, kontak pemred, nomor WA, email, wilayah coverage, kanal darurat krisis. |
| **F.07** | **SLA Compliance Tracker** | Merekam dan memonitor kinerja media mitra: waktu tayang rilis klarifikasi, kesesuaian isi, kepatuhan terhadap SLA 1 jam. Menampilkan peringkat dan histori kepatuhan. |
| **F.08** | **One-Click Media Blast** | Diseminasi massal: sekali klik, sistem mengirimkan draf rilis/klarifikasi secara simultan ke seluruh kontak media mitra via WhatsApp Gateway dan Email. Status pengiriman tercatat (Terkirim/Gagal). |
| **F.09** | **Agenda Setting Planner** | Kalender editorial untuk merencanakan konten positif (prestasi pembangunan, penghargaan Gubernur) yang disuplai ke media secara berkala. Mendukung strategi *flooding the market*. |

### Pilar 3: SULTAN Cyber Troops & KOL Management

Fitur untuk mengelola pasukan digital organik (ASN) dan kemitraan Key Opinion Leader (KOL).

| Kode | Nama Fitur | Deskripsi |
|---|---|---|
| **F.10** | **Mission Board ASN Siber** | Halaman khusus yang menampilkan instruksi harian: tautan media sosial resmi yang perlu diamplifikasi (Like, Share, Comment). Setiap misi memiliki durasi dan target. Narasi dari Mata Bathin bisa dijadikan sumber bahan komentar. |
| **F.11** | **Log Partisipasi ASN** | Mencatat kontribusi ASN dalam setiap misi. Statistik per OPD/SKPD. Fitur export rekap untuk pelaporan pimpinan. |
| **F.12** | **Direktori KOL Lokal** | Manajemen data Key Opinion Leader: nama, platform, followers, engagement rate, topik, status kontrak, histori kerjasama. |
| **F.13** | **KOL Campaign Tracker** | Tracking deliverables KOL: konten yang sudah dipublikasikan, jadwal tayang, performance (views, likes, comments), status realisasi anggaran. |
| **F.14** | **Dashboard Eksekutif Pimpinan** | View-only untuk Khabiro/Sekda/Gubernur: peta sentimen publik (dari Mata Bathin), rekap krisis aktif, grafik distribusi rilis, statistik partisipasi ASN & KOL. Brief harian otomatis dari Mata Bathin dan SULTAN BANTEN. |

---

## 6. Spesifikasi Hak Akses Pengguna

| Peran (Role) | Fitur yang Dapat Diakses |
|---|---|
| **Super Admin** (Kepala Bagian / Tim Adpim) | F.01 s.d. F.14 — Full access, manajemen user, konfigurasi sistem |
| **Tim Editor/Kreatif** | F.01 (view), F.03 (view), F.04 (create/edit), F.05, F.08 (trigger blast), F.09 |
| **Admin OPD Teknis** | F.03 (terbatas — hanya menerima & merespon validasi) |
| **Pimpinan** (Khabiro / Sekda / Gubernur) | F.14 (view-only), F.01 (view-only), F.05 (view), F.07 (view) |
| **Admin Media & KOL** | F.06 (manage), F.07 (view), F.09, F.12 (manage), F.13 (manage) |
| **User ASN Banten** | F.10 (view missions), F.11 (input partisipasi) |

---

## 7. Kebutuhan Non-Fungsional

### 7.1 Keamanan
- Autentikasi JWT + RBAC untuk setiap level pengguna
- Input sanitasi (SQL Injection & XSS prevention)
- Session timeout otomatis
- Enkripsi data sensitif
- Audit log untuk setiap perubahan status isu dan approval

### 7.2 Performa
- Dashboard utama: load time maksimal 3 detik
- Media Blast ke 50+ kontak: maksimal 5 menit
- API response: p95 < 2 detik untuk query umum

### 7.3 Desain UI/UX
- Tema warna: biru tua (#1B3A5C), merah (#C0392B), emas (#D4A017) — identitas Banten
- Responsif (mobile-first) — akses via smartphone oleh ASN dan pimpinan
- Navigasi intuitif dengan sidebar dan dashboard cards

### 7.4 Keandalan
- Uptime minimal 99% selama jam kerja
- Backup database terjadwal
- Mode offline: nomor telepon dan WA manual tetap tersedia
- **Integrasi dengan Mata Bathin** memiliki circuit breaker agar kegagalan Mata Bathin tidak menghentikan SULTAN BANTEN

### 7.5 Kompatibilitas
- Browser: Chrome, Firefox, Safari, Edge (2 versi terbaru)
- Platform: Desktop (utama) dan Mobile

---

## 8. Mapping SOP ke Fitur Sistem

> **Diagram proses lengkap (Mermaid):** lihat [`BUSINESS_PROCESS.md`](./BUSINESS_PROCESS.md) — alur end-to-end, lifecycle isu/konten, validasi OPD, diseminasi paralel, agenda setting, dan feedback loop ke Mata Bathin (selaras implementasi aplikasi).

```
SOP: DETEKSI ISU (oleh Mata Bathin)
  → Dikirim ke SULTAN BANTEN via API
  → F.01 Dashboard Crisis Room
  → F.02 ALERT Sistem Krisis
       ↓
SOP: VALIDASI DATA KE OPD TEKNIS
  → F.03 Validasi Data ke OPD
  → Evidence Mata Bathin dilampirkan otomatis
       ↓
SOP: PRODUKSI KONTEN KLARIFIKASI
  → F.04 Hub Konten Klarifikasi
  → Narrative card dari Mata Bathin sebagai acuan counter-narrative
       ↓
SOP: DISEMINASI MASIF
  → F.08 One-Click Media Blast (ke media mitra)
  → F.10 Mission Board ASN Siber (amplifikasi organik)
  → F.13 KOL Campaign Tracker (amplifikasi influencer)
       ↓
MONITORING & EVALUASI
  → F.07 SLA Compliance Tracker (monitoring kepatuhan media)
  → F.11 Log Partisipasi ASN (monitoring aktivasi)
  → F.14 Dashboard Eksekutif (ringkasan untuk pimpinan)
  → Dikirim kembali ke Mata Bathin sebagai feedback (lesson learning)
```

---

## 9. Output/Deliverable Sistem

### 9.1 Output Cetak/Export (PDF/Excel)

1. **Laporan Penanganan Krisis** — kronologi, tindakan, hasil, dilengkapi evidence dari Mata Bathin
2. **Laporan Aktivitas Media (SLA Report)** — rekap kepatuhan media mitra
3. **Rekap Partisipasi ASN per OPD** — statistik amplifikasi
4. **Laporan Kinerja KOL & Campaign** — deliverable dan performance
5. **Executive Brief** — ringkasan situasi + rekomendasi (di-generate oleh Mata Bathin, ditampilkan di SULTAN BANTEN)

### 9.2 Output Digital

1. **Arsip Isu & Konten** — database histori isu yang dapat dicari
2. **Log Diseminasi** — riwayat pengiriman rilis ke media
3. **Notifikasi & Alert** — real-time dari Mata Bathin ke SULTAN BANTEN
4. **Dashboard Visual** — grafik interaktif untuk pimpinan

---

## 10. Rencana Rilis & Pengembangan

### Milestone 8 Minggu (Sesuai RAP PKA)

#### Minggu 1-2: Persiapan & Regulasi
- Finalisasi PRD
- Setup project Flask + Vue.js
- **Setup koneksi dengan Mata Bathin** (API key, endpoint, format data)
- Desain database schema
*(Bersamaan dengan penyusunan Kepgub & SK Tim Kerja)*

#### Minggu 3-4: Pengembangan Pilar 1 (Crisis Room) + Integrasi Mata Bathin
**Backend:**
- Setup Flask project + SQLite database
- API Autentikasi & Manajemen User (RBAC)
- **API Gateway integrasi Mata Bathin** — consume alert, issue brief, evidence pack
- API Crisis Room (CRUD isu, tracking status)
- API Validasi OPD
- API Konten Klarifikasi & Approval

**Frontend:**
- Setup Vue.js + Tailwind CSS, tema Banten
- Halaman Login & Dashboard Crisis Room
- Alert notification widget
- Halaman Validasi OPD
- Halaman Produksi Konten

**Deliverable:** Crisis Room + Integrasi Mata Bathin siap demo

#### Minggu 5-6: Pengembangan Pilar 2 & 3 (Media Hub + Cyber Troops)
**Backend:**
- API Database Media Mitra & SLA Tracker
- API One-Click Media Blast (WA + Email)
- API Agenda Setting Planner
- API Mission Board ASN
- API Log Partisipasi ASN
- API Direktori KOL & Campaign Tracker

**Frontend:**
- Halaman Manajemen Media & SLA Dashboard
- Halaman Media Blast
- Halaman Kalender Editorial
- Halaman Mission Board ASN
- Halaman Direktori KOL

**Deliverable:** Media Hub & Cyber Troops module siap demo

#### Minggu 7-8: Integrasi, Dashboard Eksekutif & Finalisasi
**Backend:**
- Dashboard Eksekutif API (F.14)
- API Generate Report/Export (PDF/Excel)
- **Integrasi Executive Brief dari Mata Bathin**
- Final bug fixing & optimasi

**Frontend:**
- Dashboard Eksekutif untuk Pimpinan
- Halaman Export/Laporan
- Integrasi Executive Brief dari Mata Bathin
- UAT & Final testing
- Persiapan demo seminar PKA

**Deliverable:**
- Aplikasi SULTAN BANTEN v1.0 — siap demo
- **Integrasi Mata Bathin** — data intelijen mengalir ke SULTAN BANTEN
- Laporan UAT
- Panduan pengguna singkat

---

## 11. Manajemen Risiko

| Risiko | Dampak | Mitigasi |
|---|---|---|
| **Integrasi Mata Bathin belum siap tepat waktu** | Crisis Room tidak mendapat data intelijen otomatis | Siapkan mode manual input — admin dapat memasukkan data isu secara manual |
| **Waktu pengembangan mepet (8 minggu)** | Fitur tidak selesai semua | Prioritas: F.01, F.03, F.04, F.08, F.10 (wajib) vs F.07, F.13, F.14 (nice-to-have) |
| **Data dari Mata Bathin tidak akurat** | Respons berdasarkan analisis salah | Validasi data ke OPD teknis (F.03) sebagai quality gate sebelum produksi konten |
| **Koneksi internet tidak stabil** | Gangguan akses sistem | Mode offline: data krisis dicetak, kontak manual via telepon |
| **Ketergantungan pada Mata Bathin** | Jika Mata Bathin down, SULTAN BANTEN lumpuh | Circuit breaker: SULTAN BANTEN tetap berfungsi untuk tugas non-intelijen (agenda setting, ASN mission, KOL management) |
| **API Mata Bathin berubah** | Integrasi rusak | API versioning + contract test pada integrasi gateway |
| **User kesulitan adaptasi** | Partisipasi ASN rendah | Panduan pengguna + sosialisasi |

---

## Lampiran A: Glossary / Daftar Istilah

| Istilah | Definisi |
|---|---|
| **SULTAN BANTEN / SIAGAPIM** | *(nama sebelumnya SULTAN BANTEN)* Sistem Informasi Analisis Gema Aktual Pimpinan — media monitoring & respons isu pimpinan |
| **Mata Bathin** | Manajemen Analisis Terpadu Berita, Aktor, Tren, Hoax, Isu, Dan Narasi — platform OSINT Media Intelligence |
| **Biro Adpim** | Biro Administrasi Pimpinan Setda Provinsi Banten |
| **SLA** | Service Level Agreement — perjanjian tingkat layanan dengan media mitra |
| **KOL** | Key Opinion Leader — tokoh berpengaruh / influencer lokal |
| **OPD** | Organisasi Perangkat Daerah |
| **SOP** | Standar Operasional Prosedur |
| **OSINT** | Open Source Intelligence — intelijen dari sumber terbuka |
| **Risk Level R0-R5** | Tingkat risiko: Informational (R0), Observe (R1), Watch (R2), Elevated (R3), High (R4), Critical (R5) |
| **UAT** | User Acceptance Testing — pengujian oleh pengguna akhir |
| **Flooding the Market** | Strategi membanjiri ruang publik dengan konten positif |

---

## Lampiran B: Skema Integrasi Data Mata Bathin → SULTAN BANTEN

### B.1 Alert Krisis (dari Mata Bathin)

```json
{
  "alert_id": "MB-20260719-001",
  "type": "crisis_alert",
  "severity": "R3",
  "title": "Hoaks Kebijakan Infrastruktur",
  "why_now": "Volume mention meningkat 300% dalam 2 jam terakhir",
  "issue_summary": "Beredar informasi palsu mengenai...",
  "risk_assessment": {
    "level": "Elevated",
    "velocity": 0.85,
    "sentiment_negative_ratio": 0.72,
    "source_diversity": 8,
    "confidence": 0.78
  },
  "evidence_pack_url": "https://...",
  "recommended_actions": ["verify_with_opd", "prepare_clarification"],
  "created_at": "2026-07-19T14:30:00Z",
  "callback_url": "https://sultan-banten/api/v1/mb-callback/alert-001"
}
```

### B.2 Feedback dari SULTAN BANTEN ke Mata Bathin

```json
{
  "alert_id": "MB-20260719-001",
  "action_taken": {
    "opd_validated": true,
    "opd_notes": "Data dikonfirmasi valid oleh Dinas PUPR",
    "clarification_produced": true,
    "clarification_url": "https://...",
    "media_blast_sent": true,
    "media_count": 25,
    "asn_missions_created": 3,
    "kol_engaged": 2
  },
  "outcome": {
    "media_publication_time_avg": "45 minutes",
    "estimated_reach": 150000,
    "notes": "Isu mulai mereda 6 jam setelah klarifikasi"
  },
  "submitted_at": "2026-07-19T20:00:00Z"
}
```

---

*Dokumen ini disusun sebagai bagian dari Aksi Perubahan PKA Sultan Banten. Platform SULTAN BANTEN merupakan action layer yang mengonsumsi data intelijen dari Mata Bathin dan bertanggung jawab atas eksekusi respons komunikasi Pemerintah Provinsi Banten.*
