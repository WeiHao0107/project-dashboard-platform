<template>
  <div class="filter-bar">
    <YearSelector
      v-if="availableFilters.includes('year')"
      :model-value="modelValue.year ?? currentYear"
      @update:model-value="update('year', $event)"
    />
    <DepartmentSelector
      v-if="availableFilters.includes('department')"
      :model-value="modelValue.departmentId ?? null"
      :departments="departments"
      @update:model-value="update('departmentId', $event)"
    />
  </div>
</template>

<script setup>
const currentYear = new Date().getFullYear()

const props = defineProps({
  availableFilters: { type: Array,  default: () => [] },
  departments:      { type: Array,  default: () => [] },
  modelValue:       { type: Object, default: () => ({}) },
})
const emit = defineEmits(['update:modelValue'])

function update(key, val) {
  emit('update:modelValue', { ...props.modelValue, [key]: val })
}
</script>

<script>
import YearSelector       from './YearSelector.vue'
import DepartmentSelector from './DepartmentSelector.vue'
export default { components: { YearSelector, DepartmentSelector } }
</script>

<style scoped>
.filter-bar {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  flex-wrap: wrap;
  background: #fff;
  border-bottom: 1px solid #e8eaf6;
  padding: 10px 24px;
}
</style>
