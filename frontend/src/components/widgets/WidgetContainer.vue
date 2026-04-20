<template>
  <component
    :is="widgetComponent"
    :definition="definition"
    :data="data"
    :loading="loading"
    :error="error"
  />
</template>

<script setup>
import { computed } from 'vue'
import LineChartWidget from './LineChartWidget.vue'
import TableWidget     from './TableWidget.vue'
import { useWidgetData } from '../../composables/useWidgetData.js'

const props = defineProps({
  definition:  { type: Object, required: true },
  projectKey:  { type: String, required: true },
  pageId:      { type: String, required: true },
  filters:     { type: Object, default: () => ({}) },
})

// Refs needed by composable
import { toRef, ref } from 'vue'
const projectKeyRef = toRef(props, 'projectKey')
const defRef        = toRef(props, 'definition')
const pageIdRef     = toRef(props, 'pageId')
const filtersRef    = toRef(props, 'filters')

const { data, loading, error } = useWidgetData(projectKeyRef, defRef, pageIdRef, filtersRef)

const WIDGET_MAP = {
  line_chart: LineChartWidget,
  bar_chart:  LineChartWidget,   // reuse for now
  table:      TableWidget,
}

const widgetComponent = computed(() => WIDGET_MAP[props.definition.type] ?? TableWidget)
</script>
