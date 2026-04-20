<template>
  <div class="dashboard-layout">
    <ProjectSidebar
      :projects="projects"
      :loading="loading"
      :error="error"
      :selected-project-key="selectedProjectKey"
      :selected-page-id="selectedPageId"
      @select-project="selectProject"
      @select-page="selectPage"
    />

    <main class="dashboard-main">
      <PageRenderer
        :project-key="selectedProjectKey"
        :page-id="selectedPageId"
      />
    </main>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import ProjectSidebar from '../components/sidebar/ProjectSidebar.vue'
import PageRenderer   from '../components/pages/PageRenderer.vue'
import { useProjects } from '../composables/useProjects.js'

const { projects, loading, error } = useProjects()

const selectedProjectKey = ref(null)
const selectedPageId     = ref(null)

// Auto-select first project once loaded
watch(projects, (list) => {
  if (list.length > 0 && !selectedProjectKey.value) {
    selectedProjectKey.value = list[0].key
  }
}, { immediate: true })

function selectProject(key) {
  if (selectedProjectKey.value === key) return   // already active, no reset
  selectedProjectKey.value = key
  selectedPageId.value     = null                // clear page; ProjectItem will auto-select first
}

function selectPage(pageId) {
  selectedPageId.value = pageId
}
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  min-height: 100vh;
}
.dashboard-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
</style>
