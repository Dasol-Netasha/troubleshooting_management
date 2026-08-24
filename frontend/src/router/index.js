import { createRouter, createWebHistory } from 'vue-router'

import ListPage from '@/views/pages/ListPage.vue'
import DetailPage from '@/views/pages/DetailPage.vue'
import UpdatePage from '@/views/pages/UpdatePage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/list',
    },
    // TODO: 이후 로그인 처리 시 연결
    // {
    //   path: '/login',
    //   name: 'login-page',
    //   component: LoginPage,
    //   meta: {
    //     title: '로그인',
    //     public: true,
    //     hideChrome: true,
    //   },
    // },
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

// TODO: 로그인 기능 연결 시 이 가드를 다시 활성화
router.beforeEach(() => {
  return true
})

export default router