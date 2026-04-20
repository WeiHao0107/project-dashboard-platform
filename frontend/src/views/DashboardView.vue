<template>
  <div class="layout">
    <ProjectSidebar
      :projects="projects"
      :loading="loading"
      :error="error"
      :selected-project-key="selectedProjectKey"
      :selected-page-id="selectedPageId"
      @select-project="onSelectProject"
      @select-page="onSelectPage"
    />

    <main class="main">
      <!-- Render the dedicated page component by page key -->
      <component
        v-if="currentPageComponent && selectedProjectKey"
        :is="currentPageComponent"
        :project-key="selectedProjectKey"
        :key="selectedProjectKey + '-' + selectedPageId"
      />

      <!-- Empty state -->
      <div v-else class="empty-state">
        <div class="empty-icon">📊</div>
        <p>Select a project and page from the sidebar</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import ProjectSidebar       from '../components/sidebar/ProjectSidebar.vue'
import IssueTrendPage        from '../pages/IssueTrendPage.vue'
import MemberPerformancePage from '../pages/MemberPerformancePage.vue'
import { useProjects }       from '../composables/useProjects.js'

// ── page key → Vue component mapping ─────────────────────
const PAGE_MAP = {
  'issue-trend':        IssueTrendPage,
  'member-performance': MemberPerformancePage,
}

const { projects, loading, error } = useProjects()

const selectedProjectKey = ref(null)
const selectedPageId     = ref(null)

// Auto-select first project once list loads
watch(projects, (list) => {
  if (list.length > 0 && !selectedProjectKey.value) {
    selectedProjectKey.value = list[0].key
  }
}, { immediate: true })

function onSelectProject(key) {
  if (selectedProjectKey.value === key) return
  selectedProjectKey.value = key
  selectedPageId.value     = null    // sidebar will auto-select first page
}

function onSelectPage(pageId) {
  selectedPageId.value = pageId
}

const currentPageComponent = computed(() =>
  selectedPageId.value ? (PAGE_MAP[selectedPageId.value] ?? null) : null
)
</script>

<style scoped>
.layout { display: flex; min-height: 100vh; }

.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #9fa8da;
}
.empty-icon { font-size: 48px; }
.empty-state p { font-size: 15px; }
</style>
