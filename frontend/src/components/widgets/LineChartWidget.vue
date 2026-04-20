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

function buildOption(data) {
  if (!data?.series) return {}
  const cfg = props.definition.displayConfig || {}

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
    },
    legend: {
      show: cfg.showLegend ?? true,
      bottom: 0,
      textStyle: { color: '#6b7399' },
    },
    grid: { top: 20, left: 50, right: 20, bottom: 40 },
    xAxis: {
      type: 'category',
      data: data.series[0]?.data.map(p => p.x) || [],
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
      nameTextStyle: { color: '#6b7399' },
    },
    series: data.series.map((s, i) => ({
      name: s.name,
      type: 'line',
      smooth: true,
      data: s.data.map(p => p.y),
      symbol: 'circle',
      symbolSize: 5,
      lineStyle: { width: 2.5 },
      itemStyle: { color: (cfg.colors || ['#5470c6', '#91cc75'])[i] },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: ((cfg.colors || ['#5470c6', '#91cc75'])[i]) + '33' },
            { offset: 1, color: 'transparent' },
          ],
        },
      },
    })),
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
