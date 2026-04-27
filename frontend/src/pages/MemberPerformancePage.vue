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
        <p-select
          v-model="year"
          :options="yearOptions"
          class="filter-select"
        />
      </div>
      <div class="filter-field">
        <label class="filter-label">DEPARTMENT</label>
        <p-select
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
      <p-card>
        <template #title>
          <div class="card-header-row">
            <span>Issues Handled Per Member (Monthly)</span>
            <span v-if="data" class="card-meta">{{ data.length }} members</span>
          </div>
        </template>
        <template #content>
          <MemberTable
            :columns="tableColumns"
            :rows="data ?? []"
            :loading="loading"
            :error="error"
          />
        </template>
      </p-card>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import MemberTable from '../components/table/MemberTable.vue'
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
    const res = await api.getMemberPerformance(props.projectKey, {
      year: year.value,
      departmentId: departmentId.value,
    })
    data.value = res.data   // now a plain array
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

watch([() => props.projectKey, year, departmentId], fetchData, { immediate: true })

// Fixed column definitions (backend no longer sends columns)
const MONTH_KEYS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
const tableColumns = [
  { key: 'member',  label: 'Member', type: 'string' },
  ...MONTH_KEYS.map(m => ({ key: m, label: m, type: 'number' })),
  { key: 'total',   label: 'Total',  type: 'number' },
]
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
