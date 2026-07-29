"""Report builders — Excel (openpyxl) + PDF (fpdf2) for PRD §9.1."""

from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO

from openpyxl import Workbook
from fpdf import FPDF

from app.extensions import db
from app.models import (
    ContentItem,
    Issue,
    KolCampaign,
    KolPartner,
    MediaBlastLog,
    MediaPartner,
    MediaSlaLog,
    Mission,
    MissionParticipation,
    OpdValidation,
    Report,
)
from sqlalchemy import func


def _now():
    return datetime.now(timezone.utc)


def _wb_bytes(wb: Workbook) -> bytes:
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _sheet(wb: Workbook, title: str, headers: list[str], rows: list[list]):
    ws = wb.active if wb.active.title == "Sheet" and not wb.active["A1"].value else wb.create_sheet(title)
    if wb.active.title == "Sheet" and not wb.active["A1"].value:
        ws.title = title
    ws.append(headers)
    for row in rows:
        ws.append(row)
    return ws


class _ReportPDF(FPDF):
    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", size=8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"SULTAN BANTEN - halaman {self.page_no()}", align="C")


def _safe(text: str) -> str:
    """Helvetica core fonts are Latin-1; strip unsupported glyphs."""
    if text is None:
        return ""
    return str(text).encode("latin-1", errors="replace").decode("latin-1")


def _pdf_bytes(title: str, lines: list[str], sections: list[tuple[str, list[str]]] | None = None) -> bytes:
    pdf = _ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(0, 8, _safe(title))
    pdf.set_font("Helvetica", size=10)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 6, f"Dibuat: {_now().strftime('%Y-%m-%d %H:%M UTC')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_text_color(20, 20, 20)
    for line in lines:
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(0, 6, _safe(line))
    for section_title, section_lines in sections or []:
        pdf.ln(3)
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "B", 12)
        pdf.multi_cell(0, 7, _safe(section_title))
        pdf.set_font("Helvetica", size=10)
        for line in section_lines:
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(0, 5, _safe(f"- {line}"))
    out = pdf.output()
    if isinstance(out, (bytes, bytearray)):
        return bytes(out)
    return out.encode("latin-1")


def _save_report(report_type: str, title: str, payload: dict, user_id: int | None) -> Report:
    report = Report(
        report_type=report_type,
        title=title,
        period_end=_now(),
        payload=payload,
        generated_by=user_id,
    )
    db.session.add(report)
    db.session.commit()
    return report


# ── Crisis ──────────────────────────────────────────────────────────────────


def collect_crisis(issue_id: int | None = None) -> dict:
    q = Issue.query.order_by(Issue.created_at.desc())
    if issue_id:
        q = q.filter_by(id=issue_id)
    issues = q.limit(50).all()
    rows = []
    for issue in issues:
        vals = OpdValidation.query.filter_by(issue_id=issue.id).all()
        contents = ContentItem.query.filter_by(issue_id=issue.id).all()
        blasts = MediaBlastLog.query.filter_by(issue_id=issue.id).count()
        rows.append(
            {
                "id": issue.id,
                "title": issue.title,
                "risk_level": issue.risk_level,
                "status": issue.status,
                "source": issue.source,
                "mb_alert_id": issue.mb_alert_id,
                "summary": (issue.summary or "")[:300],
                "validations": len(vals),
                "validated": sum(1 for v in vals if v.status == "validated"),
                "contents": len(contents),
                "blasts": blasts,
                "created_at": issue.created_at.isoformat() if issue.created_at else None,
                "closed_at": issue.closed_at.isoformat() if issue.closed_at else None,
            }
        )
    return {"type": "crisis", "count": len(rows), "issues": rows}


def export_crisis(fmt: str, issue_id: int | None, user_id: int | None):
    data = collect_crisis(issue_id)
    title = "Laporan Penanganan Krisis"
    _save_report("crisis", title, data, user_id)
    if fmt == "xlsx":
        wb = Workbook()
        _sheet(
            wb,
            "Isu",
            [
                "ID",
                "Judul",
                "Risk",
                "Status",
                "Sumber",
                "MB Alert",
                "Validasi",
                "Konten",
                "Blast",
                "Dibuat",
                "Ditutup",
            ],
            [
                [
                    i["id"],
                    i["title"],
                    i["risk_level"],
                    i["status"],
                    i["source"],
                    i["mb_alert_id"] or "",
                    i["validated"],
                    i["contents"],
                    i["blasts"],
                    i["created_at"] or "",
                    i["closed_at"] or "",
                ]
                for i in data["issues"]
            ],
        )
        return _wb_bytes(wb), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "laporan-krisis.xlsx"
    lines = [f"Total isu: {data['count']}"]
    sections = [
        (
            "Daftar isu",
            [
                f"#{i['id']} [{i['risk_level']}/{i['status']}] {i['title']}"
                for i in data["issues"]
            ]
            or ["Tidak ada data"],
        )
    ]
    return _pdf_bytes(title, lines, sections), "application/pdf", "laporan-krisis.pdf"


# ── Media SLA ───────────────────────────────────────────────────────────────


def collect_media_sla() -> dict:
    logs = MediaSlaLog.query.order_by(MediaSlaLog.created_at.desc()).limit(200).all()
    partners = {p.id: p for p in MediaPartner.query.all()}
    rows = []
    for log in logs:
        p = partners.get(log.media_partner_id)
        rows.append(
            {
                "id": log.id,
                "media": p.name if p else f"#{log.media_partner_id}",
                "response_minutes": log.response_minutes,
                "sla_compliant": log.sla_compliant,
                "content_match": log.content_match,
                "published_at": log.published_at.isoformat() if log.published_at else None,
                "notes": log.notes,
            }
        )
    total = len(rows)
    compliant = sum(1 for r in rows if r["sla_compliant"])
    return {
        "type": "media_sla",
        "total": total,
        "compliant": compliant,
        "rate": round(100 * compliant / total, 1) if total else 0,
        "logs": rows,
    }


def export_media_sla(fmt: str, user_id: int | None):
    data = collect_media_sla()
    title = "Laporan Aktivitas Media (SLA)"
    _save_report("media_sla", title, data, user_id)
    if fmt == "xlsx":
        wb = Workbook()
        _sheet(
            wb,
            "SLA",
            ["ID", "Media", "Menit", "Compliant", "Content Match", "Published", "Notes"],
            [
                [
                    r["id"],
                    r["media"],
                    r["response_minutes"],
                    "Ya" if r["sla_compliant"] else "Tidak",
                    "Ya" if r["content_match"] else "Tidak",
                    r["published_at"] or "",
                    r["notes"] or "",
                ]
                for r in data["logs"]
            ],
        )
        return _wb_bytes(wb), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "laporan-sla-media.xlsx"
    lines = [
        f"Total log: {data['total']}",
        f"Compliant: {data['compliant']} ({data['rate']}%)",
        "SLA target: 60 menit",
    ]
    sections = [
        (
            "Log terbaru",
            [
                f"{r['media']}: {r['response_minutes']} mnt — "
                f"{'OK' if r['sla_compliant'] else 'Lewat SLA'}"
                for r in data["logs"][:40]
            ]
            or ["Belum ada log SLA"],
        )
    ]
    return _pdf_bytes(title, lines, sections), "application/pdf", "laporan-sla-media.pdf"


# ── ASN ─────────────────────────────────────────────────────────────────────


def collect_asn() -> dict:
    rows = (
        db.session.query(
            MissionParticipation.opd_name,
            func.count(MissionParticipation.id),
        )
        .group_by(MissionParticipation.opd_name)
        .order_by(func.count(MissionParticipation.id).desc())
        .all()
    )
    by_opd = [{"opd_name": r[0] or "Tanpa OPD", "total": r[1]} for r in rows]
    missions = Mission.query.order_by(Mission.created_at.desc()).limit(50).all()
    return {
        "type": "asn",
        "grand_total": sum(x["total"] for x in by_opd),
        "by_opd": by_opd,
        "missions": [
            {
                "id": m.id,
                "title": m.title,
                "status": m.status,
                "participations": len(m.participations),
                "target_count": m.target_count,
            }
            for m in missions
        ],
    }


def export_asn(fmt: str, user_id: int | None):
    data = collect_asn()
    title = "Rekap Partisipasi ASN per OPD"
    _save_report("asn", title, data, user_id)
    if fmt == "xlsx":
        wb = Workbook()
        _sheet(
            wb,
            "Per OPD",
            ["OPD", "Partisipasi"],
            [[r["opd_name"], r["total"]] for r in data["by_opd"]],
        )
        _sheet(
            wb,
            "Misi",
            ["ID", "Judul", "Status", "Partisipasi", "Target"],
            [
                [m["id"], m["title"], m["status"], m["participations"], m["target_count"]]
                for m in data["missions"]
            ],
        )
        return _wb_bytes(wb), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "rekap-asn.xlsx"
    lines = [f"Total partisipasi: {data['grand_total']}"]
    sections = [
        ("Per OPD", [f"{r['opd_name']}: {r['total']}" for r in data["by_opd"]] or ["Kosong"]),
        (
            "Misi",
            [f"#{m['id']} {m['title']} ({m['participations']}/{m['target_count']})" for m in data["missions"]]
            or ["Kosong"],
        ),
    ]
    return _pdf_bytes(title, lines, sections), "application/pdf", "rekap-asn.pdf"


# ── KOL ─────────────────────────────────────────────────────────────────────


def collect_kol() -> dict:
    campaigns = KolCampaign.query.order_by(KolCampaign.created_at.desc()).limit(100).all()
    partners = {p.id: p for p in KolPartner.query.all()}
    rows = []
    for c in campaigns:
        p = partners.get(c.kol_id)
        rows.append(
            {
                "id": c.id,
                "title": c.title,
                "kol": p.name if p else f"#{c.kol_id}",
                "status": c.status,
                "views": c.views or 0,
                "likes": c.likes or 0,
                "comments": c.comments or 0,
                "budget": float(c.budget) if c.budget is not None else None,
                "budget_status": c.budget_status,
                "deliverable_url": c.deliverable_url,
            }
        )
    return {
        "type": "kol",
        "count": len(rows),
        "total_views": sum(r["views"] for r in rows),
        "campaigns": rows,
    }


def export_kol(fmt: str, user_id: int | None):
    data = collect_kol()
    title = "Laporan Kinerja KOL & Campaign"
    _save_report("kol", title, data, user_id)
    if fmt == "xlsx":
        wb = Workbook()
        _sheet(
            wb,
            "Campaign",
            ["ID", "Judul", "KOL", "Status", "Views", "Likes", "Comments", "Budget", "Budget Status"],
            [
                [
                    r["id"],
                    r["title"],
                    r["kol"],
                    r["status"],
                    r["views"],
                    r["likes"],
                    r["comments"],
                    r["budget"],
                    r["budget_status"],
                ]
                for r in data["campaigns"]
            ],
        )
        return _wb_bytes(wb), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "laporan-kol.xlsx"
    lines = [f"Campaign: {data['count']}", f"Total views: {data['total_views']}"]
    sections = [
        (
            "Campaign",
            [
                f"#{r['id']} {r['title']} — {r['kol']} ({r['views']} views)"
                for r in data["campaigns"]
            ]
            or ["Kosong"],
        )
    ]
    return _pdf_bytes(title, lines, sections), "application/pdf", "laporan-kol.pdf"


# ── Executive ───────────────────────────────────────────────────────────────


def collect_executive() -> dict:
    open_statuses = {"open", "validating", "producing", "approved"}
    issues = Issue.query.all()
    active = [i for i in issues if i.status in open_statuses]
    critical = [i for i in active if i.risk_level in {"R3", "R4", "R5"}]
    waiting = OpdValidation.query.filter_by(status="waiting").count()
    asn_total = MissionParticipation.query.count()
    kol_views = db.session.query(func.coalesce(func.sum(KolCampaign.views), 0)).scalar() or 0
    return {
        "type": "executive",
        "headline": f"{len(critical)} isu kritis aktif dari {len(active)} isu terbuka",
        "kpis": {
            "active_issues": len(active),
            "critical_issues": len(critical),
            "waiting_validations": waiting,
            "asn_participations": asn_total,
            "kol_views": int(kol_views),
        },
        "critical_titles": [i.title for i in critical[:10]],
        "recommendations": [
            "Prioritaskan validasi OPD untuk isu R3+",
            "Pastikan konten approved segera di-blast",
            "Aktifkan misi ASN untuk amplifikasi organik",
        ],
    }


def export_executive(fmt: str, user_id: int | None):
    data = collect_executive()
    title = "Executive Brief"
    _save_report("executive", title, data, user_id)
    k = data["kpis"]
    if fmt == "xlsx":
        wb = Workbook()
        _sheet(
            wb,
            "KPI",
            ["Metrik", "Nilai"],
            [
                ["Isu aktif", k["active_issues"]],
                ["Isu kritis", k["critical_issues"]],
                ["Validasi menunggu", k["waiting_validations"]],
                ["Partisipasi ASN", k["asn_participations"]],
                ["Views KOL", k["kol_views"]],
            ],
        )
        _sheet(
            wb,
            "Isu kritis",
            ["Judul"],
            [[t] for t in data["critical_titles"]],
        )
        return _wb_bytes(wb), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "executive-brief.xlsx"
    lines = [data["headline"], ""] + [f"{key}: {val}" for key, val in k.items()]
    sections = [
        ("Isu kritis", data["critical_titles"] or ["Tidak ada"]),
        ("Rekomendasi", data["recommendations"]),
    ]
    return _pdf_bytes(title, lines, sections), "application/pdf", "executive-brief.pdf"
