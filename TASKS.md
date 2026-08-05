# Backlog Task — SIAGAPIM

**Proyek:** SIAGAPIM (*Sistem Informasi Analisis Gema Aktual Pimpinan*)  
**Instansi:** Biro Adpim Setda Provinsi Banten  
**Mulai sprint/backlog:** 1 Agustus 2026  
**Sumber informasi:** Biro Administrasi Pimpinan (Adpim) Setda Provinsi Banten

Keterangan prioritas: **P0** wajib / kritis · **P1** tinggi · **P2** sedang · **P3** nice-to-have  
Status singkat: *(Done)* sudah ada di aplikasi · *(In Progress)* parsial · *(Todo)* belum / perlu penguatan

---

## Epic A — Fondasi & Infrastruktur

### T-001 · Setup proyek Flask + Vue + RBAC
| Field | Isi |
|---|---|
| **Judul Task** | Setup fondasi aplikasi (API, SPA, auth JWT/RBAC) |
| **Deskripsi** | Membangun kerangka aplikasi SIAGAPIM agar tim bisa login dan bekerja sesuai peran. Meliputi: (1) backend Flask API + SQLAlchemy; (2) frontend Vue 3 + Vite + Tailwind + Pinia/Router; (3) login JWT dengan masa berlaku token; (4) RBAC untuk role `super_admin`, `editor`, `opd_admin`, `pimpinan`, `media_kol_admin`, `asn` — setiap role hanya melihat menu/fitur yang diizinkan; (5) seed data awal (role + user demo) agar siap UAT/demo. **Selesai jika:** user bisa login, `/api/health` OK, menu mengikuti role, dan akun demo berfungsi. |
| **Prioritas** | P0 |
| **Rentang Tanggal** | 1–7 Agustus 2026 |
| **Komentar** | Sudah berjalan di lokal & Docker; akun demo tersedia. |
| **Sumber Informasi** | Biro Administrasi Pimpinan (Adpim) Setda Provinsi Banten |
| **Status** | Done |

### T-002 · Database PostgreSQL + Docker deploy
| Field | Isi |
|---|---|
| **Judul Task** | Migrasi DB ke PostgreSQL & deploy Docker (dev) |
| **Deskripsi** | Memindahkan penyimpanan data dari SQLite (dev lokal) ke PostgreSQL agar siap lingkungan bersama/dev server. Meliputi: (1) konfigurasi `DATABASE_URL` (sqlite atau `postgresql+psycopg2`); (2) Docker Compose mode *standalone* (Postgres + API + Web) dan mode yang menghubungkan Postgres existing; (3) entrypoint yang menunggu DB siap, `create_all`, lalu seed; (4) deploy ke VM dev dan verifikasi health/login. **Selesai jika:** stack Docker naik, tabel terbuat di Postgres, seed user ada, frontend `:8080` dan API `:5001` bisa diakses. |
| **Prioritas** | P0 |
| **Rentang Tanggal** | 1–8 Agustus 2026 |
| **Komentar** | Standalone compose + Postgres alpine sudah dipakai di VM `10.249.101.43`. |
| **Sumber Informasi** | Biro Administrasi Pimpinan (Adpim) Setda Provinsi Banten |
| **Status** | Done |

### T-003 · Rebrand SIAGAPIM + aset visual
| Field | Isi |
|---|---|
| **Judul Task** | Rebranding SULTAN BANTEN → SIAGAPIM |
| **Deskripsi** | Mengganti identitas produk di seluruh permukaan aplikasi agar konsisten dengan nama baru dan fokus media monitoring pimpinan. Meliputi: (1) nama singkat **SIAGAPIM** + nama lengkap *Sistem Informasi Analisis Gema Aktual Pimpinan*; (2) logo/favicon memakai `pavicon.png` di login, sidebar, dan tab browser; (3) update teks di README, User Manual, Business Process, header PRD, footer laporan PDF, subject email blast, health API; (4) **tidak** mengubah label menu Crisis Room. **Selesai jika:** tidak ada branding lama yang menonjol di UI utama, dan identitas SIAGAPIM terlihat di login/dashboard. |
| **Prioritas** | P1 |
| **Rentang Tanggal** | 1–5 Agustus 2026 |
| **Komentar** | UI login/sidebar/docs sudah SIAGAPIM; logo pavicon aktif. |
| **Sumber Informasi** | Biro Administrasi Pimpinan (Adpim) Setda Provinsi Banten |
| **Status** | Done |

### T-004 · Pagination list API + UI
| Field | Isi |
|---|---|
| **Judul Task** | Pagination di seluruh fitur list |
| **Deskripsi** | Menambah paging agar daftar data tidak dimuat sekaligus (performa & UX). Meliputi: (1) helper backend `paginate()` yang mengembalikan `data` + `meta` (`page`, `per_page`, `total`, `pages`, `has_next`, `has_prev`); (2) komponen UI Prev/Next di Crisis Room, Validasi OPD, Hub Konten, Media Hub (mitra/blast/SLA), KOL, Agenda, Mission Board, Arsip (isu & konten terpisah), Users, Master OPD; (3) untuk dropdown form (OPD/mitra/KOL) tetap ambil banyak data (`per_page` tinggi) supaya pilihan tidak terpotong. **Selesai jika:** setiap list utama bisa pindah halaman, dan form dropdown masih menampilkan opsi lengkap. |
| **Prioritas** | P1 |
| **Rentang Tanggal** | 1–6 Agustus 2026 |
| **Komentar** | Dropdown master (OPD/mitra) pakai `per_page` tinggi agar tidak terpotong. |
| **Sumber Informasi** | Biro Administrasi Pimpinan (Adpim) Setda Provinsi Banten |
| **Status** | Done |

---

## Epic B — Pilar 1: Crisis Room (Kontra-Isu)

### T-005 · F.01 Dashboard Crisis Room / Isu aktif
| Field | Isi |
|---|---|
| **Judul Task** | F.01 — Dashboard Crisis Room & daftar isu |
| **Deskripsi** | Menyediakan pusat pantauan isu aktual yang menyangkut pimpinan. Meliputi: (1) daftar isu aktif dengan risk level R0–R5, status, ringkasan/why-now; (2) detail isu (brief, evidence, rekomendasi); (3) lifecycle status `open → validating → producing → approved → disseminated → closed`; (4) input manual isu jika Mata Bathin belum mengirim data; (5) dashboard ringkas di home. **Aktor:** super admin, editor, pimpinan (view). **Selesai jika:** isu bisa dibuat/dilihat/diubah statusnya, dan Crisis Room menjadi entry point penanganan isu. |
| **Prioritas** | P0 |
| **Rentang Tanggal** | 8–18 Agustus 2026 |
| **Komentar** | Modul `/crisis-room` + detail isu sudah ada; data Mata Bathin masih stub/manual jika integrasi off. |
| **Sumber Informasi** | Biro Administrasi Pimpinan (Adpim) Setda Provinsi Banten |
| **Status** | Done (integrasi live MB: In Progress) |

### T-006 · F.02 ALERT Sistem Krisis
| Field | Isi |
|---|---|
| **Judul Task** | F.02 — Alert krisis (web + overdue) |
| **Deskripsi** | Memastikan tim Adpim mendapat peringatan dini saat isu kritis muncul atau respons terlambat. Meliputi: (1) alert otomatis untuk risk R3+; (2) widget lonceng (AlertBell) + unread count + tandai dibaca; (3) browser notification; (4) pemindaian isu yang melewati batas waktu respons; (5) rencana lanjutan: kirim juga ke WhatsApp/Telegram gateway (bukan hanya web). **Aktor:** super admin, editor, pimpinan, media_kol_admin. **Selesai jika:** alert muncul di UI saat ada isu kritis/overdue; kanal eksternal dicatat sebagai dependency terpisah jika belum siap. |
| **Prioritas** | P0 |
| **Rentang Tanggal** | 8–15 Agustus 2026 |
| **Komentar** | Web notification + poll alert sudah; kanal WA/Telegram masih mock/partial. |
| **Sumber Informasi** | Biro Administrasi Pimpinan (Adpim) Setda Provinsi Banten |
| **Status** | Done (kanal WA/Telegram: Todo) |

### T-007 · F.03 Validasi Data ke OPD
| Field | Isi |
|---|---|
| **Judul Task** | F.03 — Validasi data ke OPD teknis |
| **Deskripsi** | Menjadi *quality gate* sebelum konten klarifikasi diproduksi: fakta isu diverifikasi ke OPD terkait. Meliputi: (1) editor/super admin mengirim permintaan validasi dengan memilih OPD dari master; (2) status `waiting → validated / rejected` + catatan & data pendukung dari OPD; (3) OPD admin hanya melihat permintaan OPD-nya; (4) evidence Mata Bathin tampil di konteks isu; (5) jika validated, status isu bergeser ke `validating`/`producing`. **Aktor:** editor (request), opd_admin (respon), pimpinan (view). **Selesai jika:** alur request–respon OPD tercatat dan memengaruhi status isu. |
| **Prioritas** | P0 |
| **Rentang Tanggal** | 10–20 Agustus 2026 |
| **Komentar** | Alur utama selesai; quality gate sebelum produksi konten sesuai PRD. |
| **Sumber Informasi** | Biro Administrasi Pimpinan (Adpim) Setda Provinsi Banten |
| **Status** | Done |

### T-008 · Master OPD
| Field | Isi |
|---|---|
| **Judul Task** | Master referensi OPD (dari `ct_opd.sql`) |
| **Deskripsi** | Menyediakan daftar resmi Organisasi Perangkat Daerah agar penugasan user dan validasi konsisten (bukan teks bebas). Meliputi: (1) impor/seed dari `ct_opd.sql` (~41 OPD); (2) CRUD master (nama, aktif/nonaktif) untuk super admin; (3) relasi `User.opd_id` / `opd_name`; (4) dropdown OPD di form user dan request validasi. **Selesai jika:** semua pilihan OPD di sistem mengacu ke master, dan OPD bisa dinonaktifkan tanpa menghapus histori. |
| **Prioritas** | P1 |
| **Rentang Tanggal** | 8–14 Agustus 2026 |
| **Komentar** | 41 OPD dari `ct_opd.sql` sudah di-seed. |
| **Sumber Informasi** | Biro Administrasi Pimpinan (Adpim) Setda Provinsi Banten |
| **Status** | Done |

### T-009 · F.04 Hub Konten Klarifikasi + Approval
| Field | Isi |
|---|---|
| **Judul Task** | F.04 — Produksi konten & approval pimpinan |
| **Deskripsi** | Ruang kerja editor untuk membuat narasi klarifikasi (“Banten Meluruskan Fakta”) sebelum disebar. Meliputi: (1) buat/edit konten (teks/infografis/video URL) terkait isu; (2) status `draft → in_review → approved/rejected → published`; (3) pengajuan review oleh editor; (4) approve/reject oleh pimpinan atau super admin + catatan; (5) memakai narrative card Mata Bathin sebagai acuan jika ada; (6) konten approved siap untuk Media Blast. **Selesai jika:** konten tidak bisa di-blast sebelum approved, dan reject mengembalikan ke alur edit. |
| **Prioritas** | P0 |
| **Rentang Tanggal** | 12–22 Agustus 2026 |
| **Komentar** | Lifecycle konten sesuai `BUSINESS_PROCESS.md` §4. |
| **Sumber Informasi** | Biro Administrasi Pimpinan (Adpim) Setda Provinsi Banten |
| **Status** | Done |

### T-010 · F.05 Arsip Isu & Konten
| Field | Isi |
|---|---|
| **Judul Task** | F.05 — Arsip searchable isu & konten |
| **Deskripsi** | Menyimpan dan menelusuri histori penanganan untuk akuntabilitas dan lesson learning. Meliputi: (1) pencarian kata kunci pada isu/konten; (2) filter tipe (isu/konten/semua), status, risk, sumber, rentang tanggal; (3) ringkasan arsip per isu (jumlah evidence, validasi, konten, blast); (4) timeline kronologi respons; (5) pagination terpisah untuk daftar isu dan daftar konten. **Selesai jika:** isu lama bisa ditemukan kembali beserta jejak penanganan utamanya. |
| **Prioritas** | P1 |
| **Rentang Tanggal** | 18–25 Agustus 2026 |
| **Komentar** | Endpoint `/api/archive` + UI `/arsip` sudah ada. |
| **Sumber Informasi** | Biro Administrasi Pimpinan (Adpim) Setda Provinsi Banten |
| **Status** | Done |

---

## Epic C — Pilar 2: Media Hub

### T-011 · F.06 Database Media Mitra
| Field | Isi |
|---|---|
| **Judul Task** | F.06 — Manajemen media mitra |
| **Deskripsi** | Mengelola database redaksi mitra yang jadi penerima rilis klarifikasi. Meliputi: (1) data nama media, pemred/kontak, WhatsApp, email, wilayah coverage, kanal darurat krisis, catatan; (2) status aktif/nonaktif; (3) edit & nonaktifkan tanpa menghapus histori blast/SLA. **Aktor:** super admin, editor, media_kol_admin. **Selesai jika:** mitra aktif tersedia sebagai penerima blast dan opsi pencatatan SLA. |
| **Prioritas** | P0 |
| **Rentang Tanggal** | 22–28 Agustus 2026 |
| **Komentar** | Tab Media Mitra di Media Hub. |
| **Sumber Informasi** | Biro Administrasi Pimpinan (Adpim) Setda Provinsi Banten |
| **Status** | Done |

### T-012 · F.07 SLA Compliance Tracker
| Field | Isi |
|---|---|
| **Judul Task** | F.07 — Tracker kepatuhan SLA media (1 jam) |
| **Deskripsi** | Memonitor apakah media mitra menayangkan klarifikasi sesuai SLA (target 1 jam setelah blast) dan apakah isinya sesuai. Meliputi: (1) pencatatan waktu tayang / response minutes; (2) flag content match; (3) penentuan compliant/breach; (4) ranking media berdasarkan compliance rate & rata-rata respon; (5) histori log SLA. **Selesai jika:** pimpinan/admin bisa melihat siapa yang patuh/melanggar SLA dan riwayatnya. |
| **Prioritas** | P1 |
| **Rentang Tanggal** | 25–31 Agustus 2026 |
| **Komentar** | PRD menandai F.07 sebagai nice-to-have pada risiko waktu; di app sudah tersedia. |
| **Sumber Informasi** | Biro Administrasi Pimpinan (Adpim) Setda Provinsi Banten |
| **Status** | Done |

### T-013 · F.08 One-Click Media Blast
| Field | Isi |
|---|---|
| **Judul Task** | F.08 — One-click media blast (WA + Email) |
| **Deskripsi** | Mendiseminasikan konten yang sudah disetujui ke banyak media sekaligus. Meliputi: (1) pilih konten berstatus approved/published; (2) pilih kanal WA / Email / keduanya; (3) pilih penerima (semua mitra aktif atau parsial); (4) kirim massal dan catat hasil per penerima (`sent` / `partial` / `failed`); (5) update status konten ke `published` dan isu ke `disseminated` bila berhasil; (6) picu feedback ke Mata Bathin bila relevan. **Catatan:** pengiriman saat ini masih mock/demo sampai gateway produksi siap (lihat T-026). **Selesai jika:** satu aksi blast menghasilkan log lengkap dan mengubah status isu/konten. |
| **Prioritas** | P0 |
| **Rentang Tanggal** | 22–30 Agustus 2026 |
| **Komentar** | Gateway masih mock/demo — perlu integrasi WA Gateway produksi. |
| **Sumber Informasi** | Biro Administrasi Pimpinan (Adpim) Setda Provinsi Banten |
| **Status** | Done (gateway produksi: Todo) |

### T-014 · F.09 Agenda Setting Planner
| Field | Isi |
|---|---|
| **Judul Task** | F.09 — Kalender agenda konten positif |
| **Deskripsi** | Merencanakan konten positif berkala (*flooding the market*) agar ruang publik tidak hanya diisi isu negatif. Meliputi: (1) kalender per bulan; (2) entri agenda (judul, tema, kanal, target media, tanggal rencana); (3) status `planned → in_production → ready → published` atau `cancelled`; (4) bisa berjalan independen meski Mata Bathin/Crisis Room terganggu. **Aktor:** editor, media_kol_admin, super admin; pimpinan view. **Selesai jika:** agenda bulanan bisa dikelola dan ditinjau per tanggal. |
| **Prioritas** | P1 |
| **Rentang Tanggal** | 26 Agustus – 2 September 2026 |
| **Komentar** | Independen dari alur krisis (circuit breaker PRD). |
| **Sumber Informasi** | Biro Administrasi Pimpinan (Adpim) Setda Provinsi Banten |
| **Status** | Done |

---

## Epic D — Pilar 3: ASN Cyber Troops & KOL

### T-015 · F.10 Mission Board ASN
| Field | Isi |
|---|---|
| **Judul Task** | F.10 — Mission Board ASN siber |
| **Deskripsi** | Menginstruksikan ASN untuk mengamplifikasi konten resmi di media sosial (like, share, comment). Meliputi: (1) admin/editor membuat misi (judul, instruksi, URL target, jenis aksi, target jumlah partisipan, isu terkait opsional); (2) ASN melihat misi aktif dan mencatat partisipasi (+ bukti URL opsional); (3) admin dapat menandai misi selesai/dibatalkan; (4) default landing ASN = halaman misi. **Selesai jika:** misi bisa dipublikasikan dan ASN bisa join dengan jejak partisipasi. |
| **Prioritas** | P0 |
| **Rentang Tanggal** | 22–30 Agustus 2026 |
| **Komentar** | Role ASN diarahkan ke `/missions` setelah login. |
| **Sumber Informasi** | Biro Administrasi Pimpinan (Adpim) Setda Provinsi Banten |
| **Status** | Done |

### T-016 · F.11 Log Partisipasi ASN
| Field | Isi |
|---|---|
| **Judul Task** | F.11 — Log & rekap partisipasi ASN per OPD |
| **Deskripsi** | Mengukur aktivasi ASN siber per organisasi untuk pelaporan pimpinan. Meliputi: (1) log siapa ikut misi, kapan, dari OPD mana; (2) rekap agregat per OPD/SKPD; (3) tampilan statistik di Mission Board; (4) export rekap ASN (PDF/Excel) lewat modul Laporan. **Selesai jika:** pimpinan/admin bisa melihat ranking/kontribusi OPD dan mengekspor rekap. |
| **Prioritas** | P1 |
| **Rentang Tanggal** | 28 Agustus – 4 September 2026 |
| **Komentar** | Rekap OPD di Mission Board + export via Reports. |
| **Sumber Informasi** | Biro Administrasi Pimpinan (Adpim) Setda Provinsi Banten |
| **Status** | Done |

### T-017 · F.12 Direktori KOL
| Field | Isi |
|---|---|
| **Judul Task** | F.12 — Direktori KOL lokal |
| **Deskripsi** | Menginventarisasi Key Opinion Leader lokal yang bisa diajak kampanye opini positif/klarifikasi. Meliputi: (1) data nama, platform, handle, followers, engagement rate, topik; (2) status kontrak (prospect/active/expired/terminated); (3) aktif/nonaktif; (4) ringkasan jumlah campaign terkait. **Aktor:** media_kol_admin, super admin. **Selesai jika:** KOL bisa dikelola dan dipilih saat membuat campaign. |
| **Prioritas** | P1 |
| **Rentang Tanggal** | 28 Agustus – 5 September 2026 |
| **Komentar** | Tab Direktori KOL di `/kol`. |
| **Sumber Informasi** | Biro Administrasi Pimpinan (Adpim) Setda Provinsi Banten |
| **Status** | Done |

### T-018 · F.13 KOL Campaign Tracker
| Field | Isi |
|---|---|
| **Judul Task** | F.13 — Tracker campaign & deliverable KOL |
| **Deskripsi** | Melacak eksekusi kerja sama KOL dari perencanaan sampai performa tayang. Meliputi: (1) campaign terikat ke KOL; (2) status campaign & status anggaran; (3) jadwal tayang, URL deliverable; (4) metrik views/likes/comments; (5) update berkala oleh admin media. **Selesai jika:** satu campaign punya jejak status, anggaran, dan performa dasar untuk laporan. |
| **Prioritas** | P2 |
| **Rentang Tanggal** | 1–8 September 2026 |
| **Komentar** | PRD: nice-to-have jika waktu mepet; sudah diimplementasi dasar. |
| **Sumber Informasi** | Biro Administrasi Pimpinan (Adpim) Setda Provinsi Banten |
| **Status** | Done |

### T-019 · F.14 Dashboard Eksekutif
| Field | Isi |
|---|---|
| **Judul Task** | F.14 — Dashboard eksekutif pimpinan |
| **Deskripsi** | Ringkasan eksekutif *view-oriented* untuk Khabiro/Sekda/Gubernur tanpa harus masuk detail operasional. Meliputi: (1) rekap isu/krisis aktif & kritis; (2) indikator distribusi rilis / aktivitas media; (3) statistik partisipasi ASN & KOL; (4) area untuk brief/sentimen dari Mata Bathin (saat ini boleh stub sampai integrasi live); (5) tautan cepat ke Crisis Room/laporan. **Selesai jika:** pimpinan mendapat satu layar ringkas yang bisa dipakai briefing harian. |
| **Prioritas** | P1 |
| **Rentang Tanggal** | 1–10 September 2026 |
| **Komentar** | Sentimen/brief live dari Mata Bathin masih stub. |
| **Sumber Informasi** | Biro Administrasi Pimpinan (Adpim) Setda Provinsi Banten |
| **Status** | Done (data MB live: Todo) |

---

## Epic E — Integrasi Mata Bathin & Feedback

### T-020 · Integrasi ingest Mata Bathin (API/Webhook)
| Field | Isi |
|---|---|
| **Judul Task** | Integrasi ingest alert & issue brief dari Mata Bathin |
| **Deskripsi** | Menghubungkan “otak” OSINT (Mata Bathin) ke SIAGAPIM agar isu masuk otomatis, bukan hanya input manual. Meliputi: (1) konsumsi alert krisis, issue brief, risk assessment, evidence pack, narrative card, recommendation; (2) endpoint webhook/REST + API key; (3) mapping ke model `Issue` / evidence / alert di SIAGAPIM; (4) SLA pengiriman alert ≤ 5 menit setelah MB generate; (5) retry (3x, exponential backoff) + circuit breaker agar kegagalan MB tidak menghentikan SIAGAPIM; (6) contract test format JSON Lampiran B. **Selesai jika:** alert MB uji coba muncul di Crisis Room dengan risk & brief terisi. |
| **Prioritas** | P0 |
| **Rentang Tanggal** | 8 Agustus – 12 September 2026 |
| **Komentar** | Skeleton API + flag `MATA_BATHIN_ENABLED` ada; perlu endpoint produksi & contract test. |
| **Sumber Informasi** | Biro Administrasi Pimpinan (Adpim) Setda Provinsi Banten |
| **Status** | In Progress |

### T-021 · Feedback loop ke Mata Bathin
| Field | Isi |
|---|---|
| **Judul Task** | Kirim feedback action/outcome ke Mata Bathin |
| **Deskripsi** | Mengembalikan hasil tindakan SIAGAPIM agar Mata Bathin bisa belajar efektivitas rekomendasi. Meliputi payload: action taken (OPD validated, konten dibuat, blast terkirim, misi ASN, KOL engaged), outcome (rata-rata waktu tayang media, catatan situasi). Pemicu: status isu `disseminated` / `closed`, dan setelah media blast terkait isu. **Selesai jika:** setiap penutupan/diseminasi isu menghasilkan panggilan feedback ke endpoint MB (atau log jelas jika MB off), sesuai skema Lampiran B.2. |
| **Prioritas** | P1 |
| **Rentang Tanggal** | 25 Agustus – 15 September 2026 |
| **Komentar** | Service `push_issue_feedback` sudah dipanggil; perlu verifikasi endpoint MB live. |
| **Sumber Informasi** | Biro Administrasi Pimpinan (Adpim) Setda Provinsi Banten |
| **Status** | In Progress |

---

## Epic F — Laporan, Operasional & NFR

### T-022 · Generate laporan PDF/Excel
| Field | Isi |
|---|---|
| **Judul Task** | Export laporan (krisis, SLA, ASN, KOL, executive) |
| **Deskripsi** | Menyediakan deliverable cetak/export untuk rapat pimpinan dan arsip. Jenis laporan: (1) penanganan krisis; (2) aktivitas/SLA media; (3) rekap partisipasi ASN per OPD; (4) kinerja KOL & campaign; (5) executive brief. Format PDF dan/atau Excel. UI di `/reports` dengan pilihan jenis + unduh. **Selesai jika:** tiap jenis laporan bisa di-generate tanpa error dan berisi data inti dari DB. |
| **Prioritas** | P1 |
| **Rentang Tanggal** | 1–12 September 2026 |
| **Komentar** | openpyxl + fpdf2 sudah terpasang. |
| **Sumber Informasi** | Biro Administrasi Pimpinan (Adpim) Setda Provinsi Banten |
| **Status** | Done |

### T-023 · Manajemen User UI
| Field | Isi |
|---|---|
| **Judul Task** | UI manajemen user (super admin) |
| **Deskripsi** | Mengelola akses pengguna tanpa sentuh database langsung. Meliputi: (1) daftar user + pagination; (2) tambah user (username, email, password, nama, role); (3) edit profil, ganti role, reset password opsional; (4) assign OPD untuk role yang membutuhkan; (5) aktifkan/nonaktifkan akun (kecuali akun sendiri). **Aktor:** super_admin saja. **Selesai jika:** lifecycle akun demo/operasional bisa dikelola dari UI `/users`. |
| **Prioritas** | P1 |
| **Rentang Tanggal** | 5–15 Agustus 2026 |
| **Komentar** | Halaman `/users` sudah ada. |
| **Sumber Informasi** | Biro Administrasi Pimpinan (Adpim) Setda Provinsi Banten |
| **Status** | Done |

### T-024 · Hardening NFR keamanan & keandalan
| Field | Isi |
|---|---|
| **Judul Task** | Hardening NFR (idle timeout, audit UI, backup, load test) |
| **Deskripsi** | Menutup celah non-fungsional agar aman dipakai operasional harian. Ruang lingkup: (1) session/idle timeout otomatis; (2) review sanitasi input & proteksi umum XSS/SQLi (sudah sebagian via stack); (3) enkripsi field sensitif bila diperlukan; (4) UI/audit trail untuk perubahan status isu & approval; (5) backup database terjadwal di env deploy; (6) load/smoke test target dashboard &lt; 3 detik dan API p95 &lt; 2 detik; (7) circuit breaker formal ke Mata Bathin. **Selesai jika:** checklist PRD §7 punya bukti implementasi atau mitigasi tertulis per item. |
| **Prioritas** | P1 |
| **Rentang Tanggal** | 8–20 September 2026 |
| **Komentar** | JWT/RBAC & brand UI OK; gap NFR masih terbuka (hasil audit sebelumnya). |
| **Sumber Informasi** | Biro Administrasi Pimpinan (Adpim) Setda Provinsi Banten |
| **Status** | Todo |

### T-025 · UAT, dokumentasi & demo PKA
| Field | Isi |
|---|---|
| **Judul Task** | UAT, panduan pengguna & persiapan demo |
| **Deskripsi** | Memastikan aplikasi siap diperlihatkan dan dipakai user nyata. Meliputi: (1) skenario UAT per role (admin, editor, OPD, pimpinan, ASN, media); (2) uji alur end-to-end: isu → validasi → konten → blast → ASN/KOL → laporan; (3) rapikan `USER_MANUAL.md` & `BUSINESS_PROCESS.md`; (4) data demo yang konsisten; (5) checklist demo seminar PKA (akun, URL env, fallback manual jika MB down). **Selesai jika:** ada berita acara/checklist UAT lulus dan skrip demo 15–20 menit siap dijalankan. |
| **Prioritas** | P0 |
| **Rentang Tanggal** | 12–26 September 2026 |
| **Komentar** | USER_MANUAL & BUSINESS_PROCESS sudah ada; perlu UAT formal di env dev. |
| **Sumber Informasi** | Biro Administrasi Pimpinan (Adpim) Setda Provinsi Banten |
| **Status** | In Progress |

### T-026 · Integrasi WhatsApp Gateway produksi
| Field | Isi |
|---|---|
| **Judul Task** | Integrasi WhatsApp Gateway untuk alert & media blast |
| **Deskripsi** | Mengganti pengiriman mock dengan gateway WhatsApp (dan email SMTP) milik instansi agar blast/alert benar-benar sampai ke HP/redaksi. Meliputi: (1) konfigurasi kredensial gateway di env; (2) adaptasi `messaging` service; (3) mapping status delivery riil ke log blast/alert; (4) penanganan gagal kirim + retry; (5) uji ke nomor/media uji coba. **Dependency:** ketersediaan WA Gateway Adpim/Diskominfo. **Selesai jika:** satu blast uji menghasilkan status terkirim dari provider, bukan mock lokal. |
| **Prioritas** | P2 |
| **Rentang Tanggal** | 15–26 September 2026 |
| **Komentar** | Bergantung ketersediaan gateway instansi. |
| **Sumber Informasi** | Biro Administrasi Pimpinan (Adpim) Setda Provinsi Banten |
| **Status** | Todo |

---

## Ringkasan timeline (mulai 1 Agustus 2026)

| Periode | Fokus |
|---|---|
| **1–7 Agu** | Fondasi, Docker/Postgres, rebrand, pagination |
| **8–21 Agu** | Crisis Room F.01–F.05, Master OPD, start integrasi MB |
| **22 Agu – 5 Sep** | Media Hub F.06–F.09, ASN/KOL F.10–F.13 |
| **1–12 Sep** | Dashboard eksekutif F.14, laporan, feedback MB |
| **8–26 Sep** | NFR hardening, WA gateway, UAT & demo |

---

## Cara pakai

1. Salin tiap task (T-001 dst.) ke board Jira/Trello/Notion.  
2. Sesuaikan assignee & status aktual di env.  
3. Task bertanda **Todo / In Progress** = backlog kerja lanjutan prioritas.

*Dokumen ini dihasilkan dari PRD SIAGAPIM/SULTAN BANTEN dan kondisi implementasi repo per Agustus 2026.*
