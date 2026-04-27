import { createApp } from 'vue'
import PrimeVue       from 'primevue/config'
import Aura           from '@primevue/themes/aura'
import 'primeicons/primeicons.css'

import Select          from 'primevue/select'
import Card            from 'primevue/card'
import DataTable       from 'primevue/datatable'
import Column          from 'primevue/column'
import ProgressSpinner from 'primevue/progressspinner'

import router from './router/index.js'
import App    from './App.vue'

const app = createApp(App)

app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: { darkModeSelector: false },
  },
})

// Global PrimeVue components — use as <p-select>, <p-card>, etc.
app.component('p-select',           Select)
app.component('p-card',             Card)
app.component('p-data-table',       DataTable)
app.component('p-column',           Column)
app.component('p-progress-spinner', ProgressSpinner)

app.use(router)
app.mount('#app')
