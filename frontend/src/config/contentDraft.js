export const CONTENT_TYPES = [
  {
    value: 'text_release',
    label: 'Rilis Teks',
    hint: 'Naskah resmi untuk media',
    titleLabel: 'Judul rilis',
    bodyLabel: 'Naskah rilis',
    bodyPlaceholder: 'Lead, fakta yang diluruskan, pernyataan resmi, dan narahubung…',
    bodyRows: 8,
    mediaLabel: '',
    mediaPlaceholder: '',
    note: 'Tulis naskah lengkap. Rilis ini yang nanti dikirim lewat Media Blast.',
  },
  {
    value: 'infographic',
    label: 'Infografis',
    hint: 'Kartu Banten Meluruskan Fakta',
    titleLabel: 'Judul kartu',
    bodyLabel: 'Poin kartu',
    bodyPlaceholder: '3–5 poin fakta singkat, sumber data, dan ajakan…',
    bodyRows: 8,
    mediaLabel: 'Tautan file infografis',
    mediaPlaceholder: 'https://… (PNG, PDF, atau tautan desain)',
    note: 'Isi poin singkat untuk desainer. Tempel tautan file bila desain sudah jadi.',
  },
  {
    value: 'video',
    label: 'Video',
    hint: 'Naskah bicara dan tautan video',
    titleLabel: 'Judul video',
    bodyLabel: 'Naskah / poin bicara',
    bodyPlaceholder: 'Hook, poin bicara, dan penutup…',
    bodyRows: 8,
    mediaLabel: 'Tautan video',
    mediaPlaceholder: 'https://… (YouTube, Drive, atau file video)',
    note: 'Tulis naskah singkat, lalu tempel tautan video yang sudah diunggah.',
  },
]

export function contentTypeMeta(type) {
  return CONTENT_TYPES.find((item) => item.value === type) || CONTENT_TYPES[0]
}

export function draftFromIssue(issue, type) {
  const statement = (issue?.narrative_card?.statement || issue?.summary || '').trim()
  const summary = (issue?.summary || '').trim()
  const title = (issue?.title || '').trim()

  if (type === 'infographic') {
    return {
      title,
      body: [
        'POIN FAKTA',
        statement ? `• ${statement}` : '• ',
        '• ',
        '• ',
        '',
        'SUMBER',
        '• ',
        '',
        'AJAKAN',
        'Cek klarifikasi resmi di kanal Pemprov Banten.',
      ].join('\n'),
    }
  }

  if (type === 'video') {
    const hook = statement.split(/[.!?]/)[0]?.trim() || title
    return {
      title: title ? `Video: ${title}` : '',
      body: [
        'HOOK',
        hook,
        '',
        'POIN BICARA',
        statement ? `1. ${statement}` : '1. ',
        '2. ',
        '3. ',
        '',
        'PENUTUP',
        'Ikuti kanal resmi Pemprov Banten.',
      ].join('\n'),
    }
  }

  const extra = summary && summary !== statement ? `\n${summary}` : ''
  return {
    title: title ? `Klarifikasi: ${title}` : '',
    body: ['Banten Meluruskan Fakta', '', statement, extra, '', 'Narahubung: Biro Adpim Provinsi Banten']
      .filter((line, index, all) => line !== '' || all[index - 1] !== '')
      .join('\n')
      .trim(),
  }
}
