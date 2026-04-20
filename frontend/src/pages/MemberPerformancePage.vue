<template>
  <div class="page">
    <!-- Header -->
    <div class="page-header">
      <h2 class="page-title">👥 Member Performance</h2>
      <p class="page-desc">Monthly issues resolved per team member</p>
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

    <!-- Table -->
    <div class="page-body">
      <div class="card">
        <div class="card-header">
          <span class="card-title">Issues Handled Per Member (Monthly)</span>
          <span v-if="data" class="card-meta">{{ data.meta?.totalRows }} members</span>
        </div>

        <div v-if="loading" class="state-center">
          <span class="spinner" /> Loading...
        </div>
        <div v-else-if="error" class="state-center state-error">{{ error }}</div>

        <div v-else-if="data" class="table-wrap">
          <table>
            <thead>
              <tr>
                <th v-for="col in data.columns" :key="col.key"
                    :class="{ 'th-center': col.type === 'number' }">
                  {{ col.label }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, i) in data.rows" :key="i">
                <td v-for="col in data.columns" :key="col.key"
                    :class="{ 'td-center': col.type === 'number', 'td-total': col.key === 'total' }">
                  <template v-if="col.type === 'number'">
                    <span v-if="row[col.key] > 0" class="badge" :style="heatStyle(row[col.key])">
                      {{ row[col.key] }}
                    </span>
                    <span v-else class="zero">—</span>
                  </template>
                  <template v-else>{{ row[col.key] }}</template>
                </td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <td class="foot-label">Total</td>
                <td></td>
                <td v-for="mk in monthCols" :key="mk" class="td-center">
                  <b>{{ colSum(mk) }}</b>
                </td>
                <td class="td-center td-total"><b>{{ grandTotal }}</b></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { api } from '../api/index.js'

const props = defineProps({
  projectKey: { type: String, required: true },
})

// ── Filters ──────────────────────────────────────────────
const ALL_MONTHS   = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
const currentYear  = new Date().getFullYear()
const yearOptions  = Array.from({ length: 5 }, (_, i) => currentYear - i)
const year         = ref(currentYear)
const departmentId = ref(null)
const departments  = ref([])

async function loadDepartments() {
  try { departments.value = (await api.getDepartments(props.projectKey)).data }
  catch { departments.value = [] }
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
      dataSource: 'member_monthly_summary',
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

// ── Table helpers ─────────────────────────────────────────
const monthCols = computed(() =>
  ALL_MONTHS.filter(m => data.value?.columns?.some(c => c.key === m))
)

const maxVal = computed(() => {
  if (!data.value?.rows) return 1
  let m = 0
  for (const r of data.value.rows)
    for (const mk of monthCols.value)
      if (r[mk] > m) m = r[mk]
  return m || 1
})

function heatStyle(val) {
  const pct = val / maxVal.value
  const alpha = 0.12 + pct * 0.55
  return { background: `rgba(89,120,204,${alpha.toFixed(2)})`, color: pct > 0.5 ? '#fff' : '#2d3460' }
}

const colSum = (mk) => data.value?.rows?.reduce((s, r) => s + (r[mk] || 0), 0) ?? 0
const grandTotal = computed(() => data.value?.rows?.reduce((s, r) => s + (r.total || 0), 0) ?? 0)
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
  background: #fff; font-size: 13px; color: #1a1a2e; cursor: pointer; min-width: 150px;
  outline: none; transition: border-color 0.15s;
}
.filter-select:focus { border-color: #7986cb; }

/* Body */
.page-body { padding: 20px 24px; }
.card {
  background: #fff; border-radius: 10px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08); padding: 20px;
}
.card-header {
  display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 14px;
}
.card-title { font-size: 14px; font-weight: 600; color: #2d3460; }
.card-meta  { font-size: 12px; color: #9fa8da; }

/* Table */
.table-wrap { overflow-x: auto; max-height: 540px; overflow-y: auto; }

table { width: 100%; border-collapse: collapse; font-size: 13px; }

thead th {
  position: sticky; top: 0; z-index: 1;
  background: #f5f6fb; padding: 8px 10px;
  text-align: left; font-size: 11px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.5px; color: #6b7399;
  white-space: nowrap; border-bottom: 2px solid #e8eaf6;
}
.th-center { text-align: center; min-width: 52px; }

tbody tr:hover { background: #f8f9fe; }
tbody td { padding: 7px 10px; border-bottom: 1px solid #f0f2f5; white-space: nowrap; color: #2d3460; }
.td-center { text-align: center; }
.td-total  { font-weight: 700; }

.badge {
  display: inline-block; padding: 2px 8px; border-radius: 4px;
  font-size: 12px; font-weight: 600; min-width: 28px; text-align: center;
}
.zero { color: #c5cae9; }

tfoot td {
  background: #f0f2fb; border-top: 2px solid #e8eaf6;
  padding: 7px 10px; font-size: 12.5px; color: #2d3460;
}
.foot-label { color: #6b7399; font-weight: 700; }

/* States */
.state-center {
  height: 200px; display: flex; align-items: center;
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
