<script setup>
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const query = ref('')
const activeId = ref('apa')

const sections = [
  {
    id: 'apa',
    title: 'Apa itu SIAGAPIM',
    roles: 'Semua peran',
    paragraphs: [
      'SIAGAPIM (Sistem Informasi Analisis Gema Aktual Pimpinan) memantau berita dan isu yang menyangkut pimpinan setiap hari, lalu menjalankan respons: validasi OPD, konten klarifikasi, sebar media, amplifikasi ASN dan KOL, serta laporan.',
    ],
    rows: [
      ['Mata Bathin', 'Deteksi isu, sentimen, dan peringatan dini'],
      ['SIAGAPIM', 'Pantauan harian, validasi, konten, blast, ASN, KOL, dan laporan'],
    ],
  },
  {
    id: 'masuk',
    title: 'Masuk, menu, dan keluar',
    roles: 'Semua peran',
    steps: [
      'Isi username dan password, lalu klik Masuk. Menu di kiri mengikuti peran akun.',
      'Di desktop, sidebar bisa diciutkan. Saat ciut, arahkan kursor ke ikon untuk melihat nama menu. Di layar sempit, menu menjadi laci.',
      'Lonceng di kanan atas berisi isu R3 ke atas atau respons yang terlambat. Footer menampilkan nama aplikasi dan versi.',
      'Untuk keluar, buka menu nama di kanan atas lalu pilih Keluar. Jangan bagikan akun pimpinan atau Super Admin, dan keluar setelah selesai di perangkat bersama.',
    ],
  },
  {
    id: 'peran',
    title: 'Menu per peran',
    roles: 'Semua peran',
    note: 'Tanda centang berarti menu itu tampil untuk peran tersebut. Admin Media hanya mengunduh laporan SLA dan KOL.',
    matrix: {
      headers: ['Menu', 'Super Admin', 'Editor', 'Pimpinan', 'OPD', 'Media', 'ASN'],
      rows: [
        ['Dashboard', '✓', '✓', '✓', '✓', '✓', '✓'],
        ['Eksekutif', '✓', '—', '✓', '—', '—', '—'],
        ['Crisis Room', '✓', '✓', '✓', '✓', '—', '—'],
        ['Validasi OPD', '✓', '✓', '✓', '✓', '—', '—'],
        ['Hub Konten', '✓', '✓', '✓', '—', '—', '—'],
        ['Media Hub', '✓', '✓', '✓', '—', '✓', '—'],
        ['Agenda', '✓', '✓', '✓', '—', '✓', '—'],
        ['Mission Board', '✓', '✓', '✓', '—', '—', '✓'],
        ['Influencer', '✓', '—', '—', '—', '✓', '—'],
        ['Arsip', '✓', '✓', '✓', '—', '✓', '—'],
        ['Laporan', '✓', '✓', '✓', '—', '✓', '—'],
        ['Proses Bisnis', '✓', '✓', '✓', '✓', '✓', '✓'],
        ['Tutorial', '✓', '✓', '✓', '✓', '✓', '✓'],
        ['Pengaturan', '✓', '✓', '—', '—', '—', '—'],
        ['Master OPD', '✓', '—', '—', '—', '—', '—'],
        ['Users', '✓', '—', '—', '—', '—', '—'],
      ],
    },
  },
  {
    id: 'dashboard',
    title: 'Dashboard',
    roles: 'Semua peran',
    steps: [
      'Super Admin dan Editor melihat total mention, sentimen negatif, jangkauan, isu aktif, tren 7 hari, isu yang perlu perhatian, antrean kerja, dan sebaran kanal.',
      'Pimpinan melihat ringkasan isu prioritas. Admin OPD melihat validasi yang menunggu. ASN melihat misi yang bisa diikuti.',
      'Angka percakapan dihitung dari 7 hari terakhir. Bila belum ada mention pada jendela itu, kartu dan chart berada di nol sementara isu Crisis Room tetap tampil.',
      'Ganti periode di bagian atas bila angka perlu disaring.',
    ],
  },
  {
    id: 'crisis',
    title: 'Crisis Room',
    roles: 'Super Admin, Editor, Pimpinan, OPD',
    steps: [
      'Daftar isu menampilkan judul, risiko R0–R5, status, dan sumber. Klik kartu untuk membuka detail.',
      'Di detail tersedia bukti, permintaan validasi, konten terkait, dan perubahan status sesuai wewenang.',
      'Editor atau Super Admin menambah isu manual lewat Input Isu bila sumber otomatis belum menangkap berita: judul, ringkasan, alasan kenapa sekarang, dan tingkat risiko.',
    ],
    rows: [
      ['Terbuka', 'Baru masuk, perlu ditindak'],
      ['Validasi', 'Klarifikasi OPD sedang diminta'],
      ['Produksi', 'Konten klarifikasi disusun'],
      ['Disetujui', 'Konten sudah disetujui'],
      ['Telah disebar', 'Sudah dikirim ke kanal'],
      ['Ditutup', 'Penanganan selesai'],
      ['R0–R1', 'Informasi, cukup dipantau'],
      ['R2', 'Perlu diawasi'],
      ['R3', 'Naik, biasanya memicu alert'],
      ['R4–R5', 'Tinggi sampai kritis'],
    ],
  },
  {
    id: 'alert',
    title: 'Alert lonceng',
    roles: 'Super Admin, Editor, Pimpinan, Media',
    steps: [
      'Muncul untuk isu R3 ke atas atau respons yang terlambat.',
      'Klik lonceng, pilih alert, lalu buka isu terkait.',
      'Izinkan notifikasi browser bila ingin pengingat muncul di desktop.',
    ],
  },
  {
    id: 'validasi',
    title: 'Validasi OPD',
    roles: 'Editor meminta, OPD menjawab',
    groups: [
      {
        title: 'Meminta',
        steps: [
          'Dari detail isu, buat permintaan validasi.',
          'Pilih OPD dan isi catatan.',
          'Status isu menjadi Validasi.',
        ],
      },
      {
        title: 'Menjawab',
        steps: [
          'Buka menu Validasi OPD.',
          'Pilih permintaan yang menunggu.',
          'Isi catatan atau data pendukung, lalu pilih tervalidasi atau ditolak.',
        ],
      },
    ],
    paragraphs: ['Bila ada jawaban tervalidasi, isu biasanya lanjut ke Produksi.'],
  },
  {
    id: 'konten',
    title: 'Hub Konten',
    roles: 'Editor, Pimpinan, Super Admin',
    groups: [
      {
        title: 'Menyusun',
        steps: [
          'Buat konten baru dan pilih Rilis Teks, Infografis, atau Video. Isi form mengikuti jenisnya.',
          'Hubungkan ke isu. Narasi dari sumber intelijen bisa dipakai sebagai acuan.',
          'Simpan draf, lalu ajukan review.',
        ],
      },
      {
        title: 'Menyetujui',
        steps: [
          'Buka konten yang menunggu persetujuan.',
          'Setujui, atau tolak beserta catatan.',
          'Konten yang disetujui siap disebar.',
        ],
      },
    ],
  },
  {
    id: 'media',
    title: 'Media Hub',
    roles: 'Editor, Super Admin, Media & KOL',
    groups: [
      {
        title: 'Media mitra',
        steps: ['Tambah atau ubah nama, pimpinan redaksi, WhatsApp, email, cakupan, dan kanal krisis.', 'Nonaktifkan mitra yang tidak dipakai.'],
      },
      {
        title: 'Media blast',
        steps: ['Pilih konten yang sudah disetujui atau terbit.', 'Pilih mitra dan kanal: WhatsApp, email, atau keduanya.', 'Kirim. Hasil tercatat terkirim, sebagian, atau gagal.'],
      },
      {
        title: 'SLA 60 menit',
        steps: ['Catat waktu tayang rilis.', 'Sistem menghitung menit respons dan kepatuhan.', 'Lihat peringkat kepatuhan media.'],
      },
    ],
  },
  {
    id: 'agenda',
    title: 'Agenda',
    roles: 'Editor, Pimpinan, Media & KOL',
    paragraphs: ['Kalender konten positif: pembangunan, penghargaan, sosial, ekonomi, dan tema lain yang direncanakan, bukan hanya reaksi krisis.'],
    steps: [
      'Pilih bulan dengan panah.',
      'Tambah agenda: judul, tanggal, tema, kanal, dan target media.',
      'Perbarui status dari direncanakan, produksi, siap tayang, sampai terbit, atau batalkan.',
    ],
  },
  {
    id: 'misi',
    title: 'Mission Board',
    roles: 'Admin membuat, ASN mengikuti',
    groups: [
      {
        title: 'Membuat misi',
        steps: ['Isi judul, instruksi, tautan unggahan resmi, dan jenis aksi: like, share, atau komentar.', 'Tentukan target partisipasi. Tautan ke isu bersifat opsional.', 'Simpan. Status misi menjadi aktif.'],
      },
      {
        title: 'Mengikuti misi',
        steps: ['Buka misi aktif, lalu buka tautannya dan lakukan aksi di media sosial.', 'Tandai ikut serta dan isi bukti URL atau catatan bila diminta.'],
      },
    ],
    paragraphs: ['Rekap partisipasi per OPD dipakai untuk pelaporan.'],
  },
  {
    id: 'kol',
    title: 'Influencer',
    roles: 'Super Admin, Media & KOL',
    steps: [
      'Menu Influencer membuka direktori KOL: nama, platform, akun, pengikut, engagement, topik, dan status kontrak.',
      'Campaign mencatat tautan tayangan, jadwal, tayangan, suka, komentar, anggaran, dan status sampai terbit.',
    ],
  },
  {
    id: 'arsip',
    title: 'Arsip',
    roles: 'Super Admin, Editor, Pimpinan, Media',
    steps: [
      'Cari histori isu dan konten dengan kata kunci, status, risiko, atau tanggal.',
      'Buka timeline: isu, validasi, konten, lalu blast.',
    ],
  },
  {
    id: 'laporan',
    title: 'Eksekutif dan laporan',
    roles: 'Sesuai peran',
    paragraphs: ['Halaman Eksekutif merangkum brief, isu aktif, validasi menunggu, blast, partisipasi ASN, jangkauan KOL, sebaran risiko, pipeline konten, dan isu prioritas R3 ke atas.'],
    rows: [
      ['Penanganan krisis', 'Isu, risiko, status, validasi, konten, dan blast'],
      ['SLA media', 'Log kepatuhan dan ringkasannya'],
      ['Rekap ASN', 'Partisipasi per OPD dan daftar misi'],
      ['Kinerja KOL', 'Campaign dan metriknya'],
      ['Executive brief', 'Angka utama dan rekomendasi ringkas'],
    ],
    steps: ['Pilih jenis laporan.', 'Untuk laporan krisis, ID isu bisa diisi bila ingin satu isu saja.', 'Unduh PDF atau Excel.'],
  },
  {
    id: 'admin',
    title: 'Pengaturan dan pengguna',
    roles: 'Super Admin',
    steps: [
      'Pengaturan mengatur sumber berita serta kanal WhatsApp dan email. Editor juga dapat membuka halaman ini.',
      'Master OPD dipakai saat menugaskan validasi.',
      'Users menambah akun (username, nama, email, password, peran, dan OPD bila Admin OPD), mengubah data, dan menonaktifkan pengguna selain akun sendiri.',
    ],
  },
  {
    id: 'latihan',
    title: 'Contoh penanganan',
    roles: 'Latihan bersama',
    groups: [
      {
        title: 'Satu isu sampai laporan',
        steps: [
          'Pastikan isu ada di Crisis Room, atau masukkan secara manual.',
          'Minta validasi, lalu Admin OPD menjawab tervalidasi.',
          'Editor menyusun naskah dan mengajukan review. Pimpinan menyetujui.',
          'Sebar lewat Media Hub. Opsional: misi ASN dan campaign KOL.',
          'Tutup isu, atau tinjau hasilnya di Arsip dan Laporan.',
        ],
      },
      {
        title: 'Amplifikasi ASN',
        steps: ['Admin membuat misi di Mission Board.', 'ASN membuka misi, melakukan aksi, lalu mengisi bukti.'],
      },
      {
        title: 'Konten positif rutin',
        steps: ['Rencanakan agenda bulanan.', 'Produksi naskah di Hub Konten atau kirim ke media sesuai jadwal.'],
      },
    ],
  },
  {
    id: 'tips',
    title: 'Jika sesuatu tidak jalan',
    roles: 'Semua peran',
    rows: [
      ['Menu tidak muncul', 'Peran akun memang tidak memiliki menu itu. Lihat tabel menu per peran.'],
      ['Tidak bisa masuk', 'Periksa username dan password, lalu coba lagi.'],
      ['Lonceng kosong', 'Alert muncul bila ada isu R3 ke atas atau respons terlambat. Izinkan notifikasi browser.'],
      ['Blast tercatat, pesan tidak masuk', 'Pastikan kanal WhatsApp dan email di Pengaturan sudah terhubung ke gateway resmi.'],
      ['Angka dashboard nol', 'Chart menghitung mention 7 hari terakhir. Isu di Crisis Room tetap bisa dikerjakan.'],
      ['Unduh laporan gagal', 'Masuk ulang, lalu coba lagi dengan peran yang diizinkan.'],
      ['Layar sempit', 'Buka menu dari ikon di header. Sidebar menjadi laci.'],
    ],
  },
]

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return sections
  return sections.filter((section) => {
    const bits = [
      section.title,
      section.roles,
      ...(section.paragraphs || []),
      ...(section.steps || []),
      ...(section.rows || []).flat(),
      ...(section.groups || []).flatMap((group) => [group.title, ...group.steps]),
      ...(section.matrix ? section.matrix.rows.flat() : []),
    ]
    return bits.join(' ').toLowerCase().includes(q)
  })
})

const roleLabel = computed(() => auth.user?.role?.name || 'pengguna')

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
        <h1 class="mt-1 text-2xl font-semibold tracking-tight text-white">Tutorial</h1>
        <p class="mt-1 max-w-2xl text-sm text-[#8b949e]">
          Panduan pemakaian SIAGAPIM v0.2.0 untuk Biro Adpim. Anda masuk sebagai {{ roleLabel }}.
        </p>
      </div>
      <RouterLink
        to="/proses-bisnis"
        class="rounded-xl border border-[#30363d] bg-[#161b22] px-3 py-1.5 text-xs font-semibold text-emerald-300 hover:border-emerald-500/40"
      >
        Lihat proses bisnis
      </RouterLink>
    </div>

    <div class="grid items-start gap-4 lg:grid-cols-[16rem_minmax(0,1fr)]">
      <aside class="rounded-2xl border border-[#30363d] bg-[#161b22] p-3 lg:sticky lg:top-4">
        <label class="block px-2 pb-2">
          <span class="sr-only">Cari topik</span>
          <input
            v-model="query"
            type="search"
            placeholder="Cari topik"
            class="w-full rounded-lg border border-[#30363d] bg-[#0d1117] px-3 py-2 text-sm text-[#e6edf3] outline-none placeholder:text-[#6e7681] focus:border-emerald-500/50"
          />
        </label>
        <nav class="flex gap-2 overflow-x-auto lg:flex-col lg:overflow-visible">
          <button
            v-for="section in filtered"
            :key="section.id"
            type="button"
            class="shrink-0 rounded-lg px-3 py-2 text-left text-xs font-semibold transition"
            :class="activeId === section.id ? 'bg-[#2b3544] text-white' : 'text-[#8b949e] hover:bg-[#21262d] hover:text-white'"
            @click="show(section.id)"
          >
            {{ section.title }}
          </button>
          <p v-if="!filtered.length" class="px-3 py-4 text-xs text-[#8b949e]">Tidak ada topik yang cocok.</p>
        </nav>
      </aside>

      <div class="space-y-3">
        <article
          v-for="section in filtered"
          :id="section.id"
          :key="section.id"
          class="scroll-mt-4 rounded-2xl border border-[#30363d] bg-[#161b22] p-5"
        >
          <div class="flex flex-wrap items-center justify-between gap-2">
            <h2 class="text-base font-semibold text-white">{{ section.title }}</h2>
            <span class="rounded-md border border-[#30363d] bg-[#0d1117] px-2 py-0.5 text-[11px] text-[#8b949e]">
              {{ section.roles }}
            </span>
          </div>

          <p v-for="paragraph in section.paragraphs || []" :key="paragraph" class="mt-3 text-sm leading-relaxed text-[#c9d1d9]">
            {{ paragraph }}
          </p>
          <p v-if="section.note" class="mt-3 text-sm leading-relaxed text-[#8b949e]">{{ section.note }}</p>

          <div v-if="section.matrix" class="mt-4 overflow-x-auto rounded-xl border border-[#30363d]">
            <table class="min-w-full text-left text-xs">
              <thead class="bg-[#0d1117] text-[#8b949e]">
                <tr>
                  <th v-for="header in section.matrix.headers" :key="header" class="px-3 py-2 font-semibold">{{ header }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in section.matrix.rows" :key="row[0]" class="border-t border-[#30363d]">
                  <td v-for="(cell, index) in row" :key="index" class="px-3 py-2" :class="index === 0 ? 'font-semibold text-white' : 'text-center text-[#c9d1d9]'">
                    {{ cell }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="section.rows?.length" class="mt-4 overflow-hidden rounded-xl border border-[#30363d]">
            <div
              v-for="row in section.rows"
              :key="row[0]"
              class="grid gap-1 border-t border-[#30363d] bg-[#0d1117] px-4 py-3 first:border-t-0 sm:grid-cols-[11rem_minmax(0,1fr)] sm:items-center"
            >
              <p class="text-sm font-semibold text-white">{{ row[0] }}</p>
              <p class="text-sm text-[#c9d1d9]">{{ row[1] }}</p>
            </div>
          </div>

          <ol v-if="section.steps?.length" class="mt-4 space-y-2">
            <li
              v-for="(step, index) in section.steps"
              :key="step"
              class="flex gap-3 rounded-xl border border-[#30363d] bg-[#0d1117] px-4 py-3"
            >
              <span class="text-xs font-semibold text-emerald-300">{{ index + 1 }}</span>
              <p class="text-sm leading-relaxed text-[#c9d1d9]">{{ step }}</p>
            </li>
          </ol>

          <div v-for="group in section.groups || []" :key="group.title" class="mt-4">
            <h3 class="text-sm font-semibold text-white">{{ group.title }}</h3>
            <ol class="mt-2 space-y-2">
              <li
                v-for="(step, index) in group.steps"
                :key="step"
                class="flex gap-3 rounded-xl border border-[#30363d] bg-[#0d1117] px-4 py-3"
              >
                <span class="text-xs font-semibold text-emerald-300">{{ index + 1 }}</span>
                <p class="text-sm leading-relaxed text-[#c9d1d9]">{{ step }}</p>
              </li>
            </ol>
          </div>
        </article>
      </div>
    </div>
  </div>
</template>
