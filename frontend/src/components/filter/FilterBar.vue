<template>
  <div class="filter-bar">
    <div class="filter-bar-inner">
      <YearSelector
        v-if="availableFilters.includes('year')"
        v-model="localYear"
      />
      <DepartmentSelector
        v-if="availableFilters.includes('department')"
        v-model="localDepartmentId"
        :departments="departments"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import YearSelector       from './YearSelector.vue'
import DepartmentSelector from './DepartmentSelector.vue'

const props = defineProps({
  availableFilters: { type: Array,  default: () => [] },
  defaultFilters:   { type: Object, default: () => ({}) },
  departments:      { type: Array,  default: () => [] },
  modelValue:       { type: Object, default: () => ({}) },
})

const emit = defineEmits(['update:modelValue'])

const localYear         = ref(props.defaultFilters.year ?? new Date().getFullYear())
const localDepartmentId = ref(props.modelValue?.departmentId ?? null)

// Sync outward whenever either filter changes
watch([localYear, localDepartmentId], () => {
  emit('update:modelValue', {
    year:         localYear.value,
    departmentId: localDepartmentId.value,
  })
}, { immediate: true })

// When parent changes defaultFilters (page switch), reset
watch(() => props.defaultFilters, (val) => {
  if (val?.year) localYear.value = val.year
}, { deep: true })
</script>

<style scoped>
.filter-bar {
  background: #fff;
  border-bottom: 1px solid #e8eaf6;
  padding: 10px 24px;
}

.filter-bar-inner {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  flex-wrap: wrap;
}
</style>
