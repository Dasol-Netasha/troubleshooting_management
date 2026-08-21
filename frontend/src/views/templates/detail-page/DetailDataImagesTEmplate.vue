<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'

import logoBlue from '@/assets/images/logos/logo_blue.png'
import { useIssueDetailStore } from '@/stores/issueDetailStore'

const issueDetailStore = useIssueDetailStore()
const { images, loading } = storeToRefs(issueDetailStore)

const imageItems = computed(() => {
  return images.value.map((item) => ({
    imageId: item?.image_id,
    imagePath: logoBlue,
  }))
})
</script>

<template>
  <section class="space-y-2 rounded-xl border border-slate-200 bg-white p-4">
    <h3 class="text-sm font-semibold text-slate-800">이슈 이미지</h3>

    <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="image in imageItems"
        :key="image.imageId"
        class="overflow-hidden rounded-lg border border-slate-200 bg-white"
      >
        <img :src="image.imagePath" alt="Issue image" class="h-44 w-full object-contain bg-slate-50" />
        <p class="px-3 py-2 text-xs text-slate-500">image_id: {{ image.imageId }}</p>
      </div>
    </div>

    <p v-if="!loading && imageItems.length === 0" class="text-sm text-slate-500">등록된 이미지가 없습니다.</p>
  </section>
</template>
