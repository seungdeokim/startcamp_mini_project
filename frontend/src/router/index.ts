import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/board',
      name: 'board-list',
      component: () => import('@/views/BoardListView.vue'),
    },
    {
      path: '/board/write',
      name: 'board-write',
      component: () => import('@/views/BoardWriteView.vue'),
    },
    {
      path: '/board/:id',
      name: 'board-detail',
      component: () => import('@/views/BoardDetailView.vue'),
      props: true,
    },
    {
      path: '/board/:id/edit',
      name: 'board-edit',
      component: () => import('@/views/BoardWriteView.vue'),
      props: true,
    },
    {
      path: '/info',
      name: 'info',
      component: () => import('@/views/InfoView.vue'),
    },
    {
      path: '/map',
      name: 'map',
      component: () => import('@/views/MapView.vue'),
    },
  ],
})

export default router
