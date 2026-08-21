<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goToDetail = () => {
  router.push('/detail')
}

const goToUpdate = () => {
  router.push('/update')
}
</script>

<template>
  <section class="space-y-6">
    <div>
      <h1 class="text-2xl font-semibold text-slate-900">List Page</h1>
      <p class="mt-2 text-sm text-slate-600">로그인 후 기본으로 진입하는 목록 페이지입니다.</p>
    </div>

    <div class="flex flex-wrap gap-3">
      <button
        type="button"
        class="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-700"
        @click="goToDetail"
      >
        DetailPage 이동
      </button>
      <button
        type="button"
        class="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-900 transition hover:bg-slate-100"
        @click="goToUpdate"
      >
        UpdatePage 이동
      </button>
    </div>
  </section>
</template>