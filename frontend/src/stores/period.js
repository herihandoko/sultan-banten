import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

const PERIOD_KEY = 'sb_period'

/** @typedef {'TODAY' | '3D' | '7D' | '30D'} PeriodValue */

const PERIODS = [
  { value: 'TODAY', label: 'Hari Ini', days: 1 },
  { value: '3D', label: '3 Hari Terakhir', days: 3 },
  { value: '7D', label: '7 Hari Terakhir', days: 7 },
  { value: '30D', label: '1 Bln Terakhir', days: 30 },
]

function loadInitial() {
  const saved = localStorage.getItem(PERIOD_KEY)
  if (PERIODS.some((p) => p.value === saved)) return /** @type {PeriodValue} */ (saved)
  return '3D'
}

function formatJakartaDate(date) {
  return date.toLocaleDateString('id-ID', {
    timeZone: 'Asia/Jakarta',
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

function rangeStart(days, now = new Date()) {
  const start = new Date(now)
  if (days <= 1) return start
  start.setDate(start.getDate() - (days - 1))
  return start
}

export const usePeriodStore = defineStore('period', () => {
  /** @type {import('vue').Ref<PeriodValue>} */
  const period = ref(loadInitial())

  const options = computed(() => {
    const now = new Date()
    return PERIODS.map((p) => ({
      ...p,
      periodText: `${formatJakartaDate(rangeStart(p.days, now))} — ${formatJakartaDate(now)}`,
    }))
  })

  const selected = computed(
    () => options.value.find((p) => p.value === period.value) || options.value[1],
  )

  const label = computed(() => selected.value?.label || '3 Hari Terakhir')
  const days = computed(() => selected.value?.days ?? 3)

  /**
   * @param {PeriodValue} value
   */
  function setPeriod(value) {
    if (!PERIODS.some((p) => p.value === value)) return
    period.value = value
    localStorage.setItem(PERIOD_KEY, value)
  }

  return {
    period,
    options,
    selected,
    label,
    days,
    setPeriod,
  }
})
