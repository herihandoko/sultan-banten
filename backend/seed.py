"""Seed roles, demo users, and rich dummy data for local development."""

from datetime import date, datetime, timedelta, timezone

from app.extensions import db
from app import models  # noqa: F401 — register all models
from app.models import (
    ContentApproval,
    ContentItem,
    CrisisAlert,
    EditorialAgenda,
    Issue,
    IssueEvidence,
    KolCampaign,
    KolPartner,
    MediaBlastLog,
    MediaPartner,
    MediaSlaLog,
    Mission,
    MissionParticipation,
    Opd,
    OpdValidation,
    Role,
    User,
)
from app.utils.auth import ROLE_CODES

# From ct_opd.sql (nm_opd + source id)
CT_OPD_ROWS = [
    (1, "Dinas Pendidikan dan Kebudayaan"),
    (9, "Dinas Kesehatan"),
    (16, "Dinas Pekerjaan Umum dan Penataan Ruang"),
    (25, "Dinas Perumahan Rakyat dan Kawasan Permukiman"),
    (26, "Satuan Polisi Pamong Praja"),
    (27, "Badan Penanggulangan Bencana Daerah"),
    (28, "Dinas Sosial"),
    (31, "Dinas Tenaga Kerja dan Transmigrasi"),
    (37, "Dinas Pemberdayaan Perempuan, Perlindungan Anak, Kependudukan dan Keluarga Berencana"),
    (38, "Dinas Ketahanan Pangan"),
    (40, "Dinas Lingkungan Hidup dan Kehutanan"),
    (46, "Dinas Pemberdayaan Masyarakat dan Desa"),
    (47, "Dinas Perhubungan"),
    (49, "Dinas Komunikasi, Informatika, Statistik dan Persandian"),
    (50, "Dinas Koperasi, Usaha Kecil dan Menengah"),
    (51, "Dinas Penanaman Modal dan Pelayanan Terpadu Satu Pintu"),
    (52, "Dinas Kepemudaan dan Olahraga"),
    (54, "Dinas Perpustakaan dan Kearsipan"),
    (55, "Dinas Kelautan dan Perikanan"),
    (61, "Dinas Pariwisata"),
    (62, "Dinas Pertanian"),
    (67, "Dinas Energi dan Sumber Daya Mineral"),
    (68, "Dinas Perindustrian dan Perdagangan"),
    (71, "Biro Hukum Sekretariat Daerah"),
    (79, "Sekretariat DPRD"),
    (80, "Badan Perencanaan Pembangunan Daerah"),
    (81, "Badan Pengelolaan Keuangan dan Aset Daerah"),
    (82, "Badan Pendapatan Daerah"),
    (95, "Badan Kepegawaian Daerah"),
    (96, "Badan Pengembangan Sumber Daya Manusia Daerah"),
    (97, "Badan Penghubung Daerah"),
    (98, "Inspektorat"),
    (99, "Badan Kesatuan Bangsa dan Politik"),
    (103, "Biro Pengadaan Barang/ Jasa dan LPSE Sekretariat Daerah"),
    (104, "Biro Administrasi Pimpinan dan Protokol Sekretariat Daerah"),
    (105, "Biro Organisasi dan Reformasi Sekretariat Daerah"),
    (106, "Biro Umum dan Perlengkapan Sekretariat Daerah"),
    (109, "Biro Pemerintahan dan Otonomi Daerah Sekretariat Daerah"),
    (110, "Biro Perekonomian dan Administrasi Pembangunan Sekretariat Daerah"),
    (115, "PPID Utama"),
    (116, "Biro Hukum"),
]


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _user(username: str) -> User | None:
    return User.query.filter_by(username=username).first()


def _opd_by_name(name: str) -> Opd | None:
    return Opd.query.filter_by(name=name).first()


def ensure_schema() -> None:
    """Add missing columns on existing SQLite DBs (create_all won't alter)."""
    from sqlalchemy import inspect, text

    insp = inspect(db.engine)
    if "users" in insp.get_table_names():
        cols = {c["name"] for c in insp.get_columns("users")}
        with db.engine.begin() as conn:
            if "opd_id" not in cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN opd_id INTEGER"))


def seed_roles() -> None:
    for code, name in ROLE_CODES.items():
        if not Role.query.filter_by(code=code).first():
            db.session.add(Role(code=code, name=name, description=name))
    db.session.commit()


def seed_opds() -> None:
    for source_id, name in CT_OPD_ROWS:
        existing = Opd.query.filter(
            (Opd.source_id == source_id) | (Opd.name == name)
        ).first()
        if existing:
            if existing.source_id is None:
                existing.source_id = source_id
            if existing.name != name:
                existing.name = name
            continue
        db.session.add(Opd(source_id=source_id, name=name, is_active=True))
    db.session.commit()


def seed_users() -> None:
    pupr = "Dinas Pekerjaan Umum dan Penataan Ruang"
    kes = "Dinas Kesehatan"
    kominfo = "Dinas Komunikasi, Informatika, Statistik dan Persandian"
    demo_users = [
        {
            "username": "admin",
            "email": "admin@sultanbanten.local",
            "password": "admin123",
            "full_name": "Super Admin Adpim",
            "role_code": "super_admin",
        },
        {
            "username": "editor",
            "email": "editor@sultanbanten.local",
            "password": "editor123",
            "full_name": "Tim Editor Kreatif",
            "role_code": "editor",
        },
        {
            "username": "pimpinan",
            "email": "pimpinan@sultanbanten.local",
            "password": "pimpinan123",
            "full_name": "Pimpinan Daerah",
            "role_code": "pimpinan",
        },
        {
            "username": "asn",
            "email": "asn@sultanbanten.local",
            "password": "asn123",
            "full_name": "ASN Siber Banten",
            "role_code": "asn",
            "opd_name": kominfo,
        },
        {
            "username": "asn2",
            "email": "asn2@sultanbanten.local",
            "password": "asn123",
            "full_name": "Rina ASN Serang",
            "role_code": "asn",
            "opd_name": kes,
        },
        {
            "username": "asn3",
            "email": "asn3@sultanbanten.local",
            "password": "asn123",
            "full_name": "Dedi ASN Cilegon",
            "role_code": "asn",
            "opd_name": pupr,
        },
        {
            "username": "opd",
            "email": "opd@sultanbanten.local",
            "password": "opd123",
            "full_name": "Admin OPD Dinas PUPR",
            "role_code": "opd_admin",
            "opd_name": pupr,
        },
        {
            "username": "opd_kes",
            "email": "opd.kes@sultanbanten.local",
            "password": "opd123",
            "full_name": "Admin OPD Dinas Kesehatan",
            "role_code": "opd_admin",
            "opd_name": kes,
        },
        {
            "username": "media",
            "email": "media@sultanbanten.local",
            "password": "media123",
            "full_name": "Admin Media & KOL",
            "role_code": "media_kol_admin",
        },
    ]

    for item in demo_users:
        opd = _opd_by_name(item["opd_name"]) if item.get("opd_name") else None
        existing = User.query.filter_by(username=item["username"]).first()
        if existing:
            # Sync OPD link for demo accounts
            if opd and (existing.opd_id != opd.id or existing.opd_name != opd.name):
                existing.opd_id = opd.id
                existing.opd_name = opd.name
            continue
        role = Role.query.filter_by(code=item["role_code"]).first()
        user = User(
            username=item["username"],
            email=item["email"],
            full_name=item["full_name"],
            role_id=role.id,
            opd_id=opd.id if opd else None,
            opd_name=opd.name if opd else None,
        )
        user.set_password(item["password"])
        db.session.add(user)
    db.session.commit()


def seed_media_partners() -> None:
    demos = [
        {
            "name": "Radar Banten",
            "editor_name": "Budi Santoso",
            "whatsapp": "6281211000001",
            "email": "redaksi@radarbanten.demo",
            "coverage_area": "Provinsi Banten",
            "crisis_channel": "WA Desk Krisis",
        },
        {
            "name": "BantenNews",
            "editor_name": "Siti Aminah",
            "whatsapp": "6281211000002",
            "email": "news@bantennews.demo",
            "coverage_area": "Serang–Cilegon",
            "crisis_channel": "Email + WA",
        },
        {
            "name": "Tangerang Ekspres",
            "editor_name": "Andi Wijaya",
            "whatsapp": "6281211000003",
            "email": "desk@tangerangekspres.demo",
            "coverage_area": "Tangerang Raya",
            "crisis_channel": "WA Pemred",
        },
        {
            "name": "Kabarbanten.id",
            "editor_name": "Rina Kartika",
            "whatsapp": "6281211000004",
            "email": "editor@kabarbanten.demo",
            "coverage_area": "Online / Provinsi",
            "crisis_channel": "WA Hotline",
        },
        {
            "name": "Serang Pos",
            "editor_name": "Hendra Gunawan",
            "whatsapp": "6281211000005",
            "email": "redaksi@serangpos.demo",
            "coverage_area": "Kota Serang",
            "crisis_channel": "WA Redaksi",
        },
        {
            "name": "Cilegon News",
            "editor_name": "Maya Putri",
            "whatsapp": "6281211000006",
            "email": "info@cilegonnews.demo",
            "coverage_area": "Cilegon",
            "crisis_channel": "Email",
        },
        {
            "name": "Banten TV Online",
            "editor_name": "Fajar Nugraha",
            "whatsapp": "6281211000007",
            "email": "newsroom@bantentv.demo",
            "coverage_area": "Provinsi / Broadcast",
            "crisis_channel": "WA Produser",
        },
    ]
    for item in demos:
        if MediaPartner.query.filter_by(name=item["name"]).first():
            continue
        db.session.add(MediaPartner(**item, is_active=True))
    db.session.commit()


def seed_kol_partners() -> None:
    demos = [
        {
            "name": "Raka Banten",
            "platform": "instagram",
            "handle": "@rakabanten",
            "followers": 125000,
            "engagement_rate": 3.2,
            "topics": "wisata, kuliner, budaya",
            "contract_status": "active",
        },
        {
            "name": "Salsa Serang",
            "platform": "tiktok",
            "handle": "@salsaserang",
            "followers": 340000,
            "engagement_rate": 5.1,
            "topics": "lifestyle, isu lokal",
            "contract_status": "active",
        },
        {
            "name": "Banten Insight",
            "platform": "youtube",
            "handle": "BantenInsight",
            "followers": 88000,
            "engagement_rate": 4.0,
            "topics": "opini, pemerintahan",
            "contract_status": "prospect",
        },
        {
            "name": "Naufal Cilegon",
            "platform": "instagram",
            "handle": "@naufalcilegon",
            "followers": 76000,
            "engagement_rate": 2.8,
            "topics": "industri, pekerjaan, muda",
            "contract_status": "active",
        },
        {
            "name": "Voice of Pandeglang",
            "platform": "twitter",
            "handle": "@voicpandeglang",
            "followers": 42000,
            "engagement_rate": 3.6,
            "topics": "infastruktur, desa, wisata",
            "contract_status": "active",
        },
        {
            "name": "Ustadz Lokal Banten",
            "platform": "youtube",
            "handle": "UstadzLokalBanten",
            "followers": 210000,
            "engagement_rate": 4.5,
            "topics": "dakwah, sosial, moderasi",
            "contract_status": "prospect",
        },
    ]
    for item in demos:
        if KolPartner.query.filter_by(name=item["name"]).first():
            continue
        db.session.add(KolPartner(**item, is_active=True))
    db.session.commit()


def seed_agenda() -> None:
    month_start = date.today().replace(day=1)
    demos = [
        {
            "title": "Highlight Jalan Tol Serang–Panimbang tahap 2",
            "description": "Sudut liputan: progres fisik, manfaat mobilitas warga, dan target selesai.",
            "theme": "pembangunan",
            "planned_date": month_start + timedelta(days=2),
            "channel": "both",
            "status": "in_production",
            "target_media": "Radar Banten, BantenNews",
        },
        {
            "title": "Penghargaan Inovasi Pelayanan Publik Pemprov",
            "description": "Narasi prestasi Gubernur & OPD terkait penghargaan nasional.",
            "theme": "penghargaan",
            "planned_date": month_start + timedelta(days=8),
            "channel": "media",
            "status": "planned",
            "target_media": "Kabarbanten",
        },
        {
            "title": "Program bantuan sosial Ramadan / Idul Fitri",
            "description": "Konten empati & transparansi penyaluran bansos di wilayah prioritas.",
            "theme": "sosial",
            "planned_date": month_start + timedelta(days=15),
            "channel": "sosial",
            "status": "ready",
            "target_media": "IG/TikTok Adpim",
        },
        {
            "title": "Investasi kawasan industri Cilegon–Serang",
            "description": "Flooding the market: capaian investasi & lapangan kerja.",
            "theme": "ekonomi",
            "planned_date": month_start + timedelta(days=22),
            "channel": "media",
            "status": "planned",
            "target_media": "Radar Banten, Banten Insight",
        },
        {
            "title": "Festival Budaya Anyer & pantai barat",
            "description": "Highlight pariwisata & UMKM lokal.",
            "theme": "sosial",
            "planned_date": month_start + timedelta(days=18),
            "channel": "both",
            "status": "planned",
            "target_media": "Banten TV, Salsa Serang",
        },
        {
            "title": "Capaian vaksinasi & posyandu digital",
            "description": "Narasi kesehatan masyarakat & layanan Dinkes.",
            "theme": "sosial",
            "planned_date": month_start + timedelta(days=11),
            "channel": "media",
            "status": "in_production",
            "target_media": "Serang Pos, Kabarbanten.id",
        },
        {
            "title": "Soft opening pelabuhan & logistik baru",
            "description": "Dampak ekonomi regional & konektivitas.",
            "theme": "ekonomi",
            "planned_date": month_start + timedelta(days=25),
            "channel": "media",
            "status": "planned",
            "target_media": "Cilegon News, Radar Banten",
        },
    ]
    for item in demos:
        if EditorialAgenda.query.filter_by(title=item["title"]).first():
            continue
        db.session.add(EditorialAgenda(**item))
    db.session.commit()


def seed_issues_and_pipeline() -> None:
    """Issues + evidence + validations + content + alerts (idempotent via mb_alert_id)."""
    if Issue.query.filter_by(mb_alert_id="SEED-DEMO-001").first():
        return

    editor = _user("editor")
    admin = _user("admin")
    pimpinan = _user("pimpinan")
    opd = _user("opd")
    opd_kes = _user("opd_kes")
    now = _utcnow()

    demos = [
        {
            "mb_alert_id": "SEED-DEMO-001",
            "title": "Hoaks jembatan Anyer ambruk total",
            "summary": "Beredar klaim visual jembatan Anyer ambruk; faktanya perbaikan rutin tanpa putus akses utama.",
            "why_now": "Volume mention naik tajam di X dan grup WA lokal dalam 2 jam.",
            "risk_level": "R4",
            "status": "disseminated",
            "source": "mata_bathin",
            "hours_ago": 5,
            "risk_assessment": {
                "level": "High",
                "velocity": 0.9,
                "sentiment_negative_ratio": 0.78,
                "confidence": 0.82,
            },
            "recommended_actions": ["verify_with_opd", "prepare_clarification", "media_blast"],
            "narrative_card": {
                "statement": "Banten Meluruskan Fakta: Perbaikan jembatan Anyer bersifat rutin dan terkendali.",
                "key_points": [
                    "Tidak ada keruntuhan total",
                    "Akses alternatif disiapkan Dinas PUPR",
                    "Jadwal selesai diumumkan resmi",
                ],
            },
            "evidence": [
                {
                    "title": "Post viral X",
                    "url": "https://x.com/demo/status/jembatan-anyer",
                    "source_name": "X/Twitter",
                    "evidence_type": "social",
                    "snippet": "Jembatan Anyer ambruk! Warga panik...",
                },
                {
                    "title": "Artikel portal lokal",
                    "url": "https://news.demo/jembatan-anyer",
                    "source_name": "Portal lokal",
                    "evidence_type": "article",
                    "snippet": "Warga mengeluhkan kemacetan akibat perbaikan...",
                },
            ],
        },
        {
            "mb_alert_id": "SEED-DEMO-002",
            "title": "Keluhan antrian RSUD Banten viral",
            "summary": "Keluhan layanan IGD dan antrian poliklinik tersebar di TikTok.",
            "why_now": "Video keluhan mendapat 50rb+ view dalam semalam.",
            "risk_level": "R3",
            "status": "producing",
            "source": "mata_bathin",
            "hours_ago": 18,
            "risk_assessment": {
                "level": "Elevated",
                "velocity": 0.7,
                "sentiment_negative_ratio": 0.65,
                "confidence": 0.74,
            },
            "recommended_actions": ["verify_with_opd", "prepare_clarification"],
            "narrative_card": {
                "statement": "Pemprov terus tingkatkan kapasitas layanan RSUD.",
                "key_points": ["Penambahan slot", "Hotline pengaduan", "Evaluasi shift"],
            },
            "evidence": [
                {
                    "title": "Video TikTok keluhan",
                    "url": "https://tiktok.com/@demo/rsud",
                    "source_name": "TikTok",
                    "evidence_type": "video",
                    "snippet": "Antri dari pagi belum dipanggil...",
                }
            ],
        },
        {
            "mb_alert_id": "SEED-DEMO-003",
            "title": "Isu bansos tidak tepat sasaran di Pandeglang",
            "summary": "Narasi penyaluran bansos tidak merata; perlu klarifikasi data dinas sosial.",
            "why_now": "Diskusi di grup warga dan portal berita lokal meningkat.",
            "risk_level": "R3",
            "status": "validating",
            "source": "mata_bathin",
            "hours_ago": 8,
            "risk_assessment": {
                "level": "Elevated",
                "velocity": 0.55,
                "sentiment_negative_ratio": 0.6,
                "confidence": 0.7,
            },
            "recommended_actions": ["verify_with_opd"],
            "narrative_card": {
                "statement": "Penyaluran bansos mengikuti data DTKS terverifikasi.",
                "key_points": ["Mekanisme pengaduan", "Jadwal penyaluran"],
            },
            "evidence": [
                {
                    "title": "Thread warga",
                    "url": "https://x.com/demo/bansos",
                    "source_name": "X/Twitter",
                    "evidence_type": "social",
                    "snippet": "RT: Bansos di desa kami tidak merata...",
                }
            ],
        },
        {
            "mb_alert_id": "SEED-DEMO-004",
            "title": "Klaim proyek tol macet dana",
            "summary": "Spekulasi keterlambatan proyek akibat dana; butuh update progres resmi.",
            "why_now": "Opini di YouTube lokal dengan framing negatif anggaran.",
            "risk_level": "R2",
            "status": "open",
            "source": "mata_bathin",
            "hours_ago": 30,
            "risk_assessment": {
                "level": "Watch",
                "velocity": 0.4,
                "sentiment_negative_ratio": 0.48,
                "confidence": 0.66,
            },
            "recommended_actions": ["observe", "prepare_clarification"],
            "narrative_card": None,
            "evidence": [
                {
                    "title": "Video opini YouTube",
                    "url": "https://youtube.com/watch?v=demo-tol",
                    "source_name": "YouTube",
                    "evidence_type": "video",
                    "snippet": "Proyek tol diklaim macet dana...",
                }
            ],
        },
        {
            "mb_alert_id": "SEED-DEMO-005",
            "title": "Berita palsu libur ASN massal",
            "summary": "Hoaks circular libur ASN 1 minggu disebar di WhatsApp.",
            "why_now": "Forward massal di grup ASN & warga.",
            "risk_level": "R2",
            "status": "closed",
            "source": "manual",
            "hours_ago": 72,
            "risk_assessment": {
                "level": "Watch",
                "velocity": 0.35,
                "sentiment_negative_ratio": 0.3,
                "confidence": 0.9,
            },
            "recommended_actions": ["prepare_clarification", "asn_amplify"],
            "narrative_card": {
                "statement": "Tidak ada kebijakan libur ASN massal. Cek hanya kanal resmi.",
                "key_points": ["Abaikan pesan berantai", "Cek IG/website resmi"],
            },
            "evidence": [
                {
                    "title": "Screenshot WA",
                    "url": "https://example.com/evidence/hoaks-libur.png",
                    "source_name": "WhatsApp",
                    "evidence_type": "other",
                    "snippet": "SE Libur ASN 7 hari — palsu",
                }
            ],
        },
        {
            "mb_alert_id": "SEED-DEMO-006",
            "title": "Isu pencemaran udara kawasan industri",
            "summary": "Keluhan bau & asap di sekitar kawasan industri Cilegon.",
            "why_now": "Keluhan warga meningkat usai video drone viral.",
            "risk_level": "R4",
            "status": "approved",
            "source": "mata_bathin",
            "hours_ago": 12,
            "risk_assessment": {
                "level": "High",
                "velocity": 0.8,
                "sentiment_negative_ratio": 0.71,
                "confidence": 0.77,
            },
            "recommended_actions": ["verify_with_opd", "prepare_clarification", "media_blast"],
            "narrative_card": {
                "statement": "Pemprov dan dinas terkait memantau baku mutu udara secara berkala.",
                "key_points": ["Hasil pengukuran", "Langkah pengawasan industri"],
            },
            "evidence": [
                {
                    "title": "Video drone",
                    "url": "https://tiktok.com/@demo/asap",
                    "source_name": "TikTok",
                    "evidence_type": "video",
                    "snippet": "Asap pekat di kawasan industri...",
                }
            ],
        },
        {
            "mb_alert_id": "SEED-DEMO-007",
            "title": "Narasi negatif wisata Anyer sepi",
            "summary": "Klaim wisata Anyer sepi total berdampak pada persepsi UMKM.",
            "why_now": "Konten influencer lokal membandingkan dengan destinasi lain.",
            "risk_level": "R1",
            "status": "open",
            "source": "manual",
            "hours_ago": 40,
            "risk_assessment": {
                "level": "Observe",
                "velocity": 0.25,
                "sentiment_negative_ratio": 0.4,
                "confidence": 0.6,
            },
            "recommended_actions": ["agenda_setting", "kol_engage"],
            "narrative_card": None,
            "evidence": [],
        },
    ]

    created_issues: dict[str, Issue] = {}
    for item in demos:
        hours = item.pop("hours_ago")
        evidence_list = item.pop("evidence")
        created = now - timedelta(hours=hours)
        issue = Issue(
            **item,
            created_by=editor.id if editor else None,
            created_at=created,
            updated_at=created,
            closed_at=created + timedelta(hours=20) if item["status"] == "closed" else None,
        )
        db.session.add(issue)
        db.session.flush()
        for ev in evidence_list:
            db.session.add(
                IssueEvidence(
                    issue_id=issue.id,
                    captured_at=created,
                    **ev,
                )
            )
        created_issues[item["mb_alert_id"]] = issue

    db.session.flush()

    # Validations
    i1 = created_issues["SEED-DEMO-001"]
    i2 = created_issues["SEED-DEMO-002"]
    i3 = created_issues["SEED-DEMO-003"]
    i6 = created_issues["SEED-DEMO-006"]

    validations = [
        OpdValidation(
            issue_id=i1.id,
            opd_name="Dinas Pekerjaan Umum dan Penataan Ruang",
            requested_by=editor.id if editor else None,
            assigned_to=opd.id if opd else None,
            status="validated",
            request_notes="Mohon konfirmasi status jembatan Anyer & jadwal perbaikan.",
            response_notes="Perbaikan rutinitas deck; akses utama tetap dibuka bergiliran. Target selesai H+5.",
            response_data={"condition": "maintenance", "access": "partial_lane"},
            requested_at=now - timedelta(hours=4),
            responded_at=now - timedelta(hours=3),
        ),
        OpdValidation(
            issue_id=i2.id,
            opd_name="Dinas Kesehatan",
            requested_by=editor.id if editor else None,
            assigned_to=opd_kes.id if opd_kes else None,
            status="validated",
            request_notes="Mohon data antrian RSUD & langkah perbaikan layanan.",
            response_notes="Antrian puncak pagi; ditambah loket & sistem antrean digital minggu ini.",
            requested_at=now - timedelta(hours=16),
            responded_at=now - timedelta(hours=10),
        ),
        OpdValidation(
            issue_id=i3.id,
            opd_name="Dinas Sosial",
            requested_by=admin.id if admin else None,
            status="waiting",
            request_notes="Mohon data DTKS & rekap penyaluran bansos Pandeglang.",
            requested_at=now - timedelta(hours=7),
        ),
        OpdValidation(
            issue_id=i6.id,
            opd_name="Dinas Lingkungan Hidup dan Kehutanan",
            requested_by=editor.id if editor else None,
            status="validated",
            request_notes="Hasil pengukuran kualitas udara 48 jam terakhir.",
            response_notes="Hasil dalam ambang batas pada 3 titik; 1 titik waspada — inspeksi industri dijadwalkan.",
            requested_at=now - timedelta(hours=11),
            responded_at=now - timedelta(hours=6),
        ),
    ]
    for v in validations:
        db.session.add(v)

    # Content
    contents = [
        ContentItem(
            issue_id=i1.id,
            title="Klarifikasi: Perbaikan Jembatan Anyer Terkendali",
            content_type="text_release",
            body=(
                "BANTEN MELURUSKAN FAKTA\n\n"
                "Beredar informasi jembatan Anyer ambruk total. Berdasarkan konfirmasi Dinas PUPR, "
                "yang berlangsung adalah perbaikan rutin. Akses tetap tersedia bergiliran.\n\n"
                "Masyarakat diminta merujuk informasi resmi Pemprov Banten."
            ),
            status="published",
            created_by=editor.id if editor else None,
            created_at=now - timedelta(hours=3),
        ),
        ContentItem(
            issue_id=i1.id,
            title="Infografis: Fakta Perbaikan Jembatan Anyer",
            content_type="infographic",
            body="Infografis 3 poin fakta vs hoaks.",
            media_url="https://cdn.demo/infografis-jembatan-anyer.png",
            status="published",
            created_by=editor.id if editor else None,
            created_at=now - timedelta(hours=2),
        ),
        ContentItem(
            issue_id=i2.id,
            title="Penjelasan Layanan RSUD & Antrean Digital",
            content_type="text_release",
            body="Klarifikasi Dinkes terkait antrian dan peningkatan layanan RSUD.",
            status="in_review",
            created_by=editor.id if editor else None,
            created_at=now - timedelta(hours=9),
        ),
        ContentItem(
            issue_id=i6.id,
            title="Update Pemantauan Kualitas Udara Kawasan Industri",
            content_type="text_release",
            body="Ringkasan hasil pengukuran & langkah pengawasan industri.",
            status="approved",
            created_by=editor.id if editor else None,
            created_at=now - timedelta(hours=5),
        ),
        ContentItem(
            issue_id=created_issues["SEED-DEMO-005"].id,
            title="Himbauan: Abaikan Hoaks Libur ASN",
            content_type="text_release",
            body="Tidak ada SE libur ASN massal. Cek hanya kanal resmi.",
            status="published",
            created_by=editor.id if editor else None,
            created_at=now - timedelta(hours=60),
        ),
        ContentItem(
            issue_id=i3.id,
            title="Draft: Klarifikasi Penyaluran Bansos",
            content_type="text_release",
            body="Draft menunggu data OPD Sosial.",
            status="draft",
            created_by=editor.id if editor else None,
            created_at=now - timedelta(hours=6),
        ),
    ]
    for c in contents:
        db.session.add(c)
    db.session.flush()

    # Approvals for published/approved
    for c in contents:
        if c.status in {"published", "approved"} and pimpinan:
            db.session.add(
                ContentApproval(
                    content_id=c.id,
                    reviewer_id=pimpinan.id,
                    decision="approved",
                    notes="Disetujui untuk diseminasi.",
                    decided_at=c.created_at + timedelta(minutes=40),
                )
            )

    # Alerts
    alerts = [
        CrisisAlert(
            issue_id=i1.id,
            alert_type="risk_threshold",
            title="Alert R4: Hoaks jembatan Anyer",
            message="Risk R4 — segera validasi OPD dan siapkan klarifikasi.",
            risk_level="R4",
            severity="critical",
            channels=["web", "whatsapp", "telegram"],
            delivery_status={"web": "delivered", "whatsapp": "mocked", "telegram": "mocked"},
            is_read=False,
            created_at=now - timedelta(hours=4, minutes=50),
        ),
        CrisisAlert(
            issue_id=i2.id,
            alert_type="risk_threshold",
            title="Alert R3: Keluhan RSUD viral",
            message="Video keluhan RSUD mencapai ambang elevated.",
            risk_level="R3",
            severity="high",
            channels=["web", "whatsapp"],
            delivery_status={"web": "delivered", "whatsapp": "mocked"},
            is_read=True,
            read_at=now - timedelta(hours=12),
            created_at=now - timedelta(hours=17),
        ),
        CrisisAlert(
            issue_id=i3.id,
            alert_type="response_overdue",
            title="Overdue: Validasi bansos menunggu OPD",
            message="Permintaan validasi ke Dinas Sosial melebihi 2 jam.",
            risk_level="R3",
            severity="high",
            channels=["web"],
            delivery_status={"web": "delivered"},
            is_read=False,
            created_at=now - timedelta(hours=5),
        ),
        CrisisAlert(
            issue_id=i6.id,
            alert_type="risk_threshold",
            title="Alert R4: Isu pencemaran udara",
            message="Sentimen negatif tinggi terkait kawasan industri.",
            risk_level="R4",
            severity="critical",
            channels=["web", "whatsapp", "telegram"],
            delivery_status={"web": "delivered", "whatsapp": "mocked", "telegram": "mocked"},
            is_read=False,
            created_at=now - timedelta(hours=11),
        ),
    ]
    for a in alerts:
        db.session.add(a)

    db.session.commit()


def seed_media_ops() -> None:
    """Blast logs + SLA (idempotent)."""
    if MediaBlastLog.query.filter(MediaBlastLog.channel == "seed_demo_marker").first():
        return
    # Use notes in result marker instead — check by content title linkage
    published = ContentItem.query.filter_by(
        title="Klarifikasi: Perbaikan Jembatan Anyer Terkendali"
    ).first()
    if not published:
        return
    if MediaBlastLog.query.filter_by(content_id=published.id).first():
        return

    media_user = _user("media")
    partners = MediaPartner.query.filter_by(is_active=True).order_by(MediaPartner.id).all()
    if not partners:
        return

    now = _utcnow()
    recipients = [
        {"id": p.id, "name": p.name, "whatsapp": p.whatsapp, "email": p.email}
        for p in partners[:5]
    ]

    blast1 = MediaBlastLog(
        issue_id=published.issue_id,
        content_id=published.id,
        sent_by=media_user.id if media_user else None,
        channel="both",
        recipients=recipients,
        status="sent",
        result={"sent": len(recipients) * 2, "failed": 0, "note": "seed_demo"},
        sent_at=now - timedelta(hours=2),
    )
    db.session.add(blast1)
    db.session.flush()

    approved = ContentItem.query.filter_by(
        title="Update Pemantauan Kualitas Udara Kawasan Industri"
    ).first()
    if approved:
        blast2 = MediaBlastLog(
            issue_id=approved.issue_id,
            content_id=approved.id,
            sent_by=media_user.id if media_user else None,
            channel="whatsapp",
            recipients=recipients[:3],
            status="partial",
            result={"sent": 4, "failed": 2, "note": "seed_demo"},
            sent_at=now - timedelta(hours=1),
        )
        db.session.add(blast2)

    # SLA logs — some compliant, some late
    for idx, partner in enumerate(partners[:6]):
        minutes = [25, 40, 55, 70, 35, 95][idx]
        db.session.add(
            MediaSlaLog(
                media_partner_id=partner.id,
                blast_log_id=blast1.id,
                published_at=blast1.sent_at + timedelta(minutes=minutes),
                response_minutes=minutes,
                content_match=True,
                sla_compliant=minutes <= 60,
                notes="Seed demo SLA" if minutes <= 60 else "Terlambat tayang — seed demo",
                created_at=now - timedelta(hours=1, minutes=50 - idx),
            )
        )

    db.session.commit()


def seed_missions() -> None:
    if Mission.query.filter_by(title="Amplifikasi klarifikasi jembatan Anyer").first():
        return

    editor = _user("editor")
    asn = _user("asn")
    asn2 = _user("asn2")
    asn3 = _user("asn3")
    issue = Issue.query.filter_by(mb_alert_id="SEED-DEMO-001").first()
    issue5 = Issue.query.filter_by(mb_alert_id="SEED-DEMO-005").first()
    now = _utcnow()

    missions = [
        Mission(
            issue_id=issue.id if issue else None,
            title="Amplifikasi klarifikasi jembatan Anyer",
            instruction=(
                "Like, Share, dan Comment positif pada postingan resmi Adpim "
                "tentang klarifikasi jembatan Anyer. Gunakan nada tenang & faktual."
            ),
            target_url="https://instagram.com/p/demo-klarifikasi-anyer",
            action_type="like_share_comment",
            target_count=80,
            starts_at=now - timedelta(hours=3),
            ends_at=now + timedelta(days=1),
            status="active",
            created_by=editor.id if editor else None,
            created_at=now - timedelta(hours=3),
        ),
        Mission(
            issue_id=issue5.id if issue5 else None,
            title="Sebarkan himbauan anti-hoaks libur ASN",
            instruction="Share postingan himbauan resmi ke story / grup internal OPD.",
            target_url="https://instagram.com/p/demo-anti-hoaks-asn",
            action_type="share",
            target_count=50,
            starts_at=now - timedelta(days=2),
            ends_at=now - timedelta(hours=12),
            status="completed",
            created_by=editor.id if editor else None,
            created_at=now - timedelta(days=2),
        ),
        Mission(
            issue_id=None,
            title="Dukung konten positif wisata Anyer",
            instruction="Like & comment suportif pada konten pariwisata resmi minggu ini.",
            target_url="https://instagram.com/p/demo-wisata-anyer",
            action_type="like_share_comment",
            target_count=100,
            starts_at=now - timedelta(hours=1),
            ends_at=now + timedelta(days=3),
            status="active",
            created_by=editor.id if editor else None,
            created_at=now - timedelta(hours=1),
        ),
        Mission(
            title="Mission draft dibatalkan (demo)",
            instruction="Contoh misi yang dibatalkan.",
            target_url="https://example.com",
            action_type="like",
            target_count=10,
            status="cancelled",
            created_by=editor.id if editor else None,
            created_at=now - timedelta(days=5),
        ),
    ]
    for m in missions:
        db.session.add(m)
    db.session.flush()

    active = missions[0]
    completed = missions[1]
    participants = [
        (asn, "Dinas Komunikasi, Informatika, Statistik dan Persandian", active),
        (asn2, "Dinas Kesehatan", active),
        (asn3, "Dinas Pekerjaan Umum dan Penataan Ruang", active),
        (asn, "Dinas Komunikasi, Informatika, Statistik dan Persandian", completed),
        (asn2, "Dinas Kesehatan", completed),
        (asn3, "Dinas Pekerjaan Umum dan Penataan Ruang", completed),
    ]
    for user, opd_name, mission in participants:
        if not user:
            continue
        db.session.add(
            MissionParticipation(
                mission_id=mission.id,
                user_id=user.id,
                opd_name=opd_name,
                proof_url=f"https://instagram.com/p/proof-{user.username}",
                notes="Sudah dilakukan — seed demo",
                completed_at=now - timedelta(hours=1),
            )
        )

    db.session.commit()


def seed_kol_campaigns() -> None:
    if KolCampaign.query.filter_by(title="Reel klarifikasi jembatan Anyer").first():
        return

    partners = {p.name: p for p in KolPartner.query.all()}
    issue1 = Issue.query.filter_by(mb_alert_id="SEED-DEMO-001").first()
    issue7 = Issue.query.filter_by(mb_alert_id="SEED-DEMO-007").first()
    now = _utcnow()

    demos = [
        {
            "kol": "Raka Banten",
            "issue": issue1,
            "title": "Reel klarifikasi jembatan Anyer",
            "deliverable_url": "https://instagram.com/reel/demo-anyer",
            "status": "published",
            "views": 85000,
            "likes": 6200,
            "comments": 410,
            "budget": 7500000,
            "budget_status": "paid",
            "published_at": now - timedelta(hours=1),
        },
        {
            "kol": "Salsa Serang",
            "issue": issue1,
            "title": "TikTok fakta perbaikan jembatan",
            "deliverable_url": "https://tiktok.com/@salsaserang/video/demo",
            "status": "published",
            "views": 210000,
            "likes": 18000,
            "comments": 920,
            "budget": 12000000,
            "budget_status": "approved",
            "published_at": now - timedelta(minutes=40),
        },
        {
            "kol": "Naufal Cilegon",
            "issue": None,
            "title": "Highlight investasi Cilegon",
            "deliverable_url": None,
            "status": "in_progress",
            "views": 0,
            "likes": 0,
            "comments": 0,
            "budget": 5000000,
            "budget_status": "planned",
            "scheduled_at": now + timedelta(days=3),
        },
        {
            "kol": "Voice of Pandeglang",
            "issue": issue7,
            "title": "Thread positif wisata Anyer",
            "deliverable_url": "https://x.com/voicpandeglang/status/demo",
            "status": "planned",
            "views": 0,
            "likes": 0,
            "comments": 0,
            "budget": 3000000,
            "budget_status": "approved",
            "scheduled_at": now + timedelta(days=1),
        },
        {
            "kol": "Banten Insight",
            "issue": None,
            "title": "Video opini pembangunan infrastruktur",
            "deliverable_url": None,
            "status": "planned",
            "views": 0,
            "likes": 0,
            "comments": 0,
            "budget": 15000000,
            "budget_status": "planned",
            "scheduled_at": now + timedelta(days=7),
        },
    ]

    for item in demos:
        partner = partners.get(item["kol"])
        if not partner:
            continue
        issue = item["issue"]
        db.session.add(
            KolCampaign(
                kol_id=partner.id,
                issue_id=issue.id if issue else None,
                title=item["title"],
                deliverable_url=item.get("deliverable_url"),
                scheduled_at=item.get("scheduled_at"),
                published_at=item.get("published_at"),
                views=item["views"],
                likes=item["likes"],
                comments=item["comments"],
                budget=item["budget"],
                budget_status=item["budget_status"],
                status=item["status"],
                notes="Seed demo campaign",
                created_at=now - timedelta(days=1),
            )
        )
    db.session.commit()


def seed_all() -> None:
    ensure_schema()
    seed_roles()
    seed_opds()
    seed_users()
    seed_media_partners()
    seed_kol_partners()
    seed_agenda()
    seed_issues_and_pipeline()
    seed_media_ops()
    seed_missions()
    seed_kol_campaigns()


if __name__ == "__main__":
    from app import create_app

    app = create_app()
    with app.app_context():
        db.create_all()
        seed_all()
        print("Seed complete.")
        print(
            "Counts:",
            f"opds={Opd.query.count()}",
            f"users={User.query.count()}",
            f"issues={Issue.query.count()}",
            f"content={ContentItem.query.count()}",
            f"validations={OpdValidation.query.count()}",
            f"alerts={CrisisAlert.query.count()}",
            f"media={MediaPartner.query.count()}",
            f"sla={MediaSlaLog.query.count()}",
            f"blasts={MediaBlastLog.query.count()}",
            f"missions={Mission.query.count()}",
            f"asn_logs={MissionParticipation.query.count()}",
            f"kol={KolPartner.query.count()}",
            f"campaigns={KolCampaign.query.count()}",
            f"agenda={EditorialAgenda.query.count()}",
        )
