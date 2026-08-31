<script setup>
import { useRouter } from 'vue-router'
import DetailDataTemplate from '@/views/templates/detail-page/DetailDataTemplate.vue'
import DetailDataImagesTEmplate from '@/views/templates/detail-page/DetailDataImagesTEmplate.vue'
import BackNavIconBtn from '@/components/molecules/buttons/BackNavIconBtn.vue'

const router = useRouter()

const goToList = () => {
  router.push('/list')
}
</script>

<template>
  <section class="space-y-4">
    <div class="flex items-center gap-2">
      <BackNavIconBtn @click="goToList" />
      <h1 class="text-2xl font-semibold text-slate-900">Detail Page</h1>
    </div>

    <DetailDataTemplate />
    <DetailDataImagesTEmplate />
  </section>
</template>