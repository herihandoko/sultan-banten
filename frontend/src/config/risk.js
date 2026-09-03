/** Risk level R0–R5 — selaras PRD SIAGAPIM */
export const RISK_LEVELS = ['R0', 'R1', 'R2', 'R3', 'R4', 'R5']

export const RISK_META = {
  R0: {
    code: 'R0',
    label: 'Informational',
    short: 'Informasional',
    description: 'Informasi umum — pantau saja, belum perlu tindakan khusus.',
    colorClass: 'bg-slate-200 text-slate-700',
    chartColor: '#94a3b8',
  },
  R1: {
    code: 'R1',
    label: 'Observe',
    short: 'Observe',
    description: 'Perlu diamati — pantau perkembangan isu secara berkala.',
    colorClass: 'bg-sky-100 text-sky-800',
    chartColor: '#38bdf8',
  },
  R2: {
    code: 'R2',
    label: 'Watch',
    short: 'Watch',
    description: 'Waspadai — siapkan respons jika isu membesar.',
    colorClass: 'bg-amber-100 text-amber-800',
    chartColor: '#fbbf24',
  },
  R3: {
    code: 'R3',
    label: 'Elevated',
    short: 'Elevated',
    description: 'Risiko meningkat — biasanya memicu alert; segera koordinasikan.',
    colorClass: 'bg-orange-100 text-orange-800',
    chartColor: '#fb923c',
  },
  R4: {
    code: 'R4',
    label: 'High',
    short: 'High',
    description: 'Risiko tinggi — prioritas penanganan dan klarifikasi segera.',
    colorClass: 'bg-red-100 text-red-800',
    chartColor: '#f87171',
  },
  R5: {
    code: 'R5',
    label: 'Critical',
    short: 'Critical',
    description: 'Kritis — eskalasi penuh, tindakan segera diperlukan.',
    colorClass: 'bg-banten-red text-white',
    chartColor: '#C0392B',
  },
}

export function riskMeta(level) {
  return RISK_META[level] || RISK_META.R0
}

export function riskTitle(level) {
  const m = riskMeta(level)
  return `${m.code} — ${m.label}: ${m.description}`
}

export function riskOptionLabel(level) {
  const m = riskMeta(level)
  return `${m.code} — ${m.short}`
}

export const riskColor = Object.fromEntries(
  RISK_LEVELS.map((code) => [code, RISK_META[code].colorClass]),
)
