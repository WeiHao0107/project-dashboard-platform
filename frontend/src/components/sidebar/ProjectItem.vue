<template>
  <div class="project-item">
    <!-- Project row -->
    <button
      class="project-row"
      :class="{ active: isActive }"
      @click="$emit('select', project.key)"
    >
      <span class="project-icon">{{ isActive ? '▾' : '▸' }}</span>
      <span class="project-name">{{ project.name }}</span>
    </button>

    <!-- Page list – only visible when this project is active -->
    <transition name="slide">
      <div v-if="isActive" class="page-list">
        <div v-if="pagesLoading" class="page-loading">Loading...</div>
        <button
          v-for="page in pages"
          :key="page.pageId"
          class="page-row"
          :class="{ active: activePageId === page.pageId }"
          @click="$emit('select-page', page.pageId)"
        >
          <span class="page-dot">·</span>
          {{ page.title }}
        </button>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { api } from '../../api/index.js'

const props = defineProps({
  project:      { type: Object,  required: true },
  isActive:     { type: Boolean, default: false },
  activePageId: { type: String,  default: null },
})

const emit = defineEmits(['select', 'select-page'])

const pages        = ref([])
const pagesLoading = ref(false)

async function loadPages() {
  if (pages.value.length > 0) return   // already loaded
  pagesLoading.value = true
  try {
    const res   = await api.getPages(props.project.key)
    pages.value = res.data
    // Auto-select first page when project first becomes active
    if (pages.value.length > 0) {
      emit('select-page', pages.value[0].pageId)
    }
  } finally {
    pagesLoading.value = false
  }
}

// Load pages the moment this project becomes active
watch(
  () => props.isActive,
  (val) => { if (val) loadPages() },
  { immediate: true }
)
</script>

<style scoped>
.project-row {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 16px;
  background: none;
  border: none;
  color: #a8b0d0;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  text-align: left;
  transition: background 0.15s, color 0.15s;
}
.project-row:hover  { background: #272d48; color: #e8eaf6; }
.project-row.active { background: #2d3460; color: #7986cb; }

.project-icon {
  font-size: 11px;
  width: 14px;
  color: #6b7399;
}

.project-name {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.page-list { padding-bottom: 4px; }

.page-loading {
  padding: 6px 16px 6px 36px;
  font-size: 12px;
  color: #6b7399;
}

.page-row {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 16px 7px 32px;
  background: none;
  border: none;
  color: #8890b0;
  font-size: 12.5px;
  cursor: pointer;
  text-align: left;
  transition: background 0.15s, color 0.15s;
}
.page-row:hover  { background: #272d48; color: #e8eaf6; }
.page-row.active { color: #9fa8da; font-weight: 600; background: #272d48; }

.page-dot { color: #4a5280; }

.slide-enter-active, .slide-leave-active {
  transition: max-height 0.2s ease, opacity 0.2s ease;
  overflow: hidden;
}
.slide-enter-from, .slide-leave-to { max-height: 0; opacity: 0; }
.slide-enter-to, .slide-leave-from { max-height: 300px; opacity: 1; }
</style>
