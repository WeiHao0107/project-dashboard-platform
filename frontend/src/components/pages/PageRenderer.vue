<template>
  <div class="page-renderer">
    <!-- Header -->
    <div class="page-header">
      <div class="page-title-row">
        <h2 class="page-title">{{ pageDef?.title ?? '...' }}</h2>
        <span v-if="pageDef?.description" class="page-desc">{{ pageDef.description }}</span>
      </div>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="page-loading">
      <div class="skeleton-bar"></div>
      <div class="skeleton-card"></div>
    </div>

    <div v-else-if="error" class="page-error">{{ error }}</div>

    <template v-else-if="pageDef">
      <!-- Filter bar -->
      <FilterBar
        :available-filters="pageDef.availableFilters"
        :default-filters="pageDef.defaultFilters"
        :departments="departments"
        v-model="filters"
      />

      <!-- Widget grid -->
      <WidgetGrid
        :layout="pageDef.layout"
        :project-key="projectKey"
        :page-id="pageId"
        :filters="filters"
      />
    </template>

    <div v-else class="page-empty">
      Select a page from the sidebar
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import FilterBar  from '../filter/FilterBar.vue'
import WidgetGrid from '../widgets/WidgetGrid.vue'
import { usePageDefinition } from '../../composables/usePageDefinition.js'
import { useDepartments }    from '../../composables/useDepartments.js'
import { toRef, computed }   from 'vue'

const props = defineProps({
  projectKey: { type: String, default: null },
  pageId:     { type: String, default: null },
})

const projectKeyRef = toRef(props, 'projectKey')
const pageIdRef     = toRef(props, 'pageId')

const { pageDef, loading, error } = usePageDefinition(projectKeyRef, pageIdRef)
const { departments } = useDepartments(projectKeyRef)

const filters = ref({})

// Reset filters when page changes
watch(pageDef, (def) => {
  if (def?.defaultFilters) {
    filters.value = { ...def.defaultFilters }
  }
})
</script>

<style scoped>
.page-renderer {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow-y: auto;
  background: #f0f2f5;
}

.page-header {
  padding: 20px 24px 0;
}

.page-title-row {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: #1a1a2e;
}

.page-desc {
  font-size: 13px;
  color: #6b7399;
}

.page-loading {
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.skeleton-bar {
  height: 44px;
  border-radius: 8px;
  background: linear-gradient(90deg, #e8eaf6 25%, #f5f6fb 50%, #e8eaf6 75%);
  background-size: 200% 100%;
  animation: shimmer 1.2s infinite;
}

.skeleton-card {
  height: 360px;
  border-radius: 10px;
  background: linear-gradient(90deg, #e8eaf6 25%, #f5f6fb 50%, #e8eaf6 75%);
  background-size: 200% 100%;
  animation: shimmer 1.2s infinite;
}

@keyframes shimmer {
  0%   { background-position: -200% 0; }
  100% { background-position:  200% 0; }
}

.page-error {
  padding: 40px 24px;
  color: #e57373;
  font-size: 14px;
}

.page-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9fa8da;
  font-size: 15px;
}
</style>
