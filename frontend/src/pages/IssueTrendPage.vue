<template>
  <div class="page">
    <!-- Header -->
    <div class="page-header">
      <h2 class="page-title">📈 Issue Trend</h2>
      <p class="page-desc">Cumulative created vs resolved issues over time</p>
    </div>

    <!-- Filters -->
    <div class="filter-bar">
      <div class="filter-field">
        <label class="filter-label">YEAR</label>
        <select class="filter-select" v-model="year">
          <option v-for="y in yearOptions" :key="y" :value="y">{{ y }}</option>
        </select>
      </div>
      <div class="filter-field">
        <label class="filter-label">DEPARTMENT</label>
        <select class="filter-select" v-model="departmentId">
          <option :value="null">All Departments</option>
          <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
        </select>
      </div>
    </div>

    <!-- Chart -->
    <div class="page-body">
      <div class="card">
        <div class="card-title">Created vs Resolved Issues (Cumulative)</div>
        <div v-if="loading" class="state-center">
          <span class="spinner" /> Loading...
        </div>
        <div v-else-if="error" class="state-center state-error">{{ error }}</div>
        <div v-else ref="chartEl" class="chart-area" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted, onBeforeUnmount, nextTick, toRef } from 'vue'
import * as echarts from 'echarts'
import { api } from '../api/index.js'

const props = defineProps({
  projectKey: { type: String, required: true },
})

// ── Filters ──────────────────────────────────────────────
const currentYear  = new Date().getFullYear()
const yearOptions  = Array.from({ length: 5 }, (_, i) => currentYear - i)
const year         = ref(currentYear)
const departmentId = ref(null)
const departments  = ref([])

async function loadDepartments() {
  try {
    departments.value = (await api.getDepartments(props.projectKey)).data
  } catch {
    departments.value = []
  }
}

watch(() => props.projectKey, () => {
  departmentId.value = null
  loadDepartments()
}, { immediate: true })

// ── Data fetching ─────────────────────────────────────────
const data    = ref(null)
const loading = ref(false)
const error   = ref(null)

async function fetchData() {
  loading.value = true
  error.value   = null
  try {
    const res = await api.queryData({
      projectKey: props.projectKey,
      dataSource: 'issue_created_resolved_trend',
      filters: { year: year.value, departmentId: departmentId.value },
    })
    data.value = res.data
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

watch([() => props.projectKey, year, departmentId], fetchData, { immediate: true })

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
  const floor   = cValues.map((c, i) => Math.min(c, rValues[i]))
  const redD    = cValues.map((c, i) => Math.max(0, c - rValues[i]))
  const greenD  = rValues.map((r, i) => Math.max(0, r - cValues[i]))

  const bandBase = (stack) => ({
    type: 'line', data: floor, stack, silent: true, legendHoverLink: false,
    symbol: 'none', lineStyle: { opacity: 0 }, areaStyle: { color: 'transparent' },
    tooltip: { show: false },
  })

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      formatter(params) {
        const real = params.filter(p => ['Created','Resolved'].includes(p.seriesName))
        if (!real.length) return ''
        let html = `<b>${real[0].axisValue}</b><br/>`
        real.forEach(p => { html += `${p.marker} ${p.seriesName}: <b>${p.value}</b><br/>` })
        return html
      },
    },
    legend: { bottom: 0, data: ['Created','Resolved'], textStyle: { color: '#6b7399' } },
    grid:   { top: 20, left: 55, right: 20, bottom: 45 },
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
      name: 'Cumulative Count', nameTextStyle: { color: '#6b7399' },
    },
    series: [
      bandBase('red'),
      { type: 'line', data: redD,   stack: 'red',   silent: true, legendHoverLink: false,
        symbol: 'none', lineStyle: { opacity: 0 }, areaStyle: { color: COLOR_RED_BAND },   tooltip: { show: false } },
      bandBase('green'),
      { type: 'line', data: greenD, stack: 'green', silent: true, legendHoverLink: false,
        symbol: 'none', lineStyle: { opacity: 0 }, areaStyle: { color: COLOR_GREEN_BAND }, tooltip: { show: false } },
      { name: 'Created',  type: 'line', data: cValues, smooth: true,
        symbol: 'circle', symbolSize: 5,
        lineStyle: { color: COLOR_CREATED,  width: 2.5 }, itemStyle: { color: COLOR_CREATED } },
      { name: 'Resolved', type: 'line', data: rValues, smooth: true,
        symbol: 'circle', symbolSize: 5,
        lineStyle: { color: COLOR_RESOLVED, width: 2.5 }, itemStyle: { color: COLOR_RESOLVED } },
    ],
  }
}

const ro = new ResizeObserver(() => chart?.resize())

onMounted(async () => {
  await nextTick()
  if (chartEl.value) { chart = echarts.init(chartEl.value); ro.observe(chartEl.value) }
})
onBeforeUnmount(() => { ro.disconnect(); chart?.dispose() })

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

/* Filter bar */
.filter-bar {
  display: flex; gap: 16px; flex-wrap: wrap; align-items: flex-end;
  background: #fff; border-bottom: 1px solid #e8eaf6; padding: 10px 24px;
}
.filter-field { display: flex; flex-direction: column; gap: 4px; }
.filter-label {
  font-size: 10px; font-weight: 700; letter-spacing: 1px;
  text-transform: uppercase; color: #6b7399;
}
.filter-select {
  padding: 6px 10px; border: 1px solid #d1d5e0; border-radius: 6px;
  background: #fff; font-size: 13px; color: #1a1a2e; cursor: pointer; min-width: 130px;
  outline: none; transition: border-color 0.15s;
}
.filter-select:focus { border-color: #7986cb; }

/* Body */
.page-body { padding: 20px 24px; }
.card {
  background: #fff; border-radius: 10px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08); padding: 20px;
}
.card-title { font-size: 14px; font-weight: 600; color: #2d3460; margin-bottom: 12px; }
.chart-area { height: 400px; }

.state-center {
  height: 400px; display: flex; align-items: center;
  justify-content: center; gap: 8px; color: #6b7399; font-size: 14px;
}
.state-error { color: #e57373; }

.spinner {
  width: 18px; height: 18px;
  border: 2px solid #e8eaf6; border-top-color: #7986cb;
  border-radius: 50%; animation: spin 0.8s linear infinite; display: inline-block;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
