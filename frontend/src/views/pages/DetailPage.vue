<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goToList = () => {
  router.push('/list')
}
</script>

<template>
  <section class="space-y-4">
    <h1 class="text-2xl font-semibold text-slate-900">Detail Page</h1>
    <p class="text-sm text-slate-600">상세 정보를 표시하는 페이지입니다.</p>
    <button
      type="button"
      class="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-900 transition hover:bg-slate-100"
      @click="goToList"
    >
      ListPage로 돌아가기
    </button>
  </section>
</template>