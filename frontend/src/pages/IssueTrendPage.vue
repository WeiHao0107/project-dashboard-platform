<template>
  <div class="page">
    <div class="page-header">
      <h2 class="page-title">📈 Issue Trend</h2>
      <p class="page-desc">Cumulative created vs resolved issues over time</p>
    </div>

    <FilterBar
      :available-filters="['year', 'department']"
      :departments="departments"
      v-model="filters"
    />

    <div class="page-body">
      <div class="chart-card">
        <div class="card-title">Created vs Resolved Issues (Cumulative)</div>

        <div v-if="loading" class="state-loading">
          <span class="spinner" /> Loading chart data...
        </div>
        <div v-else-if="error" class="state-error">{{ error }}</div>
        <div v-else ref="chartEl" class="chart-area" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, nextTick, toRef } from 'vue'
import * as echarts from 'echarts'
import FilterBar        from '../components/filter/FilterBar.vue'
import { usePageData }  from '../composables/usePageData.js'
import { useDepartments } from '../composables/useDepartments.js'

const props = defineProps({
  projectKey: { type: String, required: true },
})

const projectKeyRef = toRef(props, 'projectKey')
const filters       = ref({ year: new Date().getFullYear(), departmentId: null })

const { departments }          = useDepartments(projectKeyRef)
const { data, loading, error } = usePageData(projectKeyRef, 'issue_created_resolved_trend', filters)

// ── ECharts ──────────────────────────────────────────────
const chartEl = ref(null)
let chart = null

const COLOR_CREATED    = '#ef4444'
const COLOR_RESOLVED   = '#22c55e'
const COLOR_RED_BAND   = 'rgba(239,68,68,0.18)'
const COLOR_GREEN_BAND = 'rgba(34,197,94,0.18)'

function buildOption(d) {
  const xData   = d.series[0].data.map(p => p.x)
  const cValues = d.series[0].data.map(p => p.y)
  const rValues = d.series[1].data.map(p => p.y)

  const floorVals  = cValues.map((c, i) => Math.min(c, rValues[i]))
  const redDelta   = cValues.map((c, i) => Math.max(0, c - rValues[i]))
  const greenDelta = rValues.map((r, i) => Math.max(0, r - cValues[i]))

  const bandBase = (stackName) => ({
    type: 'line', data: floorVals, stack: stackName,
    silent: true, legendHoverLink: false, symbol: 'none',
    lineStyle: { opacity: 0 }, areaStyle: { color: 'transparent' },
    tooltip: { show: false },
  })

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      formatter(params) {
        const real = params.filter(p => p.seriesName === 'Created' || p.seriesName === 'Resolved')
        if (!real.length) return ''
        let html = `<b>${real[0].axisValue}</b><br/>`
        real.forEach(p => { html += `${p.marker} ${p.seriesName}: <b>${p.value}</b><br/>` })
        return html
      },
    },
    legend: {
      bottom: 0, data: ['Created', 'Resolved'],
      textStyle: { color: '#6b7399' },
    },
    grid: { top: 20, left: 55, right: 20, bottom: 45 },
    xAxis: {
      type: 'category', data: xData,
      axisLine: { lineStyle: { color: '#d1d5e0' } },
      axisLabel: { color: '#6b7399', fontSize: 12 },
    },
    yAxis: {
      type: 'value',
      axisLine:  { show: false },
      splitLine: { lineStyle: { color: '#f0f2f5' } },
      axisLabel: { color: '#6b7399', fontSize: 12 },
      name: 'Cumulative Count',
      nameTextStyle: { color: '#6b7399' },
    },
    series: [
      bandBase('red'),
      { type: 'line', data: redDelta, stack: 'red', silent: true, legendHoverLink: false,
        symbol: 'none', lineStyle: { opacity: 0 }, areaStyle: { color: COLOR_RED_BAND },
        tooltip: { show: false } },
      bandBase('green'),
      { type: 'line', data: greenDelta, stack: 'green', silent: true, legendHoverLink: false,
        symbol: 'none', lineStyle: { opacity: 0 }, areaStyle: { color: COLOR_GREEN_BAND },
        tooltip: { show: false } },
      { name: 'Created',  type: 'line', data: cValues, smooth: true,
        symbol: 'circle', symbolSize: 5,
        lineStyle: { color: COLOR_CREATED,  width: 2.5 },
        itemStyle: { color: COLOR_CREATED } },
      { name: 'Resolved', type: 'line', data: rValues, smooth: true,
        symbol: 'circle', symbolSize: 5,
        lineStyle: { color: COLOR_RESOLVED, width: 2.5 },
        itemStyle: { color: COLOR_RESOLVED } },
    ],
  }
}

const resizeObserver = new ResizeObserver(() => chart?.resize())

onMounted(async () => {
  await nextTick()
  if (chartEl.value) {
    chart = echarts.init(chartEl.value)
    resizeObserver.observe(chartEl.value)
  }
})

onBeforeUnmount(() => {
  resizeObserver.disconnect()
  chart?.dispose()
})

watch(data, async (val) => {
  if (!val?.series) return
  await nextTick()
  if (!chart && chartEl.value) chart = echarts.init(chartEl.value)
  chart?.setOption(buildOption(val), true)
})
</script>

<style scoped>
.page { display: flex; flex-direction: column; height: 100%; background: #f0f2f5; overflow-y: auto; }

.page-header { padding: 20px 24px 0; }
.page-title  { font-size: 20px; font-weight: 700; color: #1a1a2e; }
.page-desc   { font-size: 13px; color: #6b7399; margin-top: 3px; }

.page-body { padding: 20px 24px; }

.chart-card {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  padding: 20px;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  color: #2d3460;
  margin-bottom: 12px;
}

.chart-area { height: 400px; }

.state-loading {
  height: 400px;
  display: flex; align-items: center; justify-content: center;
  gap: 8px; color: #6b7399; font-size: 14px;
}
.state-error {
  height: 400px;
  display: flex; align-items: center; justify-content: center;
  color: #e57373; font-size: 13px;
}

.spinner {
  width: 18px; height: 18px;
  border: 2px solid #e8eaf6; border-top-color: #7986cb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  display: inline-block;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
