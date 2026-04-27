<template>
  <div>
    <div v-if="loading" class="state-center">
      <p-progress-spinner style="width:36px;height:36px" strokeWidth="4" />
      <span>Loading...</span>
    </div>
    <div v-else-if="error" class="state-center state-error">{{ error }}</div>

    <p-data-table
      v-else-if="rows.length"
      :value="rows"
      size="small"
      scrollable
      scroll-height="500px"
      class="member-table"
    >
      <p-column
        v-for="col in columns"
        :key="col.key"
        :field="col.key"
        :header="col.label"
        :header-class="col.type === 'number' ? 'th-center' : ''"
        :body-class="col.type === 'number' ? 'td-center' : ''"
        :footer-class="col.type === 'number' ? 'td-center' : ''"
      >
        <template #body="{ data: row }">
          <template v-if="col.type === 'number'">
            <span v-if="row[col.key] > 0" class="badge" :style="heatStyle(row[col.key])">
              {{ row[col.key] }}
            </span>
            <span v-else class="zero">—</span>
          </template>
          <template v-else>{{ row[col.key] }}</template>
        </template>

        <template #footer>
          <span v-if="col.key === firstTextCol" class="foot-label">Total</span>
          <b v-else-if="col.type === 'number'">{{ colSum(col.key) }}</b>
        </template>
      </p-column>
    </p-data-table>

    <div v-else-if="!loading" class="state-center">No data</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  columns: { type: Array,   required: true },   // [{ key, label, type }]
  rows:    { type: Array,   required: true },   // row objects
  loading: { type: Boolean, default: false },
  error:   { type: String,  default: null },
})

// First text-type column gets the "Total" footer label
const firstTextCol = computed(() =>
  props.columns.find(c => c.type !== 'number')?.key ?? null
)

// Max value across month-like number columns (exclude 'total') for heat scale
const maxVal = computed(() => {
  const monthCols = props.columns
    .filter(c => c.type === 'number' && c.key !== 'total')
    .map(c => c.key)
  let m = 0
  for (const r of props.rows)
    for (const k of monthCols)
      if (r[k] > m) m = r[k]
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

const colSum = (key) => props.rows.reduce((s, r) => s + (r[key] || 0), 0)
</script>

<style scoped>
.member-table :deep(.th-center),
.member-table :deep(.td-center) { text-align: center !important; }

.member-table :deep(th) {
  font-size: 11px !important; font-weight: 700 !important;
  text-transform: uppercase; letter-spacing: 0.5px;
  white-space: nowrap; min-width: 52px;
}
.member-table :deep(td) { white-space: nowrap; font-size: 13px; }

.member-table :deep(tfoot td) {
  background: #f0f2fb !important; font-size: 12.5px;
}
.foot-label { color: #6b7399; font-weight: 700; }

.badge {
  display: inline-block; padding: 2px 8px; border-radius: 4px;
  font-size: 12px; font-weight: 600; min-width: 28px; text-align: center;
}
.zero { color: #c5cae9; }

.state-center {
  height: 200px; display: flex; align-items: center;
  justify-content: center; gap: 10px; color: #6b7399; font-size: 14px;
}
.state-error { color: #e57373; }
</style>
