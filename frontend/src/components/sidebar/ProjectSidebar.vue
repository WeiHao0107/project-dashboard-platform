<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <span class="sidebar-logo">📊</span>
      <span class="sidebar-title">Dashboard</span>
    </div>

    <div class="sidebar-section-label">Projects</div>

    <div v-if="loading" class="sidebar-loading">Loading...</div>
    <div v-else-if="error" class="sidebar-error">{{ error }}</div>

    <nav v-else class="sidebar-nav">
      <ProjectItem
        v-for="project in projects"
        :key="project.key"
        :project="project"
        :is-active="selectedProjectKey === project.key"
        :active-page-id="selectedPageId"
        @select="$emit('select-project', project.key)"
        @select-page="(pageId) => $emit('select-page', pageId)"
      />
    </nav>
  </aside>
</template>

<script setup>
import ProjectItem from './ProjectItem.vue'

defineProps({
  projects:           { type: Array,  default: () => [] },
  loading:            { type: Boolean, default: false },
  error:              { type: String,  default: null },
  selectedProjectKey: { type: String,  default: null },
  selectedPageId:     { type: String,  default: null },
})

defineEmits(['select-project', 'select-page'])
</script>

<style scoped>
.sidebar {
  width: 220px;
  min-height: 100vh;
  background: #1e2235;
  color: #c8cde4;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 16px 16px;
  border-bottom: 1px solid #2d3250;
}

.sidebar-logo { font-size: 20px; }

.sidebar-title {
  font-size: 16px;
  font-weight: 700;
  color: #e8eaf6;
  letter-spacing: 0.3px;
}

.sidebar-section-label {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  color: #6b7399;
  padding: 16px 16px 6px;
}

.sidebar-nav { flex: 1; overflow-y: auto; }

.sidebar-loading,
.sidebar-error {
  padding: 12px 16px;
  font-size: 13px;
  color: #6b7399;
}
.sidebar-error { color: #e57373; }
</style>
