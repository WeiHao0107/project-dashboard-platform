<template>
  <div class="widget-grid">
    <WidgetContainer
      v-for="widget in layout"
      :key="widget.widgetId"
      :definition="widget"
      :project-key="projectKey"
      :page-id="pageId"
      :filters="filters"
      class="widget-cell"
    />
  </div>
</template>

<script setup>
import WidgetContainer from './WidgetContainer.vue'

defineProps({
  layout:     { type: Array,  default: () => [] },
  projectKey: { type: String, required: true },
  pageId:     { type: String, required: true },
  filters:    { type: Object, default: () => ({}) },
})
</script>

<style scoped>
.widget-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px 24px;
}

.widget-cell {
  width: 100%;
}
</style>
