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
    description: 'Baru masuk / perlu ditindak.',
    colorClass: 'bg-sky-100 text-sky-800',
  },
  validating: {
    code: 'validating',
    short: 'Validating',
    description: 'Sedang diminta klarifikasi OPD.',
    colorClass: 'bg-amber-100 text-amber-900',
  },
  producing: {
    code: 'producing',
    short: 'Producing',
    description: 'Produksi konten klarifikasi.',
    colorClass: 'bg-violet-100 text-violet-800',
  },
  approved: {
    code: 'approved',
    short: 'Approved',
    description: 'Konten sudah disetujui.',
    colorClass: 'bg-emerald-100 text-emerald-800',
  },
  disseminated: {
    code: 'disseminated',
    short: 'Disseminated',
    description: 'Sudah disebar (blast, media, dll.).',
    colorClass: 'bg-banten-sand text-banten-navy',
  },
  closed: {
    code: 'closed',
    short: 'Closed',
    description: 'Selesai ditutup.',
    colorClass: 'bg-slate-200 text-slate-700',
  },
}

export function issueStatusMeta(status) {
  return ISSUE_STATUS_META[status] || {
    code: status || '—',
    short: status || '—',
    description: 'Status isu',
    colorClass: 'bg-banten-sand text-banten-navy',
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
