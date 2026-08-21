import { createRouter, createWebHistory } from 'vue-router'

import LoginPage from '@/views/pages/LoginPage.vue'
import ListPage from '@/views/pages/ListPage.vue'
import DetailPage from '@/views/pages/DetailPage.vue'
import UpdatePage from '@/views/pages/UpdatePage.vue'
import { useAuthStore } from '@/stores/authStore'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/list',
    },
    {
      path: '/login',
      name: 'login-page',
      component: LoginPage,
      meta: {
        title: '로그인',
        public: true,
        hideChrome: true,
      },
    },
    {
      path: '/list',
      name: 'list-page',
      component: ListPage,
      meta: {
        title: '목록',
      },
    },
    {
      path: '/detail/:issueId',
      name: 'detail-page',
      component: DetailPage,
      meta: {
        title: '상세',
      },
    },
    {
      path: '/update',
      name: 'update-page',
      component: UpdatePage,
      meta: {
        title: '수정',
      },
    },
    {
      path: '/main',
      redirect: '/list',
      meta: {
        public: true,
      },
    },
  ],
})

router.beforeEach((to) => {
  const authStore = useAuthStore()

  if (!to.meta.public && !authStore.isAuthenticated) {
    return { path: '/login' }
  }

  if (to.name === 'login-page' && authStore.isAuthenticated) {
    return { path: '/list' }
  }

  return true
})

export default router