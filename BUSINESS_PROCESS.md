# Business Process — SULTAN BANTEN

Alur proses sesuai [SultanBanten-PRD.md](./SultanBanten-PRD.md) dan implementasi aplikasi saat ini (status isu, konten, validasi, blast, ASN, KOL).

---

## 1. Peta konteks (Mata Bathin ↔ SULTAN BANTEN)

```mermaid
flowchart LR
  subgraph OSINT["Mata Bathin — Intel Engine"]
    SRC[Internet / Media Sosial]
    PIPE[Ingestion → AI Agents → Risk Scoring]
    OUT[Alert · Issue Brief · Evidence · Narrative Card]
    SRC --> PIPE --> OUT
  end

  subgraph SB["SULTAN BANTEN — Action Platform"]
    CR[Crisis Room]
    ACT[Validasi → Konten → Diseminasi → Amplifikasi]
    MON[SLA · Laporan · Dashboard Eksekutif]
    CR --> ACT --> MON
  end

  OUT -->|REST / Webhook| CR
  MON -->|Feedback loop| OSINT
```

| Sisi | Peran |
|---|---|
| **Mata Bathin** | Deteksi, skor risiko R0–R5, brief, rekomendasi |
| **SULTAN BANTEN** | Eksekusi respons: OPD, konten, media, ASN, KOL, arsip, laporan |

---

## 2. SOP end-to-end — Kontra-isu (alur utama)

Alur ini memetakan **§8 Mapping SOP** di PRD ke modul yang ada di aplikasi.

```mermaid
flowchart TD
  A([Mata Bathin deteksi isu]) -->|API / Webhook / input manual| B

  B[F.01 Crisis Room<br/>Isu status: open]
  B --> C{Risk R3+ atau<br/>SLA respons lewat?}
  C -->|Ya| D[F.02 Alert Krisis<br/>Web notification]
  C -->|Tidak| E
  D --> E

  E[F.03 Minta validasi OPD<br/>Isu → validating]
  E --> F{OPD merespon?}
  F -->|Validated| G[Isu → producing]
  F -->|Rejected| H[Kembali tinjau / open]
  H --> E

  G --> I[F.04 Hub Konten<br/>draft → in_review]
  I --> J{Pimpinan / Super Admin<br/>approve?}
  J -->|Rejected| I
  J -->|Approved| K[Konten approved<br/>Isu → approved]

  K --> L[F.08 Media Blast<br/>WA + Email mitra]
  L --> M[Isu → disseminated<br/>Konten → published]

  M --> N[F.10 Mission Board ASN]
  M --> O[F.13 Campaign KOL]
  M --> P[F.07 Catat SLA media]

  N --> Q[F.11 Log partisipasi ASN]
  O --> R[Track deliverable & performa]
  P --> S[Peringkat compliance]

  Q --> T[F.14 Dashboard Eksekutif]
  R --> T
  S --> T
  T --> U[F.05 Arsip + F Reports PDF/Excel]
  U --> V([Feedback ke Mata Bathin])
  M --> V

  style B fill:#1B3A5C,color:#fff
  style K fill:#D4A017,color:#1B3A5C
  style M fill:#C0392B,color:#fff
  style V fill:#1B3A5C,color:#fff
```

### Aktor per tahap

| Tahap | Role utama | Modul |
|---|---|---|
| Terima isu & alert | Super Admin, Editor, Pimpinan | `/crisis-room`, Alert Bell |
| Validasi OPD | Editor minta · OPD Admin jawab | `/validasi-opd`, detail isu |
| Produksi konten | Editor | `/konten` |
| Approval | Pimpinan, Super Admin | Detail konten |
| Media blast & SLA | Editor, Media/KOL Admin | `/media-hub` |
| Amplifikasi ASN | Editor buat misi · ASN ikut | `/missions` |
| KOL | Media/KOL Admin | `/kol` |
| Monitoring | Pimpinan | `/executive`, `/reports`, `/arsip` |

---

## 3. Lifecycle status isu (sesuai model `Issue`)

```mermaid
stateDiagram-v2
  [*] --> open: Alert Mata Bathin / input manual

  open --> validating: Request validasi OPD
  validating --> producing: Minimal 1 OPD validated
  validating --> open: Semua ditolak / reset

  open --> producing: Langsung buat konten
  producing --> producing: Edit / review konten
  producing --> approved: Konten di-approve

  approved --> disseminated: Media blast sukses
  producing --> disseminated: Blast saat isu masih producing

  disseminated --> closed: Tutup isu
  approved --> closed: Tutup isu
  open --> closed: Tutup tanpa diseminasi
  validating --> closed: Tutup isu

  closed --> [*]

  note right of disseminated
    Trigger feedback ke Mata Bathin
    (juga saat closed)
  end note
```

**Urutan ideal (SOP):**  
`open → validating → producing → approved → disseminated → closed`

---

## 4. Lifecycle konten klarifikasi (F.04)

```mermaid
stateDiagram-v2
  [*] --> draft: Editor buat konten

  draft --> in_review: Ajukan review
  rejected --> draft: Edit ulang
  rejected --> in_review: Ajukan lagi setelah edit

  in_review --> approved: Pimpinan / Super Admin approve
  in_review --> rejected: Reject + catatan

  approved --> published: Setelah media blast
  published --> [*]
```

```mermaid
flowchart LR
  subgraph Editor
    A[Buat draft] --> B[Submit review]
  end
  subgraph Approver["Pimpinan / Super Admin"]
    B --> C{Decision}
    C -->|approved| D[Siap blast]
    C -->|rejected| A
  end
  subgraph MediaHub["Media Hub"]
    D --> E[One-Click Blast]
    E --> F[published]
  end
```

---

## 5. Validasi OPD (F.03) — detail

```mermaid
flowchart TD
  A[Editor / Super Admin<br/>pilih OPD dari Master OPD] --> B[Status validasi: waiting]
  B --> C[Isu: open → validating]
  C --> D[OPD Admin lihat di Validasi OPD]
  D --> E{Respon}
  E -->|validated + data pendukung| F[Isu → producing<br/>jika belum producing]
  E -->|rejected + alasan| G[Tetap tinjau isu]
  F --> H[Editor lanjut Hub Konten]
  G --> A
```

Evidence pack dari Mata Bathin dilampirkan di detail isu / permintaan validasi.

---

## 6. Diseminasi & amplifikasi paralel (setelah konten approved)

```mermaid
flowchart TB
  A([Konten approved]) --> B[F.08 Media Blast]

  B --> C[Kirim ke media mitra aktif<br/>channel: WA / Email / both]
  C --> D{Hasil pengiriman}
  D -->|sent / partial / failed| E[Log blast]
  E --> F[Isu → disseminated]
  E --> G[F.07 Catat SLA tayang]

  A --> H[F.10 Buat misi ASN]
  H --> I[ASN Like / Share / Comment]
  I --> J[F.11 Log per OPD]

  A --> K[F.13 Campaign KOL]
  K --> L[Publish deliverable]
  L --> M[Update views / likes / budget]

  G --> N[Dashboard & Reports]
  J --> N
  M --> N
```

Ketiga jalur (media, ASN, KOL) **bisa jalan paralel** setelah klarifikasi siap — sesuai pilar PRD 2 & 3.

---

## 7. Jalur proaktif — Agenda Setting (F.09)

Bukan reaksi krisis, melainkan strategi *flooding the market* (konten positif rutin).

```mermaid
flowchart LR
  A[Rencana bulanan] --> B[Agenda: planned]
  B --> C[in_production]
  C --> D[ready]
  D --> E[published ke media / sosmed]
  E --> F[Arsip & laporan branding]
  B --> X[cancelled]
```

Dapat berjalan **independen** dari alur kontra-isu (circuit breaker PRD: sistem tetap berguna meski Mata Bathin down).

---

## 8. Feedback loop ke Mata Bathin

```mermaid
sequenceDiagram
  participant MB as Mata Bathin
  participant SB as SULTAN BANTEN
  participant OPD as OPD Teknis
  participant MED as Media Mitra

  MB->>SB: Alert + Issue Brief + Evidence
  SB->>SB: Crisis Room (open) + Alert R3+
  SB->>OPD: Request validasi
  OPD-->>SB: validated / rejected
  SB->>SB: Produksi & approval konten
  SB->>MED: Media blast
  MED-->>SB: Tayang (SLA log)
  Note over SB: Status isu disseminated / closed
  SB->>MB: Feedback (action_taken, OPD result, media response, outcome)
```

Dipicu otomatis saat isu berstatus **`disseminated`** atau **`closed`**, dan setelah blast terkait isu.

---

## 9. Ringkasan tiga pilar → modul aplikasi

```mermaid
mindmap
  root((SULTAN BANTEN))
    Pilar1 Crisis Room
      F01 Crisis Room
      F02 Alert
      F03 Validasi OPD
      F04 Hub Konten
      F05 Arsip
    Pilar2 Media Hub
      F06 Mitra Media
      F07 SLA Tracker
      F08 Media Blast
      F09 Agenda Setting
    Pilar3 Cyber Troops KOL
      F10 Mission Board
      F11 Log ASN
      F12 Direktori KOL
      F13 Campaign KOL
      F14 Dashboard Eksekutif
    Supporting
      Users RBAC
      Master OPD
      Reports PDF Excel
```

---

## 10. Checklist operasional cepat

1. **Deteksi** — isu masuk Crisis Room (`open`); cek Alert Bell jika R3+.
2. **Validasi** — minta OPD; tunggu `validated` → isu `producing`.
3. **Klarifikasi** — buat konten → `in_review` → approve pimpinan.
4. **Blast** — kirim ke mitra → isu `disseminated`.
5. **Amplifikasi** — misi ASN + campaign KOL (opsional paralel).
6. **Monitor** — SLA media, rekap ASN, dashboard pimpinan, export laporan.
7. **Tutup** — isu `closed` + pastikan feedback ke Mata Bathin terkirim.
8. **Proaktif** — isi Agenda Setting untuk konten positif terjadwal.

---

*Dokumen ini mengikuti status & API yang diimplementasikan di project. Jika status model berubah, sesuaikan diagram §3–§5.*
