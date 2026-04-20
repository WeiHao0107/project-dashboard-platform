<template>
  <div class="page">
    <div class="page-header">
      <h2 class="page-title">👥 Member Performance</h2>
      <p class="page-desc">Monthly issues resolved per team member</p>
    </div>

    <FilterBar
      :available-filters="['year', 'department']"
      :departments="departments"
      v-model="filters"
    />

    <div class="page-body">
      <div class="table-card">
        <div class="card-header">
          <span class="card-title">Issues Handled Per Member (Monthly)</span>
          <span v-if="data" class="card-meta">{{ data.meta?.totalRows }} members</span>
        </div>

        <div v-if="loading" class="state-loading">
          <span class="spinner" /> Loading table data...
        </div>
        <div v-else-if="error" class="state-error">{{ error }}</div>

        <div v-else-if="data" class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th v-for="col in data.columns" :key="col.key"
                    :class="['th-' + col.type, isMonthKey(col.key) ? 'th-month' : '']">
                  {{ col.label }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in data.rows" :key="idx">
                <td v-for="col in data.columns" :key="col.key"
                    :class="['td-' + col.type, col.key === 'total' ? 'td-total' : '', isMonthKey(col.key) ? 'td-month' : '']">
                  <template v-if="col.type === 'number'">
                    <span v-if="row[col.key] > 0" class="num-badge" :style="heatStyle(row[col.key])">
                      {{ row[col.key] }}
                    </span>
                    <span v-else class="num-zero">—</span>
                  </template>
                  <template v-else>{{ row[col.key] }}</template>
                </td>
              </tr>
            </tbody>
            <tfoot>
              <tr class="foot-row">
                <td class="foot-label">Total</td>
                <td></td>
                <td v-for="mk in monthKeys" :key="mk" class="td-number td-month">
                  <b>{{ colTotal(mk) }}</b>
                </td>
                <td class="td-number td-total"><b>{{ grandTotal }}</b></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, toRef } from 'vue'
import FilterBar          from '../components/filter/FilterBar.vue'
import { usePageData }    from '../composables/usePageData.js'
import { useDepartments } from '../composables/useDepartments.js'

const props = defineProps({
  projectKey: { type: String, required: true },
})

const projectKeyRef = toRef(props, 'projectKey')
const filters       = ref({ year: new Date().getFullYear(), departmentId: null })

const { departments }          = useDepartments(projectKeyRef)
const { data, loading, error } = usePageData(projectKeyRef, 'member_monthly_summary', filters)

const ALL_MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

const isMonthKey = (key) => ALL_MONTHS.includes(key)

const monthKeys = computed(() =>
  ALL_MONTHS.filter(m => data.value?.columns?.some(c => c.key === m))
)

const maxVal = computed(() => {
  if (!data.value?.rows) return 1
  let m = 0
  for (const r of data.value.rows)
    for (const mk of monthKeys.value)
      if (r[mk] > m) m = r[mk]
  return m || 1
})

function heatStyle(val) {
  const pct   = val / maxVal.value
  const alpha = 0.12 + pct * 0.55
  return {
    background: `rgba(89,120,204,${alpha.toFixed(2)})`,
    color: pct > 0.5 ? '#fff' : '#2d3460',
  }
}

function colTotal(mk) {
  return data.value?.rows?.reduce((s, r) => s + (r[mk] || 0), 0) ?? 0
}

const grandTotal = computed(() =>
  data.value?.rows?.reduce((s, r) => s + (r.total || 0), 0) ?? 0
)
</script>

<style scoped>
.page { display: flex; flex-direction: column; height: 100%; background: #f0f2f5; overflow-y: auto; }

.page-header { padding: 20px 24px 0; }
.page-title  { font-size: 20px; font-weight: 700; color: #1a1a2e; }
.page-desc   { font-size: 13px; color: #6b7399; margin-top: 3px; }

.page-body { padding: 20px 24px; }

.table-card {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 14px;
}
.card-title { font-size: 14px; font-weight: 600; color: #2d3460; }
.card-meta  { font-size: 12px; color: #9fa8da; }

.table-wrapper { overflow-x: auto; max-height: 540px; overflow-y: auto; }

.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }

.data-table thead th {
  position: sticky; top: 0; z-index: 1;
  background: #f5f6fb;
  padding: 8px 10px;
  text-align: left;
  font-size: 11px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.5px;
  color: #6b7399;
  white-space: nowrap;
  border-bottom: 2px solid #e8eaf6;
}
.th-month, .th-number { text-align: center; min-width: 52px; }
.data-table tbody tr:hover { background: #f8f9fe; }
.data-table td {
  padding: 7px 10px; border-bottom: 1px solid #f0f2f5;
  white-space: nowrap; color: #2d3460;
}
.td-month, .td-number { text-align: center; }
.td-total { font-weight: 700; }

.num-badge {
  display: inline-block; padding: 2px 8px;
  border-radius: 4px; font-size: 12px; font-weight: 600;
  min-width: 28px; text-align: center;
}
.num-zero { color: #c5cae9; }

.foot-row td {
  background: #f0f2fb;
  border-top: 2px solid #e8eaf6;
  padding: 7px 10px;
  font-size: 12.5px;
}
.foot-label { color: #6b7399; font-weight: 700; }

.state-loading {
  height: 200px;
  display: flex; align-items: center; justify-content: center;
  gap: 8px; color: #6b7399; font-size: 14px;
}
.state-error {
  height: 200px;
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
