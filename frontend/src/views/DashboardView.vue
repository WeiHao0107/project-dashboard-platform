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
      <component
        v-if="currentPageComponent && selectedProjectKey"
        :is="currentPageComponent"
        :project-key="selectedProjectKey"
        :key="selectedProjectKey + '-' + selectedPageId"
      />
      <div v-else class="empty-state">
        <div class="empty-icon">📊</div>
        <p>Select a project and page from the sidebar</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import ProjectSidebar        from '../components/sidebar/ProjectSidebar.vue'
import IssueTrendPage        from '../pages/IssueTrendPage.vue'
import MemberPerformancePage from '../pages/MemberPerformancePage.vue'
import { api }               from '../api/index.js'

// ── page key → component mapping ─────────────────────────
const PAGE_MAP = {
  'issue-trend':        IssueTrendPage,
  'member-performance': MemberPerformancePage,
}

// ── projects ──────────────────────────────────────────────
const projects = ref([])
const loading  = ref(false)
const error    = ref(null)

async function fetchProjects() {
  loading.value = true
  try {
    projects.value = (await api.getProjects()).data
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(fetchProjects)

// Auto-select first project once loaded
watch(projects, (list) => {
  if (list.length > 0 && !selectedProjectKey.value) {
    selectedProjectKey.value = list[0].key
  }
})

// ── selection state ───────────────────────────────────────
const selectedProjectKey = ref(null)
const selectedPageId     = ref(null)

function onSelectProject(key) {
  if (selectedProjectKey.value === key) return
  selectedProjectKey.value = key
  selectedPageId.value     = null
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
.main   { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

.empty-state {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 12px; color: #9fa8da;
}
.empty-icon { font-size: 48px; }
.empty-state p { font-size: 15px; }
</style>
