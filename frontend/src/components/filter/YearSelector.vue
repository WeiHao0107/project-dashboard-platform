<template>
  <div class="filter-field">
    <label class="filter-label">Year</label>
    <select class="filter-select" :value="modelValue" @change="$emit('update:modelValue', +$event.target.value)">
      <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
    </select>
  </div>
</template>

<script setup>
defineProps({
  modelValue: { type: Number, required: true },
})
defineEmits(['update:modelValue'])

const currentYear = new Date().getFullYear()
const years = Array.from({ length: 5 }, (_, i) => currentYear - i)
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
  min-width: 90px;
  outline: none;
  transition: border-color 0.15s;
}
.filter-select:focus { border-color: #7986cb; }
</style>
