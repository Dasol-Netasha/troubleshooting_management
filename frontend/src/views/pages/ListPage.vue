<script setup>
import { useRouter } from 'vue-router'

import FilterTemplate from '@/views/templates/list-page/FilterTemplate.vue'
import ListTableTemplate from '@/views/templates/list-page/ListTableTemplate.vue'

const router = useRouter()

const goToUpdate = () => {
  router.push('/update')
}
</script>

<template>
  <section class="space-y-4">
    <div class="flex items-center justify-end gap-2">
      <button
        type="button"
        class="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-900 transition hover:bg-slate-100"
        @click="goToUpdate"
      >
        UpdatePage 이동
      </button>
    </div>

    <FilterTemplate />
    <ListTableTemplate />
  </section>
</template>