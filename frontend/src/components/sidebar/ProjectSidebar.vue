<template>
  <aside class="sidebar">
    <!-- Logo -->
    <div class="sidebar-logo">
      <span class="logo-icon">📊</span>
      <span class="logo-text">Dashboard</span>
    </div>

    <!-- ── PROJECT LIST ── -->
    <div class="section-label">Projects</div>

    <div v-if="loading" class="sidebar-hint">Loading...</div>
    <div v-else-if="error" class="sidebar-hint error">{{ error }}</div>

    <nav v-else class="project-list">
      <button
        v-for="proj in projects"
        :key="proj.key"
        class="project-btn"
        :class="{ active: route.params.projectKey === proj.key }"
        @click="selectProject(proj.key)"
      >
        <span class="project-initial">{{ proj.name[0] }}</span>
        <span class="project-name">{{ proj.name }}</span>
        <span v-if="route.params.projectKey === proj.key" class="project-check">✓</span>
      </button>
    </nav>

    <!-- ── PAGE LIST ── -->
    <template v-if="route.params.projectKey && pages.length">
      <div class="divider" />
      <div class="section-label">Pages</div>
      <nav class="page-list">
        <RouterLink
          v-for="page in pages"
          :key="page.pageId"
          :to="{ name: page.pageId, params: { projectKey: route.params.projectKey } }"
          class="page-btn"
          active-class="active"
        >
          <span class="page-icon">{{ PAGE_ICONS[page.icon] ?? '📄' }}</span>
          {{ page.title }}
        </RouterLink>
      </nav>
    </template>

    <div v-else-if="route.params.projectKey && pagesLoading" class="sidebar-hint">
      Loading pages...
    </div>
  </aside>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../../api/index.js'

const PAGE_ICONS = {
  'chart-line': '📈',
  'users':      '👥',
  'table':      '📋',
  'bar-chart':  '📊',
}

const props = defineProps({
  projects: { type: Array,   default: () => [] },
  loading:  { type: Boolean, default: false },
  error:    { type: String,  default: null },
})

const route  = useRoute()
const router = useRouter()

// ── Pages for current project ─────────────────────────────
const pages        = ref([])
const pagesLoading = ref(false)

async function loadPages(projectKey) {
  if (!projectKey) { pages.value = []; return }
  pagesLoading.value = true
  try {
    pages.value = (await api.getPages(projectKey)).data
  } finally {
    pagesLoading.value = false
  }
}

watch(() => route.params.projectKey, loadPages, { immediate: true })

// ── Project click → navigate to that project's first page ─
function selectProject(key) {
  if (route.params.projectKey === key) return
  router.push({ name: 'issue-trend', params: { projectKey: key } })
}
</script>

<style scoped>
.sidebar {
  width: 220px; min-height: 100vh;
  background: #1e2235; color: #c8cde4;
  display: flex; flex-direction: column; flex-shrink: 0; overflow-y: auto;
}

.sidebar-logo {
  display: flex; align-items: center; gap: 10px;
  padding: 18px 16px 14px; border-bottom: 1px solid #2d3250;
}
.logo-icon { font-size: 20px; }
.logo-text  { font-size: 16px; font-weight: 700; color: #e8eaf6; }

.section-label {
  font-size: 10px; font-weight: 700; letter-spacing: 1.2px;
  text-transform: uppercase; color: #6b7399; padding: 14px 16px 6px;
}

.project-list { display: flex; flex-direction: column; gap: 2px; padding: 0 8px; }

.project-btn {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 10px; background: none; border: none; border-radius: 7px;
  color: #a8b0d0; font-size: 13px; font-weight: 500;
  cursor: pointer; text-align: left; width: 100%;
  transition: background 0.15s, color 0.15s;
}
.project-btn:hover  { background: #272d48; color: #e8eaf6; }
.project-btn.active { background: #2d3460; color: #fff; font-weight: 600; }

.project-initial {
  width: 26px; height: 26px; border-radius: 6px; background: #3d4570;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700; color: #9fa8da; flex-shrink: 0;
}
.project-btn.active .project-initial { background: #5c6bc0; color: #fff; }
.project-name  { flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.project-check { font-size: 11px; color: #7986cb; }

.divider { height: 1px; background: #2d3250; margin: 10px 0 0; }

.page-list { display: flex; flex-direction: column; gap: 2px; padding: 0 8px 12px; }

.page-btn {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 10px; background: none; border: none; border-radius: 7px;
  color: #8890b0; font-size: 13px; cursor: pointer; text-align: left;
  text-decoration: none; transition: background 0.15s, color 0.15s; width: 100%;
}
.page-btn:hover  { background: #272d48; color: #e8eaf6; }
.page-btn.active { background: #272d48; color: #9fa8da; font-weight: 600; }

.page-icon { font-size: 14px; }

.sidebar-hint { padding: 8px 16px; font-size: 12px; color: #6b7399; }
.sidebar-hint.error { color: #e57373; }
</style>
