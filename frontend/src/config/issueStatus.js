/** Status isu — selaras USER_MANUAL / PRD SIAGAPIM */
export const ISSUE_STATUSES = [
  'open',
  'validating',
  'producing',
  'approved',
  'disseminated',
  'closed',
]

export const ISSUE_STATUS_META = {
  open: {
    code: 'open',
    short: 'Open',
    actor: 'Editor',
    description: 'Baru masuk / perlu ditindak.',
    colorClass: 'bg-sky-100 text-sky-800',
    outlineClass: 'border border-sky-400/40 bg-sky-400/15 text-sky-300',
  },
  validating: {
    code: 'validating',
    short: 'Validating',
    actor: 'OPD',
    description: 'Sedang diminta klarifikasi OPD.',
    colorClass: 'bg-amber-100 text-amber-900',
    outlineClass: 'border border-amber-400/40 bg-amber-400/15 text-amber-300',
  },
  producing: {
    code: 'producing',
    short: 'Producing',
    actor: 'Editor',
    description: 'Produksi konten klarifikasi.',
    colorClass: 'bg-violet-100 text-violet-800',
    outlineClass: 'border border-violet-400/40 bg-violet-400/15 text-violet-300',
  },
  approved: {
    code: 'approved',
    short: 'Approved',
    actor: 'Pimpinan',
    description: 'Konten sudah disetujui.',
    colorClass: 'bg-emerald-100 text-emerald-800',
    outlineClass: 'border border-emerald-500/40 bg-emerald-500/15 text-emerald-300',
  },
  disseminated: {
    code: 'disseminated',
    short: 'Disseminated',
    actor: 'Media',
    description: 'Sudah disebar (blast, media, dll.).',
    colorClass: 'bg-banten-sand text-banten-navy',
    outlineClass: 'border border-cyan-400/40 bg-cyan-400/15 text-cyan-300',
  },
  closed: {
    code: 'closed',
    short: 'Closed',
    actor: 'Editor',
    description: 'Selesai ditutup.',
    colorClass: 'bg-slate-200 text-slate-700',
    outlineClass: 'border border-slate-400/40 bg-slate-400/15 text-slate-300',
  },
}

export function issueStatusMeta(status) {
  return ISSUE_STATUS_META[status] || {
    code: status || '—',
    short: status || '—',
    description: 'Status isu',
    colorClass: 'bg-banten-sand text-banten-navy',
    outlineClass: 'border border-slate-400/40 bg-slate-400/15 text-slate-300',
  }
}

export function issueStatusTitle(status) {
  const m = issueStatusMeta(status)
  return `${m.short}: ${m.description}`
}

export function issueStatusOptionLabel(status) {
  const m = issueStatusMeta(status)
  return `${m.short} — ${m.description}`
}
