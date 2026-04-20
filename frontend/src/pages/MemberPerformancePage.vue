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
        <Select
          v-model="year"
          :options="yearOptions"
          class="filter-select"
        />
      </div>
      <div class="filter-field">
        <label class="filter-label">DEPARTMENT</label>
        <Select
          v-model="departmentId"
          :options="departments"
          option-label="name"
          option-value="id"
          placeholder="All Departments"
          show-clear
          class="filter-select"
        />
      </div>
    </div>

    <!-- Table -->
    <div class="page-body">
      <Card>
        <template #title>
          <div class="card-header-row">
            <span>Issues Handled Per Member (Monthly)</span>
            <span v-if="data" class="card-meta">{{ data.meta?.totalRows }} members</span>
          </div>
        </template>
        <template #content>
          <div v-if="loading" class="state-center">
            <ProgressSpinner style="width:36px;height:36px" strokeWidth="4" />
            <span>Loading...</span>
          </div>
          <div v-else-if="error" class="state-center state-error">{{ error }}</div>

          <DataTable
            v-else-if="data"
            :value="data.rows"
            size="small"
            scrollable
            scroll-height="500px"
            class="member-table"
          >
            <Column
              v-for="col in data.columns"
              :key="col.key"
              :field="col.key"
              :header="col.label"
              :header-class="col.type === 'number' ? 'th-center' : ''"
              :body-class="col.type === 'number' ? 'td-center' : ''"
              :footer-class="col.type === 'number' ? 'td-center' : ''"
            >
              <template #body="{ data: row }">
                <template v-if="col.type === 'number'">
                  <span
                    v-if="row[col.key] > 0"
                    class="badge"
                    :style="heatStyle(row[col.key])"
                  >{{ row[col.key] }}</span>
                  <span v-else class="zero">—</span>
                </template>
                <template v-else>{{ row[col.key] }}</template>
              </template>
              <template #footer>
                <span v-if="col.key === 'member'" class="foot-label">Total</span>
                <b v-else-if="col.type === 'number'">{{ colSum(col.key) }}</b>
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import Select          from 'primevue/select'
import Card            from 'primevue/card'
import DataTable       from 'primevue/datatable'
import Column          from 'primevue/column'
import ProgressSpinner from 'primevue/progressspinner'
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

const colSum = (key) => data.value?.rows?.reduce((s, r) => s + (r[key] || 0), 0) ?? 0
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
.filter-select { min-width: 150px; }

/* Body */
.page-body { padding: 20px 24px; }

.card-header-row {
  display: flex; justify-content: space-between; align-items: baseline;
}
.card-meta { font-size: 12px; color: #9fa8da; font-weight: 400; }

/* DataTable overrides */
.member-table :deep(.th-center),
.member-table :deep(.td-center) { text-align: center !important; }

.member-table :deep(th) {
  font-size: 11px !important; font-weight: 700 !important;
  text-transform: uppercase; letter-spacing: 0.5px;
  white-space: nowrap; min-width: 52px;
}
.member-table :deep(td) { white-space: nowrap; font-size: 13px; }

/* Footer row */
.member-table :deep(tfoot td) {
  background: #f0f2fb !important; font-size: 12.5px;
}
.foot-label { color: #6b7399; font-weight: 700; }

.badge {
  display: inline-block; padding: 2px 8px; border-radius: 4px;
  font-size: 12px; font-weight: 600; min-width: 28px; text-align: center;
}
.zero { color: #c5cae9; }

/* States */
.state-center {
  height: 200px; display: flex; align-items: center;
  justify-content: center; gap: 10px; color: #6b7399; font-size: 14px;
}
.state-error { color: #e57373; }
</style>
