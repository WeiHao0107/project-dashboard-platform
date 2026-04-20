import { createRouter, createWebHistory } from 'vue-router'
import IssueTrendPage        from '../pages/IssueTrendPage.vue'
import MemberPerformancePage from '../pages/MemberPerformancePage.vue'

// page-key → { name, component }
export const PAGE_DEFS = [
  { pageId: 'issue-trend',        name: 'issue-trend',        component: IssueTrendPage },
  { pageId: 'member-performance', name: 'member-performance', component: MemberPerformancePage },
]

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // Layout shell – sidebar lives here, content via <RouterView>
    {
      path: '/',
      component: () => import('../views/DashboardView.vue'),
      children: PAGE_DEFS.map(({ name, component }) => ({
        path: ':projectKey/' + name,
        name,
        component,
        props: true,          // passes projectKey as prop to page component
      })),
    },
    // Catch-all → root (sidebar will redirect to first project/page)
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

export default router
