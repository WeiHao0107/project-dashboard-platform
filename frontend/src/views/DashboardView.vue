<template>
  <div class="layout">
    <ProjectSidebar
      :projects="projects"
      :loading="loading"
      :error="error"
    />

    <main class="main">
      <RouterView v-if="$route.params.projectKey" />
      <div v-else class="empty-state">
        <div class="empty-icon">📊</div>
        <p>Select a project and page from the sidebar</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ProjectSidebar from '../components/sidebar/ProjectSidebar.vue'
import { api } from '../api/index.js'

const router   = useRouter()
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

// Auto-navigate to first project's first page when no route is active yet
watch(projects, (list) => {
  if (list.length > 0 && !router.currentRoute.value.params.projectKey) {
    router.replace({ name: 'issue-trend', params: { projectKey: list[0].key } })
  }
})
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
