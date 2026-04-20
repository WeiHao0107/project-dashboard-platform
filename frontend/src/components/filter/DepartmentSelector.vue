<template>
  <div class="filter-field">
    <label class="filter-label">Department</label>
    <select
      class="filter-select"
      :value="modelValue"
      @change="$emit('update:modelValue', $event.target.value ? +$event.target.value : null)"
    >
      <option :value="null">All Departments</option>
      <option v-for="dept in departments" :key="dept.id" :value="dept.id">
        {{ dept.name }}
      </option>
    </select>
  </div>
</template>

<script setup>
defineProps({
  modelValue:  { type: Number,  default: null },
  departments: { type: Array,   default: () => [] },
})
defineEmits(['update:modelValue'])
</script>

<style scoped>
.filter-field { display: flex; flex-direction: column; gap: 4px; }

.filter-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: #6b7399;
}

.filter-select {
  padding: 6px 10px;
  border: 1px solid #d1d5e0;
  border-radius: 6px;
  background: #fff;
  font-size: 13px;
  color: #1a1a2e;
  cursor: pointer;
  min-width: 150px;
  outline: none;
  transition: border-color 0.15s;
}
.filter-select:focus { border-color: #7986cb; }
</style>
