<script setup>
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'

const query = ref('')
const activeId = ref('konteks')

const sections = [
  { id: 'konteks', title: 'Peta konteks', text: 'mata bathin sipantau intelijen alert brief' },
  { id: 'sop', title: 'SOP kontra-isu', text: 'crisis room validasi konten blast laporan' },
  { id: 'isu', title: 'Status isu', text: 'terbuka validasi produksi disetujui disebar ditutup' },
  { id: 'konten', title: 'Status konten', text: 'draf review disetujui terbit ditolak' },
  { id: 'opd', title: 'Validasi OPD', text: 'perangkat daerah tervalidasi ditolak' },
  { id: 'sebar', title: 'Diseminasi paralel', text: 'media blast asn kol sla whatsapp email' },
  { id: 'agenda', title: 'Agenda proaktif', text: 'konten positif bulanan direncanakan' },
  { id: 'umpan', title: 'Umpan balik', text: 'feedback mata bathin disseminated closed' },
  { id: 'pilar', title: 'Tiga pilar', text: 'crisis room media hub amplifikasi laporan' },
  { id: 'cek', title: 'Checklist', text: 'deteksi validasi klarifikasi blast tutup agenda' },
]

const steps = [
  {
    n: '01',
    title: 'Terima isu dan alert',
    who: 'Super Admin · Editor · Pimpinan',
    body: 'Mata Bathin atau SIPANTAU mengirim isu, atau Editor memasukkan isu manual. Status awal Terbuka. Isu R3 ke atas atau respons yang terlambat muncul di lonceng.',
    href: '/crisis-room',
    menu: 'Crisis Room',
  },
  {
    n: '02',
    title: 'Minta validasi OPD',
    who: 'Editor meminta · Admin OPD menjawab',
    body: 'Editor memilih OPD dari Master OPD. Isu menjadi Validasi. Jawaban tervalidasi menggeser isu ke Produksi. Bila ditolak, isu ditinjau ulang.',
    href: '/validasi-opd',
    menu: 'Validasi OPD',
  },
  {
    n: '03',
    title: 'Produksi dan persetujuan',
    who: 'Editor menyusun · Pimpinan menyetujui',
    body: 'Naskah dibuat sebagai draf, diajukan review, lalu disetujui atau dikembalikan. Setelah disetujui, isu berstatus Disetujui dan konten siap disebar.',
    href: '/konten',
    menu: 'Hub Konten',
  },
  {
    n: '04',
    title: 'Sebar, amplifikasi, catat SLA',
    who: 'Editor · Media · ASN',
    body: 'Blast ke media mitra mengubah isu menjadi Telah disebar. Misi ASN dan campaign KOL bisa jalan bersamaan. Waktu tayang dicatat untuk SLA 60 menit.',
    href: '/media-hub',
    menu: 'Media Hub',
  },
  {
    n: '05',
    title: 'Pantau, arsipkan, tutup',
    who: 'Pimpinan · Super Admin',
    body: 'Dashboard eksekutif, laporan PDF/Excel, dan arsip merangkum hasil. Isu ditutup setelah respons selesai, lalu umpan balik dikirim ke Mata Bathin.',
    href: '/reports',
    menu: 'Laporan',
  },
]

const issueFlow = ['Terbuka', 'Validasi', 'Produksi', 'Disetujui', 'Telah disebar', 'Ditutup']

const issueBranches = [
  { from: 'Validasi', to: 'Terbuka', hint: 'Semua OPD menolak, atau permintaan diulang' },
  { from: 'Terbuka', to: 'Produksi', hint: 'Konten dibuat tanpa menunggu validasi' },
  { from: 'Produksi', to: 'Telah disebar', hint: 'Blast dilakukan saat isu masih produksi' },
  { from: 'Terbuka / Validasi / Disetujui', to: 'Ditutup', hint: 'Isu ditutup tanpa penyebaran' },
]

const contentFlow = [
  { code: 'Draf', hint: 'Editor menyusun naskah' },
  { code: 'Review', hint: 'Menunggu Pimpinan atau Super Admin' },
  { code: 'Disetujui', hint: 'Siap di-blast' },
  { code: 'Terbit', hint: 'Setelah media blast' },
]

const pillars = [
  {
    title: 'Crisis Room',
    items: ['Crisis Room', 'Alert lonceng', 'Validasi OPD', 'Hub Konten', 'Arsip'],
  },
  {
    title: 'Media Hub',
    items: ['Media mitra', 'SLA 60 menit', 'Media blast', 'Agenda konten positif'],
  },
  {
    title: 'Amplifikasi',
    items: ['Mission Board ASN', 'Log partisipasi', 'Direktori KOL', 'Campaign KOL', 'Dashboard eksekutif'],
  },
]

const checklist = [
  'Isu masuk Crisis Room dengan status Terbuka. Cek lonceng bila risikonya R3 ke atas.',
  'Minta validasi OPD. Setelah ada yang tervalidasi, isu pindah ke Produksi.',
  'Buat konten, ajukan review, lalu tunggu persetujuan pimpinan.',
  'Kirim blast ke mitra. Isu menjadi Telah disebar.',
  'Opsional dan bisa bersamaan: misi ASN serta campaign KOL.',
  'Catat SLA media, lihat rekap ASN, dan unduh laporan.',
  'Tutup isu. Umpan balik ke Mata Bathin terkirim saat disebar atau ditutup.',
  'Isi Agenda untuk konten positif yang terjadwal, terpisah dari alur krisis.',
]

const filteredNav = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return sections
  return sections.filter((section) => `${section.title} ${section.text}`.toLowerCase().includes(q))
})

function isVisible(id) {
  return filteredNav.value.some((section) => section.id === id)
}

function show(id) {
  activeId.value = id
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
</script>

<template>
  <div>
    <div class="mb-5 flex flex-wrap items-end justify-between gap-3">
      <div>
        <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-emerald-400">Panduan</p>
        <h1 class="mt-1 text-2xl font-semibold tracking-tight text-white">Proses bisnis</h1>
        <p class="mt-1 max-w-2xl text-sm text-[#8b949e]">
          SOP dari deteksi isu sampai laporan, mengikuti alur operasional SIAGAPIM.
        </p>
      </div>
      <RouterLink
        to="/panduan"
        class="rounded-xl border border-[#30363d] bg-[#161b22] px-3 py-1.5 text-xs font-semibold text-emerald-300 hover:border-emerald-500/40"
      >
        Buka tutorial
      </RouterLink>
    </div>

    <div class="grid items-start gap-4 lg:grid-cols-[15rem_minmax(0,1fr)]">
      <aside class="rounded-2xl border border-[#30363d] bg-[#161b22] p-3 lg:sticky lg:top-4">
        <label class="block px-2 pb-2">
          <span class="sr-only">Cari bagian</span>
          <input
            v-model="query"
            type="search"
            placeholder="Cari bagian"
            class="w-full rounded-lg border border-[#30363d] bg-[#0d1117] px-3 py-2 text-sm text-[#e6edf3] outline-none placeholder:text-[#6e7681] focus:border-emerald-500/50"
          />
        </label>
        <nav class="flex gap-2 overflow-x-auto lg:flex-col lg:overflow-visible">
          <button
            v-for="section in filteredNav"
            :key="section.id"
            type="button"
            class="shrink-0 rounded-lg px-3 py-2 text-left text-xs font-semibold transition"
            :class="activeId === section.id ? 'bg-[#2b3544] text-white' : 'text-[#8b949e] hover:bg-[#21262d] hover:text-white'"
            @click="show(section.id)"
          >
            {{ section.title }}
          </button>
        </nav>
      </aside>

      <div class="space-y-4">
        <section v-show="isVisible('konteks')" id="konteks" class="scroll-mt-4 rounded-2xl border border-[#30363d] bg-[#161b22] p-5">
          <h2 class="text-base font-semibold text-white">Peta konteks</h2>
          <p class="mt-1 text-sm text-[#8b949e]">Mata Bathin mendeteksi. SIAGAPIM mengeksekusi respons.</p>
          <div class="mt-4 grid gap-3 md:grid-cols-[1fr_auto_1fr] md:items-center">
            <article class="rounded-xl border border-[#30363d] bg-[#0d1117] p-4">
              <p class="text-[11px] font-semibold uppercase tracking-wide text-[#6e7681]">Mata Bathin</p>
              <p class="mt-2 text-sm font-semibold text-white">Mesin intelijen</p>
              <p class="mt-2 text-sm leading-relaxed text-[#c9d1d9]">
                Internet dan media sosial masuk, dinilai risikonya R0–R5, lalu keluar sebagai alert, brief, bukti, dan kartu narasi.
              </p>
            </article>
            <p class="text-center text-xs font-semibold text-emerald-300">mengirim isu</p>
            <article class="rounded-xl border border-[#30363d] bg-[#0d1117] p-4">
              <p class="text-[11px] font-semibold uppercase tracking-wide text-[#6e7681]">SIAGAPIM</p>
              <p class="mt-2 text-sm font-semibold text-white">Pantauan dan eksekusi</p>
              <p class="mt-2 text-sm leading-relaxed text-[#c9d1d9]">
                Crisis Room menerima isu, lalu validasi, konten, penyebaran, amplifikasi, SLA, dan laporan. Hasilnya diumpankan kembali.
              </p>
            </article>
          </div>
        </section>

        <section v-show="isVisible('sop')" id="sop" class="scroll-mt-4 rounded-2xl border border-[#30363d] bg-[#161b22] p-5">
          <h2 class="text-base font-semibold text-white">SOP kontra-isu</h2>
          <p class="mt-1 text-sm text-[#8b949e]">Alur utama saat ada isu yang perlu diluruskan.</p>
          <ol class="mt-4 space-y-3">
            <li v-for="step in steps" :key="step.n" class="rounded-xl border border-[#30363d] bg-[#0d1117] p-4">
              <div class="flex gap-4">
                <span class="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-emerald-500/30 text-sm font-semibold text-emerald-300">
                  {{ step.n }}
                </span>
                <div class="min-w-0 flex-1">
                  <div class="flex flex-wrap items-center justify-between gap-2">
                    <h3 class="text-sm font-semibold text-white">{{ step.title }}</h3>
                    <RouterLink :to="step.href" class="text-xs font-semibold text-emerald-300 hover:text-emerald-200">
                      {{ step.menu }}
                    </RouterLink>
                  </div>
                  <p class="mt-1 text-[11px] font-semibold uppercase tracking-wide text-[#6e7681]">{{ step.who }}</p>
                  <p class="mt-2 text-sm leading-relaxed text-[#c9d1d9]">{{ step.body }}</p>
                </div>
              </div>
            </li>
          </ol>
        </section>

        <section v-show="isVisible('isu')" id="isu" class="scroll-mt-4 rounded-2xl border border-[#30363d] bg-[#161b22] p-5">
          <h2 class="text-base font-semibold text-white">Status isu</h2>
          <p class="mt-1 text-sm text-[#8b949e]">Urutan ideal satu isu.</p>
          <div class="mt-4 flex flex-wrap gap-2">
            <template v-for="(label, index) in issueFlow" :key="label">
              <span class="rounded-lg border border-[#30363d] bg-[#0d1117] px-3 py-2 text-sm font-semibold text-white">{{ label }}</span>
              <span v-if="index < issueFlow.length - 1" class="self-center text-[#6e7681]">→</span>
            </template>
          </div>
          <ul class="mt-4 space-y-2">
            <li
              v-for="branch in issueBranches"
              :key="branch.hint"
              class="rounded-xl border border-[#30363d] bg-[#0d1117] px-4 py-3 text-sm text-[#c9d1d9]"
            >
              <span class="font-semibold text-white">{{ branch.from }}</span>
              <span class="text-[#6e7681]"> → </span>
              <span class="font-semibold text-white">{{ branch.to }}</span>
              <span class="mt-1 block text-xs text-[#8b949e]">{{ branch.hint }}</span>
            </li>
          </ul>
        </section>

        <section v-show="isVisible('konten')" id="konten" class="scroll-mt-4 rounded-2xl border border-[#30363d] bg-[#161b22] p-5">
          <h2 class="text-base font-semibold text-white">Status konten klarifikasi</h2>
          <div class="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <article v-for="item in contentFlow" :key="item.code" class="rounded-xl border border-[#30363d] bg-[#0d1117] px-4 py-3">
              <p class="text-sm font-semibold text-white">{{ item.code }}</p>
              <p class="mt-1 text-xs text-[#8b949e]">{{ item.hint }}</p>
            </article>
          </div>
          <p class="mt-3 text-sm leading-relaxed text-[#c9d1d9]">
            Konten yang ditolak kembali ke draf, diperbaiki, lalu diajukan lagi. Yang sudah disetujui baru boleh di-blast, dan setelah terkirim statusnya menjadi Terbit.
          </p>
        </section>

        <section v-show="isVisible('opd')" id="opd" class="scroll-mt-4 rounded-2xl border border-[#30363d] bg-[#161b22] p-5">
          <h2 class="text-base font-semibold text-white">Validasi OPD</h2>
          <ol class="mt-4 space-y-2">
            <li class="rounded-xl border border-[#30363d] bg-[#0d1117] px-4 py-3 text-sm text-[#c9d1d9]">Editor atau Super Admin memilih OPD dan mengirim permintaan. Status validasi: menunggu. Isu pindah dari Terbuka ke Validasi.</li>
            <li class="rounded-xl border border-[#30363d] bg-[#0d1117] px-4 py-3 text-sm text-[#c9d1d9]">Admin OPD membuka menu Validasi OPD, mengisi data pendukung, lalu memilih tervalidasi atau ditolak.</li>
            <li class="rounded-xl border border-[#30363d] bg-[#0d1117] px-4 py-3 text-sm text-[#c9d1d9]">Minimal satu jawaban tervalidasi menggeser isu ke Produksi, dan Editor lanjut ke Hub Konten. Bukti dari Mata Bathin ada di detail isu.</li>
          </ol>
        </section>

        <section v-show="isVisible('sebar')" id="sebar" class="scroll-mt-4 rounded-2xl border border-[#30363d] bg-[#161b22] p-5">
          <h2 class="text-base font-semibold text-white">Diseminasi paralel</h2>
          <p class="mt-1 text-sm text-[#8b949e]">Setelah konten disetujui, tiga jalur ini bisa berjalan bersamaan.</p>
          <div class="mt-4 grid gap-3 lg:grid-cols-3">
            <article class="rounded-xl border border-[#30363d] bg-[#0d1117] p-4">
              <p class="text-sm font-semibold text-white">Media mitra</p>
              <p class="mt-2 text-sm leading-relaxed text-[#c9d1d9]">Kirim lewat WhatsApp, email, atau keduanya. Hasil tercatat terkirim, sebagian, atau gagal. Isu menjadi Telah disebar, lalu waktu tayang dicatat untuk SLA.</p>
            </article>
            <article class="rounded-xl border border-[#30363d] bg-[#0d1117] p-4">
              <p class="text-sm font-semibold text-white">ASN</p>
              <p class="mt-2 text-sm leading-relaxed text-[#c9d1d9]">Admin membuat misi like, share, atau komentar. ASN mengerjakan dan mengisi bukti. Partisipasi direkap per OPD.</p>
            </article>
            <article class="rounded-xl border border-[#30363d] bg-[#0d1117] p-4">
              <p class="text-sm font-semibold text-white">Influencer</p>
              <p class="mt-2 text-sm leading-relaxed text-[#c9d1d9]">Campaign mencatat tautan tayangan, jadwal, interaksi, dan anggaran sampai konten terbit.</p>
            </article>
          </div>
        </section>

        <section v-show="isVisible('agenda')" id="agenda" class="scroll-mt-4 rounded-2xl border border-[#30363d] bg-[#161b22] p-5">
          <h2 class="text-base font-semibold text-white">Agenda proaktif</h2>
          <p class="mt-2 text-sm leading-relaxed text-[#c9d1d9]">
            Jalur ini bukan reaksi krisis. Ini kalender konten positif yang direncanakan bulanan: direncanakan, produksi, siap tayang, lalu terbit. Agenda bisa dibatalkan, dan tetap jalan meski deteksi otomatis sedang tidak aktif.
          </p>
          <RouterLink to="/agenda" class="mt-3 inline-block text-xs font-semibold text-emerald-300 hover:text-emerald-200">Buka Agenda</RouterLink>
        </section>

        <section v-show="isVisible('umpan')" id="umpan" class="scroll-mt-4 rounded-2xl border border-[#30363d] bg-[#161b22] p-5">
          <h2 class="text-base font-semibold text-white">Umpan balik ke Mata Bathin</h2>
          <ol class="mt-4 space-y-2 text-sm text-[#c9d1d9]">
            <li class="rounded-xl border border-[#30363d] bg-[#0d1117] px-4 py-3">Mata Bathin mengirim alert, brief, dan bukti.</li>
            <li class="rounded-xl border border-[#30363d] bg-[#0d1117] px-4 py-3">SIAGAPIM membuka Crisis Room dan alert bila risiko R3 ke atas.</li>
            <li class="rounded-xl border border-[#30363d] bg-[#0d1117] px-4 py-3">OPD menjawab validasi, konten disetujui, media mitra menerima blast dan tayang.</li>
            <li class="rounded-xl border border-[#30363d] bg-[#0d1117] px-4 py-3">Saat isu Telah disebar atau Ditutup, SIAGAPIM mengirim balik tindakan, hasil OPD, respons media, dan hasil akhir.</li>
          </ol>
        </section>

        <section v-show="isVisible('pilar')" id="pilar" class="scroll-mt-4 rounded-2xl border border-[#30363d] bg-[#161b22] p-5">
          <h2 class="text-base font-semibold text-white">Tiga pilar</h2>
          <div class="mt-4 grid gap-3 lg:grid-cols-3">
            <article v-for="pillar in pillars" :key="pillar.title" class="rounded-xl border border-[#30363d] bg-[#0d1117] p-4">
              <p class="text-sm font-semibold text-white">{{ pillar.title }}</p>
              <ul class="mt-3 space-y-1.5">
                <li v-for="item in pillar.items" :key="item" class="text-sm text-[#c9d1d9]">{{ item }}</li>
              </ul>
            </article>
          </div>
          <p class="mt-3 text-sm text-[#8b949e]">Penunjang: pengguna dan peran, Master OPD, serta laporan PDF dan Excel.</p>
        </section>

        <section v-show="isVisible('cek')" id="cek" class="scroll-mt-4 rounded-2xl border border-[#30363d] bg-[#161b22] p-5">
          <h2 class="text-base font-semibold text-white">Checklist operasional</h2>
          <ol class="mt-4 space-y-2">
            <li
              v-for="(item, index) in checklist"
              :key="item"
              class="flex gap-3 rounded-xl border border-[#30363d] bg-[#0d1117] px-4 py-3"
            >
              <span class="text-xs font-semibold text-emerald-300">{{ index + 1 }}</span>
              <p class="text-sm leading-relaxed text-[#c9d1d9]">{{ item }}</p>
            </li>
          </ol>
        </section>
      </div>
    </div>
  </div>
</template>
