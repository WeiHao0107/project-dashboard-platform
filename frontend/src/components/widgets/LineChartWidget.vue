<template>
  <div class="widget-card">
    <div class="widget-header">
      <h3 class="widget-title">{{ definition.title }}</h3>
    </div>
    <div v-if="loading" class="widget-loading">
      <span class="spinner"></span> Loading...
    </div>
    <div v-else-if="error" class="widget-error">{{ error }}</div>
    <div v-else ref="chartEl" class="chart-area"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  definition:  { type: Object,  required: true },
  data:        { type: Object,  default: null },
  loading:     { type: Boolean, default: false },
  error:       { type: String,  default: null },
})

const chartEl = ref(null)
let chart     = null

const COLOR_CREATED  = '#ef4444'   // red
const COLOR_RESOLVED = '#22c55e'   // green
const COLOR_RED_BAND   = 'rgba(239,68,68,0.18)'
const COLOR_GREEN_BAND = 'rgba(34,197,94,0.18)'

function buildOption(data) {
  if (!data?.series) return {}
  const cfg = props.definition.displayConfig || {}

  const xData    = data.series[0]?.data.map(p => p.x) || []
  const cValues  = data.series[0]?.data.map(p => p.y) || []
  const rValues  = data.series[1]?.data.map(p => p.y) || []

  // Compute per-point: floor = min(c,r), red delta, green delta
  const floorVals = cValues.map((c, i) => Math.min(c, rValues[i]))
  const redDelta  = cValues.map((c, i) => Math.max(0, c - rValues[i]))
  const greenDelta = rValues.map((r, i) => Math.max(0, r - cValues[i]))

  // Invisible band series — needed so areaStyle fills from floor up
  const bandBase = (stackName) => ({
    type: 'line', data: floorVals,
    stack: stackName, silent: true, legendHoverLink: false,
    symbol: 'none', lineStyle: { opacity: 0 },
    areaStyle: { color: 'transparent' },
    tooltip: { show: false },
  })

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      // Only show the two real series in tooltip
      formatter(params) {
        const real = params.filter(p => p.seriesName === 'Created' || p.seriesName === 'Resolved')
        if (!real.length) return ''
        let html = `<b>${real[0].axisValue}</b><br/>`
        real.forEach(p => {
          html += `${p.marker} ${p.seriesName}: <b>${p.value}</b><br/>`
        })
        return html
      },
    },
    legend: {
      show: cfg.showLegend ?? true,
      bottom: 0,
      data: ['Created', 'Resolved'],
      textStyle: { color: '#6b7399' },
    },
    grid: { top: 30, left: 55, right: 20, bottom: 45 },
    xAxis: {
      type: 'category',
      data: xData,
      axisLine:  { lineStyle: { color: '#d1d5e0' } },
      axisLabel: { color: '#6b7399', fontSize: 12 },
      name: cfg.xAxisLabel,
      nameTextStyle: { color: '#6b7399' },
    },
    yAxis: {
      type: 'value',
      axisLine:  { show: false },
      splitLine: { lineStyle: { color: '#f0f2f5' } },
      axisLabel: { color: '#6b7399', fontSize: 12 },
      name: cfg.yAxisLabel,
      nameTextStyle: { color: '#6b7399', padding: [0, 0, 0, -10] },
    },
    series: [
      // ── Red band (created > resolved region) ──
      bandBase('red'),
      {
        type: 'line', data: redDelta,
        stack: 'red', silent: true, legendHoverLink: false,
        symbol: 'none', lineStyle: { opacity: 0 },
        areaStyle: { color: COLOR_RED_BAND },
        tooltip: { show: false },
      },
      // ── Green band (resolved > created region) ──
      bandBase('green'),
      {
        type: 'line', data: greenDelta,
        stack: 'green', silent: true, legendHoverLink: false,
        symbol: 'none', lineStyle: { opacity: 0 },
        areaStyle: { color: COLOR_GREEN_BAND },
        tooltip: { show: false },
      },
      // ── Created line (red) ──
      {
        name: 'Created',
        type: 'line',
        data: cValues,
        smooth: true,
        symbol: 'circle', symbolSize: 5,
        lineStyle: { color: COLOR_CREATED, width: 2.5 },
        itemStyle: { color: COLOR_CREATED },
      },
      // ── Resolved line (green) ──
      {
        name: 'Resolved',
        type: 'line',
        data: rValues,
        smooth: true,
        symbol: 'circle', symbolSize: 5,
        lineStyle: { color: COLOR_RESOLVED, width: 2.5 },
        itemStyle: { color: COLOR_RESOLVED },
      },
    ],
  }
}

function initChart() {
  if (!chartEl.value) return
  chart = echarts.init(chartEl.value)
  if (props.data) chart.setOption(buildOption(props.data))
}

const resizeObserver = new ResizeObserver(() => chart?.resize())

onMounted(async () => {
  await nextTick()
  initChart()
  if (chartEl.value) resizeObserver.observe(chartEl.value)
})

onBeforeUnmount(() => {
  resizeObserver.disconnect()
  chart?.dispose()
})

watch(() => props.data, async (val) => {
  await nextTick()
  if (!chart) initChart()
  if (chart && val) chart.setOption(buildOption(val), true)
})
</script>

<style scoped>
.widget-card {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  padding: 20px;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.widget-header { margin-bottom: 12px; }

.widget-title {
  font-size: 14px;
  font-weight: 600;
  color: #2d3460;
}

.chart-area {
  flex: 1;
  min-height: 320px;
}

.widget-loading {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #6b7399;
  font-size: 14px;
}

.widget-error {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #e57373;
  font-size: 13px;
}

.spinner {
  width: 18px; height: 18px;
  border: 2px solid #e8eaf6;
  border-top-color: #7986cb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  display: inline-block;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
