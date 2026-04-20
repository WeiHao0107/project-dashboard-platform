<template>
  <div class="widget-card">
    <div class="widget-header">
      <h3 class="widget-title">{{ definition.title }}</h3>
      <span v-if="data" class="widget-meta">{{ data.meta?.totalRows }} members</span>
    </div>

    <div v-if="loading" class="widget-loading">
      <span class="spinner"></span> Loading...
    </div>
    <div v-else-if="error" class="widget-error">{{ error }}</div>

    <div v-else-if="data" class="table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th
              v-for="col in data.columns"
              :key="col.key"
              :class="['col-' + col.type, isMonthCol(col.key) ? 'col-month' : '']"
            >
              {{ col.label }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, idx) in data.rows" :key="idx">
            <td
              v-for="col in data.columns"
              :key="col.key"
              :class="['col-' + col.type, col.key === 'total' ? 'col-total' : '']"
            >
              <template v-if="col.type === 'number'">
                <span v-if="row[col.key] > 0" class="num-badge" :style="badgeStyle(row[col.key])">
                  {{ row[col.key] }}
                </span>
                <span v-else class="num-zero">—</span>
              </template>
              <template v-else>{{ row[col.key] }}</template>
            </td>
          </tr>
        </tbody>
        <tfoot v-if="totals">
          <tr class="footer-row">
            <td class="col-string footer-label">Total</td>
            <td class="col-string footer-label"></td>
            <td
              v-for="mk in monthKeys"
              :key="mk"
              class="col-number col-month"
            >
              <strong>{{ totals[mk] || 0 }}</strong>
            </td>
            <td class="col-number col-total">
              <strong>{{ grandTotal }}</strong>
            </td>
          </tr>
        </tfoot>
      </table>
    </div>
    <div v-else class="widget-empty">No data</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  definition: { type: Object,  required: true },
  data:       { type: Object,  default: null },
  loading:    { type: Boolean, default: false },
  error:      { type: String,  default: null },
})

const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

const monthKeys = computed(() =>
  MONTHS.filter(m => props.data?.columns?.some(c => c.key === m))
)

const isMonthCol = (key) => MONTHS.includes(key)

const totals = computed(() => {
  if (!props.data?.rows?.length) return null
  const t = {}
  for (const mk of monthKeys.value) {
    t[mk] = props.data.rows.reduce((s, r) => s + (r[mk] || 0), 0)
  }
  return t
})

const grandTotal = computed(() =>
  props.data?.rows?.reduce((s, r) => s + (r.total || 0), 0) ?? 0
)

// Colour heat-map: more issues → deeper blue
const maxVal = computed(() => {
  if (!props.data?.rows) return 1
  let m = 0
  for (const r of props.data.rows) {
    for (const mk of monthKeys.value) {
      if (r[mk] > m) m = r[mk]
    }
  }
  return m || 1
})

function badgeStyle(val) {
  const pct   = val / maxVal.value
  const alpha = 0.12 + pct * 0.55
  return { background: `rgba(89,120,204,${alpha.toFixed(2)})`, color: pct > 0.5 ? '#fff' : '#2d3460' }
}
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

.widget-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 14px;
}

.widget-title {
  font-size: 14px;
  font-weight: 600;
  color: #2d3460;
}

.widget-meta {
  font-size: 12px;
  color: #9fa8da;
}

.table-wrapper {
  flex: 1;
  overflow-x: auto;
  overflow-y: auto;
  max-height: 520px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.data-table thead th {
  position: sticky;
  top: 0;
  background: #f5f6fb;
  padding: 8px 10px;
  text-align: left;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #6b7399;
  white-space: nowrap;
  border-bottom: 2px solid #e8eaf6;
  z-index: 1;
}

.data-table tbody tr:hover { background: #f8f9fe; }

.data-table td {
  padding: 7px 10px;
  border-bottom: 1px solid #f0f2f5;
  white-space: nowrap;
  color: #2d3460;
}

.col-month { text-align: center; min-width: 54px; }
.col-total { text-align: center; min-width: 58px; font-weight: 700; }
.col-number { text-align: center; }

.num-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  min-width: 28px;
  text-align: center;
}

.num-zero { color: #c5cae9; }

.footer-row td {
  background: #f0f2fb;
  border-top: 2px solid #e8eaf6;
  font-size: 12.5px;
  color: #2d3460;
}

.footer-label { color: #6b7399; font-weight: 700; }

.widget-loading {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #6b7399;
  font-size: 14px;
}

.widget-error, .widget-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #e57373;
  font-size: 13px;
}
.widget-empty { color: #9fa8da; }

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
