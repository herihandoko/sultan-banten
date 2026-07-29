# Panduan Pengguna — SULTAN BANTEN

**Versi aplikasi:** v0.1.1  
**Instansi:** Biro Administrasi Pimpinan (Adpim) Setda Provinsi Banten  
**Dokumen:** User Manual (penggunaan operasional)

---

## 1. Apa itu SULTAN BANTEN?

**SULTAN BANTEN** (*Sistem Utama Layanan Tanggap Informasi, Manajemen Opini, dan Branding Digital Terpadu*) adalah platform **crisis response & media engagement**.

| Sistem | Peran |
|--------|--------|
| **Mata Bathin** | “Otak” — deteksi isu, sentimen, early warning (OSINT) |
| **SULTAN BANTEN** | “Tangan” — validasi OPD, produksi konten, blast media, ASN, KOL, laporan |

Alur ringkas:

```
Deteksi isu → Alert → Validasi OPD → Produksi konten → Diseminasi
(media blast / misi ASN / KOL) → Monitoring & laporan
```

---

## 2. Cara masuk

1. Buka aplikasi di browser (contoh lokal: `http://127.0.0.1:5173`).
2. Masukkan **Username** dan **Password**.
3. Klik **Masuk**.

Setelah login, menu yang tampil menyesuaikan **role** Anda.

### 2.1 Akun demo (lingkungan development)

| Username | Password | Peran |
|----------|----------|--------|
| `admin` | `admin123` | Super Admin — akses penuh |
| `editor` | `editor123` | Tim Editor/Kreatif |
| `pimpinan` | `pimpinan123` | Pimpinan (Khabiro/Sekda/Gubernur) |
| `opd` | `opd123` | Admin OPD Teknis (Dinas PUPR) |
| `opd_kes` | `opd123` | Admin OPD Dinas Kesehatan |
| `media` | `media123` | Admin Media & KOL |
| `asn` | `asn123` | User ASN (Diskominfo) |
| `asn2` / `asn3` | `asn123` | ASN tambahan (Dinkes / PUPR) |

> Ganti password default sebelum dipakai di lingkungan nyata.

### 2.2 Keluar

Klik tombol **Keluar** di pojok kanan atas.

---

## 3. Navigasi umum

### Sidebar
- Menu utama di kiri (desktop) / drawer (mobile).
- Tombol **hamburger** di header: ciutkan/lebarkan sidebar.
- Saat sidebar ciut, **hover ikon** menampilkan nama menu.
- Lonjong **lonceng** (Alert): notifikasi krisis (R3+ / overdue).

### Footer
Menampilkan nama aplikasi dan versi (contoh: `SULTAN BANTEN · v0.1.1`).

---

## 4. Ringkasan menu per peran

| Menu | Super Admin | Editor | Pimpinan | OPD | Media/KOL | ASN |
|------|:-----------:|:------:|:--------:|:---:|:---------:|:---:|
| Dashboard | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Crisis Room | ✓ | ✓ | ✓ | ✓ | — | — |
| Validasi OPD | ✓ | ✓ | ✓ | ✓ | — | — |
| Hub Konten | ✓ | ✓ | ✓ | — | — | — |
| Media Hub | ✓ | ✓ | ✓ | — | ✓ | — |
| Agenda | ✓ | ✓ | ✓ | — | ✓ | — |
| Mission Board | ✓ | ✓ | ✓ | — | — | ✓ |
| KOL | ✓ | — | — | — | ✓ | — |
| Arsip | ✓ | ✓ | ✓ | — | ✓ | — |
| Eksekutif | ✓ | — | ✓ | — | — | — |
| Laporan | ✓ | ✓ | ✓ | — | ✓* | — |
| Users | ✓ | — | — | — | — | — |

\*Admin Media/KOL: laporan SLA & KOL saja.

---

## 5. Panduan fitur

### 5.1 Dashboard (beranda)

**Untuk:** ringkasan situasi publik (intelijen).

Yang ditampilkan:
- Total mention, sentimen negatif, reach, isu aktif
- Tren volume & sentimen 7 hari
- Alert isu aktif (klik untuk ke detail isu bila tersedia)
- Sebaran per platform (X, portal, Instagram, WA)

> Sebagian metrik bisa bertanda **Data demo · stub Mata Bathin** jika koneksi live belum aktif. Crisis Room tetap bisa dipakai dengan input manual.

---

### 5.2 Crisis Room

**Untuk:** pusat komando isu.

**Melihat isu**
1. Buka **Crisis Room**.
2. Daftar isu menampilkan judul, risk level (R0–R5), status, sumber.
3. Klik isu untuk membuka **Detail**.

**Membuat isu manual** (Editor / Super Admin) — fallback jika Mata Bathin down:
1. Klik **+ Input Isu**.
2. Isi judul, ringkasan, *why now*, risk level.
3. Simpan.

**Status isu (alur tipikal)**

| Status | Arti |
|--------|------|
| `open` | Baru masuk / perlu ditindak |
| `validating` | Sedang diminta klarifikasi OPD |
| `producing` | Produksi konten klarifikasi |
| `approved` | Konten sudah disetujui |
| `disseminated` | Sudah disebar (blast, dll.) |
| `closed` | Selesai ditutup |

Di detail isu Anda dapat: lihat evidence, minta validasi OPD, lihat konten terkait, ubah status (sesuai wewenang).

**Risk level**

| Level | Arti singkat |
|-------|----------------|
| R0–R1 | Informasional / observe |
| R2 | Watch |
| R3 | Elevated — biasanya memicu alert |
| R4 | High |
| R5 | Critical |

---

### 5.3 Alert krisis (lonceng)

- Muncul untuk isu **R3+** atau respons **terlambat** (overdue).
- Klik lonceng → daftar alert → buka isu terkait.
- Browser bisa meminta izin **Notifikasi** — izinkan agar alert muncul di desktop.
- Pengiriman WhatsApp/Telegram di demo bersifat **simulasi**; di produksi dihubungkan ke gateway resmi.

---

### 5.4 Validasi OPD

**Editor / Super Admin — minta validasi**
1. Buka detail isu → buat permintaan validasi.
2. Isi nama OPD / catatan permintaan.
3. Status isu menjadi `validating`.

**Admin OPD — respon**
1. Login sebagai OPD (`opd` / `opd123`).
2. Buka **Validasi OPD**.
3. Pilih permintaan status **waiting**.
4. Isi catatan / data pendukung.
5. Pilih **Validated** atau **Rejected**.

Setelah semua validasi selesai (minimal ada yang validated), isu biasanya lanjut ke status `producing`.

---

### 5.5 Hub Konten Klarifikasi

**Editor — buat & ajukan**
1. Buka **Hub Konten** → buat konten baru (rilis teks / infografis / video).
2. Hubungkan ke isu; bila ada *narrative card* dari Mata Bathin, bisa dipakai sebagai acuan “Banten Meluruskan Fakta”.
3. Simpan draft → **Submit review**.

**Pimpinan / Super Admin — approval**
1. Buka konten berstatus `in_review`.
2. **Approve** atau **Reject** (beri catatan bila perlu).
3. Konten approved siap di-blast.

---

### 5.6 Media Hub

Tiga fungsi utama:

**A. Database media mitra**
- Tambah/edit media: nama, pemred, WA, email, coverage, kanal krisis.
- Nonaktifkan mitra yang tidak dipakai.

**B. One-click media blast**
1. Pilih konten yang **approved/published**.
2. Pilih mitra (atau semua aktif) dan kanal (WA / email / keduanya).
3. Klik kirim — status **Terkirim / Partial / Gagal** tercatat di log.
4. Di lingkungan demo, pengiriman **disimulasikan**.

**C. SLA Compliance Tracker (target 60 menit)**
1. Catat waktu tayang rilis di media.
2. Sistem hitung menit respons & kepatuhan SLA.
3. Lihat ranking kepatuhan media.

---

### 5.7 Agenda Setting

Kalender konten **positif** (*flooding the market*): pembangunan, penghargaan, sosial, ekonomi, dll.

1. Pilih bulan dengan panah ‹ ›.
2. **+ Agenda** → isi judul, tanggal, tema, kanal, target media.
3. Update status: planned → in_production → ready → published (atau batalkan).

---

### 5.8 Mission Board ASN

**Admin (Editor / Super Admin) — buat misi**
1. Judul, instruksi, tautan postingan resmi, tipe aksi (Like / Share / Comment).
2. Target jumlah partisipasi; opsional tautkan ke isu.
3. Simpan — status `active`.

**ASN — ikut misi**
1. Login `asn` / `asn123`.
2. Buka misi aktif → buka tautan → lakukan aksi di medsos.
3. Klik ikut serta; isi bukti URL / catatan bila diminta.

**Statistik**
Tab stats menampilkan partisipasi per OPD (untuk pelaporan).

---

### 5.9 KOL (Key Opinion Leader)

**Direktori KOL**
- Nama, platform, handle, followers, engagement, topik, status kontrak.

**Campaign tracker**
- Buat campaign: deliverable URL, jadwal, views/likes/comments, anggaran & status anggaran.
- Update status hingga published.

---

### 5.10 Arsip

Pencarian histori isu & konten:
- Filter kata kunci, status, risk, tanggal.
- Buka detail → **timeline** (isu → validasi → konten → blast).

---

### 5.11 Dashboard Eksekutif

View ringkas untuk pimpinan:
- Executive brief
- KPI isu aktif, validasi menunggu, blast, ASN, reach KOL
- Grafik distribusi risiko, pipeline konten, ASN per OPD
- Daftar isu prioritas R3+

---

### 5.12 Laporan & Export (PDF / Excel)

Menu **Laporan**:

| Laporan | Isi |
|---------|-----|
| Penanganan Krisis | Daftar isu, risk, status, validasi, konten, blast |
| SLA Media | Log kepatuhan & ringkasan |
| Rekap ASN | Partisipasi per OPD + daftar misi |
| Kinerja KOL | Campaign & metrik |
| Executive Brief | KPI & rekomendasi ringkas |

1. Pilih jenis laporan.
2. (Opsional) isi ID isu untuk filter laporan krisis.
3. Klik **PDF** atau **Excel** — file terunduh.

---

### 5.13 Manajemen User (Super Admin)

Menu **Users**:
1. **+ User** — username, nama, email, password, **role**, OPD (bila Admin OPD).
2. **Edit** — ubah role, email, password (opsional), status aktif.
3. Nonaktifkan user (kecuali akun sendiri).

Role yang tersedia: Super Admin, Tim Editor/Kreatif, Admin OPD Teknis, Pimpinan, Admin Media & KOL, User ASN Banten.

---

## 6. Skenario latihan (walkthrough demo)

Gunakan beberapa browser/profil atau logout–login bergantian.

### Skenario A — Penanganan isu lengkap

1. Login **admin** atau **editor** → Crisis Room → **Input Isu** (atau tunggu webhook Mata Bathin).
2. Detail isu → minta **Validasi OPD**.
3. Login **opd** → Validasi OPD → **Validated**.
4. Login **editor** → Hub Konten → buat rilis → **Submit review**.
5. Login **pimpinan** → approve konten.
6. Login **editor**/**media** → Media Hub → **Blast**.
7. (Opsional) buat misi ASN & campaign KOL.
8. Tutup isu (status `closed`) atau lihat **Arsip** / **Laporan**.

### Skenario B — ASN amplify

1. Admin buat misi di Mission Board.
2. Login **asn** → join misi + isi bukti.

### Skenario C — Konten positif rutin

1. Login editor/media → **Agenda** → rencanakan konten bulanan.
2. Produksi di Hub Konten / supply ke media sesuai agenda.

---

## 7. Tips & pemecahan masalah

| Masalah | Solusi |
|---------|--------|
| Menu tidak muncul | Role Anda memang terbatas — cek tabel di bagian 4 |
| Login gagal | Cek username/password; pastikan backend API jalan |
| Alert tidak berbunyi | Izinkan notifikasi browser; pastikan ada isu R3+ |
| Blast “terkirim” tapi WA tidak masuk | Di demo masih simulasi; hubungkan gateway produksi |
| Metrik Dashboard “demo” | Set `MATA_BATHIN_BASE_URL` di `.env` untuk data live |
| Export gagal | Pastikan login role yang diizinkan; coba refresh token (login ulang) |
| Layar sempit | Gunakan tombol menu mobile; sidebar jadi drawer |

---

## 8. Keamanan penggunaan

- Jangan bagikan akun pimpinan / super admin.
- Logout setelah selesai di perangkat bersama.
- Ganti password demo di lingkungan resmi.
- Data kontak media bersifat operasional — jaga kerahasiaannya.

---

## 9. Bantuan teknis singkat

| Layanan | Alamat default (dev) |
|---------|----------------------|
| Frontend | `http://127.0.0.1:5173` |
| API Backend | `http://127.0.0.1:5001` |
| Health check | `GET /api/health` |

Spesifikasi produk lengkap: lihat `SultanBanten-PRD.md`.  
Setup teknis developer: lihat `README.md`.

---

*Dokumen ini disusun untuk mendukung operasional dan demo SULTAN BANTEN sebagai action layer Adpim Provinsi Banten.*
